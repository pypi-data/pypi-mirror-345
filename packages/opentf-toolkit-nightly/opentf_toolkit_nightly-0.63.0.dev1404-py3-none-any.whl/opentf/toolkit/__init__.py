# Copyright (c) 2021 Henix, Henix.fr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A toolkit for creating OpenTestFactory plugins."""

from typing import Any, Callable, Dict, Optional

import os
import threading

from collections import defaultdict
from time import sleep

from flask import Flask, request, g

import yaml

from opentf.commons import (
    make_app,
    run_app,
    get_context_parameter,
    subscribe,
    unsubscribe,
    EXECUTIONCOMMAND,
    EXECUTIONRESULT,
    PROVIDERCOMMAND,
    PROVIDERCONFIG,
    GENERATORCOMMAND,
    SERVICECONFIG,
    CHANNEL_HOOKS,
    PLUGIN_DESCRIPTOR,
    make_dispatchqueue,
    make_status_response,
    validate_descriptors,
    validate_inputs,
    validate_schema,
)
from opentf.commons.meta import read_category_labels, maybe_set_category_labels
from opentf.toolkit import core


########################################################################

SUBSCRIPTION_KEY = '__subscription uuid__'
KIND_KEY = '__kind key__'
INPUTS_KEY = '__inputs key__'
OUTPUTS_KEY = '__outputs key__'
WATCHEDFILES_KEY = '__watched files__'
WATCHEDFILES_EVENT_KEY = '__watched files event__'
DISPATCHQUEUE_KEY = '__dispatch queue__'

WATCHDOG_POLLING_DELAY_SECONDS = 30
WATCHDOG_POLLING_DELAY_KEY = 'watchdog_polling_delay_seconds'
AVAILABILITY_CHECK_DELAY_SECONDS = 'availability_check_delay_seconds'

Handler = Callable[[Dict[str, Any]], Any]


########################################################################
# Helpers for provider plugins


def _one_and_only_one(*args) -> bool:
    """Check that one and only one argument is not None."""
    return len([arg for arg in args if arg is not None]) == 1


def _maybe_get_item(cache: Dict[Any, Any], labels: Dict[str, str]) -> Optional[Any]:
    """Get most relevant item from cache if it exists."""
    prefix, category, version = read_category_labels(labels)

    for keys in (
        (prefix, category, version),
        (None, category, version),
        (prefix, category, None),
        (None, category, None),
        (prefix, None, None),
    ):
        if (entry := cache.get(keys)) is not None:
            return entry

    return None


def _ensure_inputs_match(
    plugin: Flask, labels: Dict[str, str], inputs: Dict[str, Any]
) -> None:
    """Check inputs.

    Normalize inputs, fills missing optional inputs with their default
    values.

    If one of the inputs is a template (name starting with '{'), no
    normalization is performed.

    # Raised exceptions

    A _core.ExecutionError_ is raised if a required entry is missing,
    or if an unexpected entry is found.
    """
    cache = plugin.config['CONTEXT'][INPUTS_KEY]
    if (entry := _maybe_get_item(cache, labels)) is None:
        return

    declaration, additional_inputs = entry
    try:
        validate_inputs(declaration, inputs, additional_inputs)
    except ValueError as err:
        raise core.ExecutionError(str(err))


def _get_target(
    labels: Dict[str, str], providers: Dict[str, Handler]
) -> Optional[Handler]:
    """Find target for labels.

    - `prefix/category[@vn]` is more specific than `category[@vn]`
    - `category@vn` is more specific than `category`
    - `category[@vn]` is more specific than `prefix`

    # Required parameters

    - labels: a dictionary, the labels
    - providers: a dictionary, the providers

    # Returned value

    Finds the most specific provider.  Returns None if no provider
    matches.
    """
    prefix, category, version = read_category_labels(labels)

    for template in (f'{prefix}/{category}', category):
        if version:
            parts = version.split('.')
            while parts:
                function = f'{template}@{".".join(parts)}'
                if function in providers:
                    return providers[function]
                parts.pop()
        if template in providers:
            return providers[template]

    return None


