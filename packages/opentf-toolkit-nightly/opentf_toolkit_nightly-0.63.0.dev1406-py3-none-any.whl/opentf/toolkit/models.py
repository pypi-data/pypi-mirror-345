# Copyright (c) 2025 Henix, Henix.fr
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

"""Handling models from plugins configuration files."""

from typing import Any

import os

from opentf.commons import read_and_validate
from opentf.toolkit import watch_file

Model = dict[str, Any]
Spec = dict[str, Any]

########################################################################

IMG_MODELS = []

########################################################################
### Configuration loader helpers


def deduplicate(
    plugin,
    models: list[Model],
) -> tuple[list[Model], set[str]]:
    """Deduplicate models in a list.

    # Required parameter

    - models: a list of dictionaries (models), in increasing priority order.

    # Returned value

    A tuple containing a list of deduplicated models and a possibly empty
    list of warnings.
    """
    seen = {}
    name, kind = None, None
    warnings = set()
    for model in reversed(models):
        key = (name, kind) = model.get('name'), model.get('kind')
        if key not in seen:
            seen[key] = model
        else:
            if model.get('.source') != 'default':
                msg = f'Duplicate definitions found for {plugin.name} {kind+' ' if kind else ''}"{name}", only the definition with the highest priority will be used.'
                warnings.add(msg)
    if warnings:
        for msg in warnings:
            plugin.logger.warning(msg)
    return list(reversed(list(seen.values()))), warnings


def filter_listdir(plugin, path: str, kinds: tuple[str, ...]) -> list[str]:
    """listdir-like, filtering for files with specified extensions."""
    files = [
        f
        for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f)) and f.endswith(kinds)
    ]
    if not files:
        plugin.logger.debug('No %s files provided in %s.', ', '.join(kinds), path)
    return sorted(files)


def _read_models(
    plugin, schema: str, configfile: str, config_key: str
) -> list[Model] | None:
    """Read plugin models JSON or YAML and return models list."""
    try:
        models = read_and_validate(schema, configfile)
    except ValueError as err:
        plugin.logger.error(
            'Invalid %s definition file "%s": %s.  Ignoring.',
            plugin.name,
            configfile,
            str(err),
        )
        return None

    return models[config_key]


def _load_image_models(
    plugin, config_path: str, config_key: str, schema: str, default_models: list[Model]
) -> list[dict[str, Any]]:
    """Load models from `CONFIG_PATH` directory.

    Storing models and possible warnings in plugin.config['CONFIG'].
    """
    models = default_models
    for config_file in filter_listdir(plugin, config_path, ('.yaml', '.yml')):
        filepath = os.path.join(config_path, config_file)
        try:
            if not (img_models := _read_models(plugin, schema, filepath, config_key)):
                continue
            plugin.logger.debug(
                'Loading %s models from file "%s".', plugin.name, config_file
            )
            models.extend(img_models)
        except Exception as err:
            raise ValueError(
                f'Failed to load {plugin.name} models from file "{config_file}": {str(err)}.'
            )
    models, warnings = deduplicate(plugin, models)
    plugin.config['CONFIG'][config_key] = models
    plugin.config['CONFIG']['warnings'] = warnings
    return models


def _refresh_configuration(
    _, configfile: str, schema: str, plugin, config_key: str
) -> None:
    """Read plugin models from environment variable specified file.

    Storing models in .config['CONFIG'], using the following entries:

    - {config_key}: a list of models
    - warnings: a list of duplicate models warnings
    """
    try:
        config = plugin.config['CONFIG']
        models = IMG_MODELS.copy()
        plugin.logger.info(
            f'Reading {plugin.name} models definition from {configfile}.'
        )
        env_models = _read_models(plugin, schema, configfile, config_key) or []
        models.extend(env_models)
        config[config_key], config['warnings'] = deduplicate(plugin, models)
    except Exception as err:
        plugin.logger.error(
            'Error while reading %s "%s" definition: %s.',
            plugin.name,
            configfile,
            str(err),
        )


########################################################################
### Configuration loader


def load_and_watch_models(
    plugin,
    config_path: str,
    config_key: str,
    schema: str,
    default_models: list[Model],
    env_var: str,
) -> None:
    """Load plugin configuration models.

    Plugin configuration models are loaded from configuration files path
    and filepath specified by the environment variable. File specified by the
    environment variable is watched for modifications. Models list is stored
    in `plugin.config['CONFIG'][{config_key}]` entry.

    # Required parameters

    - plugin: a Flask plugin
    - config_path: a string, configuration models path, should be a directory
    - config_key: a string, plugin configuration key name
    - schema: a string, plugin models validation schema
    - default_models: a list of plugin-specific default models
    - env_var: a string, environment variable name

    # Raised exception

    ValueError is raised if configuration files path is not found or
    is not a directory.
    """
    if not os.path.isdir(config_path):
        raise ValueError(
            f'Configuration files path "{config_path}" not found or not a directory.'
        )

    IMG_MODELS.extend(
        _load_image_models(plugin, config_path, config_key, schema, default_models)
    )

    if os.environ.get(env_var):
        watch_file(
            plugin,
            os.environ[env_var],
            _refresh_configuration,
            schema,
            plugin,
            config_key,
        )

    plugin.logger.info(
        'Loading default %s definitions and definitions from "%s".',
        plugin.name,
        config_path,
    )