INVALID_HOOKS_DEFINITION_TEMPLATE = {
    'name': 'invalid-external-hooks-definition',
    'events': [],
    'before': [
        {
            'run': 'echo ::error::Invalid hooks definition.  Hooks defined by {name}_{type_}_HOOKS are disabled.  Please contact your orchestrator administrator for more info.',
            'if': "runner.os == 'windows'",
        },
        {
            'run': 'echo "::error::Invalid hooks definition.  Hooks defined by {name}_{type_}_HOOKS are disabled.  Please contact your orchestrator administrator for more info."',
            'if': "runner.os != 'windows'",
        },
    ],
}


def _maybe_add_hook_watcher(plugin: Flask, schema: str) -> None:
    """Add hook watcher if needed.

    If the `{name}_{type}_HOOKS` environment variable is set, the plugin
    will watch the file and update its hooks accordingly.

    If the hooks definition is invalid, a default hook is defined
    instead, informing workflows of the issue.

    # Required parameters

    - plugin: a Flask object
    - schema: a string, the schema name
    """
    if plugin.config['CONTEXT'][KIND_KEY] == EXECUTIONCOMMAND:
        type_ = 'CHANNEL'
    else:
        type_ = 'PROVIDER'
    if env := os.environ.get(f'{plugin.name.upper()}_{type_}_HOOKS'):
        befores = INVALID_HOOKS_DEFINITION_TEMPLATE['before']
        events = INVALID_HOOKS_DEFINITION_TEMPLATE['events']
        befores[0]['run'] = befores[0]['run'].format(
            name=plugin.name.upper(), type_=type_
        )
        befores[1]['run'] = befores[1]['run'].format(
            name=plugin.name.upper(), type_=type_
        )
        if type_ == 'PROVIDER':
            events.append({'category': '_'})
        elif type_ == 'CHANNEL':
            events.append({'channel': 'setup'})
        watch_file(
            plugin,
            env,
            _read_hooks_definition,
            schema if type_ == 'PROVIDER' else CHANNEL_HOOKS,
            INVALID_HOOKS_DEFINITION_TEMPLATE,
        )


def _read_hooks_definition(
    plugin: Flask, hooksfile: str, schema: str, invalid: Dict[str, Any]
) -> None:
    """Read hooks definition file.

    Try to read hooks definition file and set or replace existing hooks
    with those of `hooksfile`.

    # Required parameters

    - plugin: a Flask object
    - hooksfile: a string, the hooks definition file
    - schema: a string, the schema name
    - invalid: a dictionary, a hook definition
    """
    config = plugin.config['CONFIG']
    try:
        with open(hooksfile, 'r', encoding='utf-8') as src:
            hooks = yaml.safe_load(src)
        if not isinstance(hooks, dict) or not 'hooks' in hooks:
            plugin.logger.error(
                'Hooks definition file "%s" needs a "hooks" entry, ignoring.', hooksfile
            )
            config['hooks'] = [invalid]
            return

        if config.get('hooks'):
            plugin.logger.info('Replacing hooks definition using "%s".', hooksfile)
        else:
            plugin.logger.info('Reading hooks definition from "%s".', hooksfile)

        config['hooks'] = hooks['hooks']
        valid, extra = validate_schema(schema, config)
        if valid:
            return

        plugin.logger.error(
            'Error while verifying "%s" hooks definition: %s.', hooksfile, extra
        )
    except Exception as err:
        plugin.logger.error(
            'Error while reading "%s" hooks definition: %s.', hooksfile, err
        )

    config['hooks'] = [invalid]


########################################################################
# Dispatchers


def _dispatch_providercommand(
    plugin: Flask, handler: Handler, body: Dict[str, Any]
) -> None:
    """Provider plugin dispatcher.

    `handler` is expected to return either a list of steps or raise a
    _core.ExecutionError_ exception.
    """
    try:
        labels = body['metadata'].get('labels', {})
        plugin.logger.debug(
            'Calling provider function %s (%s/%s@%s).',
            handler.__name__,
            *read_category_labels(labels, default='_'),
        )
        inputs: Dict[str, Any] = body['step'].get('with', {})
        _ensure_inputs_match(plugin, labels, inputs)
        outputs = _maybe_get_item(plugin.config['CONTEXT'][OUTPUTS_KEY], labels)
        core.publish_providerresult(handler(inputs), outputs)
    except core.ExecutionError as err:
        core.publish_error(str(err))
    except Exception as err:
        core.publish_error(f'Unexpected execution error: {err}.')


def _dispatch_executioncommand(_, handler: Handler, body: Dict[str, Any]) -> None:
    """Channel plugin dispatcher."""
    try:
        handler(body)
    except Exception as err:
        core.publish_error(f'Unexpected execution error: {err}.')


def _dispatch_generatorcommand(
    plugin: Flask, handler: Handler, body: Dict[str, Any]
) -> None:
    """Generator plugin dispatcher."""
    try:
        labels = body['metadata'].get('labels', {})
        plugin.logger.debug(
            'Calling generator %s (%s/%s@%s).',
            handler.__name__,
            *read_category_labels(labels, default='_'),
        )
        inputs: Dict[str, Any] = body.get('with', {})
        _ensure_inputs_match(plugin, labels, inputs)
        outputs = _maybe_get_item(plugin.config['CONTEXT'][OUTPUTS_KEY], labels)
        core.publish_generatorresult(handler(inputs), outputs)
    except core.ExecutionError as err:
        core.publish_error(str(err))
    except Exception as err:
        core.publish_error(f'Unexpected execution error: {err}.')


########################################################################
#  Watchdog


def _run_handlers(plugin: Flask, file, handlers) -> None:
    """Run file handlers."""
    for handler, args, kwargs in handlers:
        try:
            handler(plugin, file, *args, **kwargs)
        except Exception as err:
            plugin.logger.error(
                'Handler "%s" for file "%s" failed: %s.  Ignoring.', handler, file, err
            )


def _watchdog(plugin: Flask, polling_delay: int) -> None:
    """Watch changes and call handlers when appropriate."""
    files_stat = defaultdict(float)
    files_handlers = plugin.config[WATCHEDFILES_KEY]
    first = True
    while True:
        for file in list(files_handlers):
            try:
                current_modified_time = os.stat(file).st_mtime
            except OSError as err:
                plugin.logger.debug('Could not stat file "%s": %s.', file, err)
                current_modified_time = 0
            if current_modified_time == files_stat[file] and not first:
                continue
            if files_stat[file] != current_modified_time and not first:
                plugin.logger.debug('Watched file "%s" has changed.', file)
            files_stat[file] = current_modified_time
            _run_handlers(plugin, file, list(files_handlers[file]))
        first = False
        plugin.config[WATCHEDFILES_EVENT_KEY].wait(polling_delay)
        plugin.config[WATCHEDFILES_EVENT_KEY].clear()


def _start_watchdog(plugin: Flask) -> None:
    """Set up a watchdog that monitors specified files for changes."""
    polling_delay = max(
        WATCHDOG_POLLING_DELAY_SECONDS,
        get_context_parameter(plugin, WATCHDOG_POLLING_DELAY_KEY),
    )

    plugin.logger.debug('Starting configuration watchdog thread.')
    threading.Thread(
        target=_watchdog, args=(plugin, polling_delay), daemon=True
    ).start()


def watch_file(plugin: Flask, path: str, handler, *args, **kwargs) -> None:
    """Watch file changes.

    There can be more than one handler watching a given file.  A handler
    is a function taking at least two parameters: a `plugin` object and
    a file path (a string).  It may take additional parameters.  It will
    be called whenever the file changes.

    The watchdog polls every 30 seconds by default.  This can be
    adjusted by setting the `watchdog_polling_delay_seconds` context
    parameter (but it cannot be more frequent).

    # Required parameters

    - plugin: a Flask application
    - path: a string, the file path
    - handler: a function

    # Optional parameters

    - *args: an array
    - **kwargs: a dictionary

    The provided extra parameters, if any, are passed to the handler
    whenever it is called.
    """
    need_init = plugin.config.get(WATCHEDFILES_KEY) is None
    if need_init:
        plugin.config[WATCHEDFILES_KEY] = defaultdict(list)
        plugin.config[WATCHEDFILES_EVENT_KEY] = threading.Event()
    plugin.logger.debug('Adding configuration watcher for "%s".', path)
    plugin.config[WATCHEDFILES_KEY][path].append((handler, args, kwargs))
    if need_init:
        _start_watchdog(plugin)
    else:
        plugin.config[WATCHEDFILES_EVENT_KEY].set()


def _watchnotifier(
    plugin: Flask,
    polling_delay: int,
    check: Callable[..., bool],
    items,
    notify: Callable[[], None],
):
    reference = {}
    while True:
        sleep(polling_delay)
        try:
            statuses = {item: check(item) for item in list(items)}
            if statuses != reference:
                notify()
                reference = statuses
        except Exception as err:
            plugin.logger.debug(
                f'Unexpected exception in watchnotifier, ignoring... {err}'
            )


def watch_and_notify(
    plugin: Flask, status: Callable[..., Any], items, notify: Callable[[], None]
) -> None:
    """Watch statuses changes in items.

    Check item status change at regular interval, call notify if
    changes detected.

    # Required parameters

    - plugin: a Flask application
    - status: a function taking an item and returning a value
    - items: an iterable
    - notify: a function of no arguments
    """
    polling_delay = get_context_parameter(plugin, AVAILABILITY_CHECK_DELAY_SECONDS)

    plugin.logger.debug('Starting watch notifier thread.')
    threading.Thread(
        target=_watchnotifier,
        args=(plugin, polling_delay, status, items, notify),
        daemon=True,
    ).start()


def _subscribe(
    plugin: Flask,
    cat_prefix: Optional[str],
    cat: Optional[str],
    cat_version: Optional[str],
    manifest: Dict[str, Any],
) -> str:
    """Subscribe for the relevant event."""
    context = plugin.config['CONTEXT']
    kind = context[KIND_KEY]
    labels = {}
    maybe_set_category_labels(labels, cat_prefix, cat, cat_version)
    context[INPUTS_KEY][(cat_prefix, cat, cat_version)] = (
        manifest.get('inputs', {}),
        manifest.get('additionalInputs'),
    )
    context[OUTPUTS_KEY][(cat_prefix, cat, cat_version)] = {
        k: v['value'] if isinstance(v, dict) else v
        for k, v in manifest.get('outputs', {}).items()
    }
    return subscribe(kind=kind, target='inbox', app=plugin, labels=labels)


def run_plugin(plugin: Flask) -> None:
    """Start and run plugin.

    Subscribe to the relevant events before startup and tries to
    unsubscribe in case of errors.

    Spurious subscriptions may remain in case of brutal termination.
    """
    try:
        context = plugin.config['CONTEXT']
        context[SUBSCRIPTION_KEY] = []
        context[INPUTS_KEY] = {}
        context[OUTPUTS_KEY] = {}
        if context[KIND_KEY] in (PROVIDERCOMMAND, GENERATORCOMMAND):
            for manifest in plugin.config['DESCRIPTOR']:
                metadata = manifest.get('metadata', {})
                if metadata.get('name', '').lower() != plugin.name.lower():
                    continue
                if 'action' not in metadata:
                    continue
                for event in manifest.get('events', []):
                    cat_prefix = event.get('categoryPrefix')
                    cat = event.get('category')
                    if cat or cat_prefix:
                        cat_version = event.get('categoryVersion')
                        context[SUBSCRIPTION_KEY].append(
                            _subscribe(plugin, cat_prefix, cat, cat_version, manifest)
                        )
                    else:
                        plugin.logger.warning(
                            'At least one of "category", "categoryPrefix" required, ignoring.'
                        )
        elif context[KIND_KEY] == EXECUTIONCOMMAND:
            context[SUBSCRIPTION_KEY].append(
                subscribe(kind=EXECUTIONCOMMAND, target='inbox', app=plugin)
            )
        run_app(plugin)
    finally:
        for subscription_id in plugin.config['CONTEXT'][SUBSCRIPTION_KEY]:
            unsubscribe(subscription_id, app=plugin)


def make_plugin(
    name: str,
    description: str,
    channel: Optional[Handler] = None,
    generator: Optional[Handler] = None,
    provider: Optional[Handler] = None,
    providers: Optional[Dict[str, Handler]] = None,
    publisher: Optional[Handler] = None,
    descriptor=None,
    schema=None,
    configfile=None,
    args: Optional[Any] = None,
) -> Flask:
    """Create and return a new plugin service.

    One and only one of `channel`, `generator`, `provider`, `providers`,
    or `publisher` must be specified.

    If no `descriptor` is specified, there must be `plugin.yaml` file in
    the same directory as the caller source file.  If none is found the
    execution stops.

    - Create default config
    - Subscribe to eventbus
    - Add publication handler
    - Create service (not started)

    Some 'optional' parameters are required for some plugin types:

    `args` is required for channel handlers.  It must be a list of one
    element that implements the `__contains__` protocol.

    # Required parameters

    - name: a string
    - description: a string
    - `channel`, `generator`, `provider`, `providers`, or `publisher`: a
      function
    - providers: a dictionary

    # Optional parameters

    - descriptor: a dictionary or a list of dictionaries or None (None
      by default)
    - schema: a string or None (None by default)
    - configfile: a string or None (None by default)
    - args: a list or None (None by default)

    # Returned value

    A plugin service (not started).

    # Raised exceptions

    A _ValueError_ exception is raised if the provided parameters are
    invalid.
    """

    def process_inbox():
        try:
            body = request.get_json() or {}
        except Exception as err:
            return make_status_response('BadRequest', f'Could not parse body: {err}.')

        if channel:
            try:
                channel_id = body['metadata'].get('channel_id')
                if channel_id and channel_id not in args[0]:
                    return make_status_response(
                        'OK', 'Job not handled by this channel plugin.'
                    )
            except KeyError:
                return make_status_response(
                    'BadRequest',
                    f'Not a valid {kind} request: Missing "metadata" section',
                )

        valid, extra = validate_schema(kind, body)
        if not valid:
            return make_status_response(
                'BadRequest', f'Not a valid {kind} request: {extra}.'
            )

        if workflow_id := body.get('metadata', {}).get('workflow_id'):
            g.workflow_id = workflow_id

        if providers:
            labels = body['metadata']['labels']

            if target := _get_target(labels=labels, providers=providers):
                _dispatch_providercommand(plugin, target, body)
            else:
                plugin.logger.warning('Labels %s not handled by %s.', str(labels), name)
        elif provider:
            _dispatch_providercommand(plugin, provider, body)
        elif channel:
            _dispatch_executioncommand(plugin, channel, body)
        elif generator:
            _dispatch_generatorcommand(plugin, generator, body)
        else:
            return make_status_response('BadRequest', 'Not implemented yet.')

        return make_status_response('OK', '')

    if not _one_and_only_one(channel, generator, provider, providers, publisher):
        raise ValueError(
            'One and only one of "channel", "generator", "provider", "providers", or "publisher" is required.'
        )
    if not (descriptor is None or isinstance(descriptor, (dict, list))):
        raise ValueError(
            '"descriptor", if specified, must be a dictionary or a list of dictionaries.'
        )
    if channel and (not isinstance(args, list) or len(args) != 1):
        raise ValueError(
            '"args" is required for channel plugins and must be a list of one element.'
        )

    if not schema:
        schema = SERVICECONFIG if generator else PROVIDERCONFIG

    plugin = make_app(
        name,
        description,
        configfile=configfile,
        schema=schema,
        descriptor=descriptor if descriptor is not None else 'plugin.yaml',
    )

    if channel:
        kind = EXECUTIONCOMMAND
    elif generator:
        kind = GENERATORCOMMAND
    elif publisher:
        kind = EXECUTIONRESULT
    else:
        kind = PROVIDERCOMMAND

    plugin.config['CONTEXT'][KIND_KEY] = kind
    plugin.route('/inbox', methods=['POST'])(process_inbox)

    if kind == PROVIDERCOMMAND:
        _maybe_add_hook_watcher(plugin, schema)
        plugin.config[DISPATCHQUEUE_KEY] = make_dispatchqueue(plugin)
    elif kind == GENERATORCOMMAND:
        plugin.config[DISPATCHQUEUE_KEY] = make_dispatchqueue(plugin)
    elif kind == EXECUTIONCOMMAND:
        _maybe_add_hook_watcher(plugin, CHANNEL_HOOKS)
        plugin.config[DISPATCHQUEUE_KEY] = make_dispatchqueue(plugin)

    core.register_defaultplugin(plugin)

    return plugin
