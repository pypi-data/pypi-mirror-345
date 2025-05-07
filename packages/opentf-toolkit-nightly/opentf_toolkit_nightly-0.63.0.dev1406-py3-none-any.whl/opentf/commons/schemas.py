# Copyright (c) 2023 Henix, Henix.fr
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

"""Helpers for the OpenTestFactory schemas and validation."""

from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import json
import logging
import os

from jsonschema import Draft201909Validator, ValidationError
from toposort import toposort, CircularDependencyError
from yaml import safe_load


import opentf.schemas


########################################################################
# Schemas

SERVICECONFIG = 'opentestfactory.org/v1beta2/ServiceConfig'
SSHSERVICECONFIG = 'opentestfactory.org/v1alpha2/SSHServiceConfig'
EVENTBUSCONFIG = 'opentestfactory.org/v1alpha1/EventBusConfig'
PROVIDERCONFIG = 'opentestfactory.org/v1beta1/ProviderConfig'

SUBSCRIPTION = 'opentestfactory.org/v1/Subscription'

WORKFLOW = 'opentestfactory.org/v1/Workflow'
WORKFLOWCANCELLATION = 'opentestfactory.org/v1/WorkflowCancellation'
WORKFLOWCOMPLETED = 'opentestfactory.org/v1/WorkflowCompleted'
WORKFLOWCANCELED = 'opentestfactory.org/v1/WorkflowCanceled'
WORKFLOWRESULT = 'opentestfactory.org/v1alpha1/WorkflowResult'

GENERATORCOMMAND = 'opentestfactory.org/v1alpha1/GeneratorCommand'
GENERATORRESULT = 'opentestfactory.org/v1/GeneratorResult'

PROVIDERCOMMAND = 'opentestfactory.org/v1/ProviderCommand'
PROVIDERRESULT = 'opentestfactory.org/v1/ProviderResult'

EXECUTIONCOMMAND = 'opentestfactory.org/v1/ExecutionCommand'
EXECUTIONRESULT = 'opentestfactory.org/v1alpha1/ExecutionResult'
EXECUTIONERROR = 'opentestfactory.org/v1alpha1/ExecutionError'

AGENTREGISTRATION = 'opentestfactory.org/v1alpha1/AgentRegistration'

NOTIFICATION = 'opentestfactory.org/v1alpha1/Notification'

ALLURE_COLLECTOR_OUTPUT = 'opentestfactory.org/v1alpha1/AllureCollectorOutput'

CHANNEL_HOOKS = 'opentestfactory.org/v1alpha1/ChannelHandlerHooks'

QUALITY_GATE = 'opentestfactory.org/v1alpha1/QualityGate'
RETENTION_POLICY = 'opentestfactory.org/v1alpha1/RetentionPolicy'
TRACKER_PUBLISHER = 'opentestfactory.org/v1alpha1/TrackerPublisher'
INSIGHT_COLLECTOR = 'opentestfactory.org/v1alpha1/InsightCollector'

PLUGIN_DESCRIPTOR = 'config.opentestfactory.org/v1/Descriptor'


########################################################################
# JSON Schema Helpers

_schemas: Dict[str, Dict[str, Any]] = {}
_validators: Dict[str, Draft201909Validator] = {}

SCHEMAS_ROOT_DIRECTORY = list(opentf.schemas.__path__)[0]


def get_schema(name: str) -> Dict[str, Any]:
    """Get specified schema.

    # Required parameters

    - name: a string, the schema name (its kind)

    # Returned value

    A _schema_.  A schema is a dictionary.

    # Raised exceptions

    If an error occurs while reading the schema, the initial exception
    is logged and raised again.
    """
    if name not in _schemas:
        try:
            with open(
                os.path.join(SCHEMAS_ROOT_DIRECTORY, f'{name}.json'),
                'r',
                encoding='utf-8',
            ) as schema:
                _schemas[name] = json.loads(schema.read())
        except Exception as err:
            logging.error('Could not read schema "%s": %s', name, err)
            raise
    return _schemas[name]


def _validator(schema: str) -> Draft201909Validator:
    if schema not in _validators:
        _validators[schema] = Draft201909Validator(get_schema(schema))
    return _validators[schema]


def validate_schema(
    schema: str, instance: Dict[str, Any]
) -> Tuple[bool, Optional[str]]:
    """Return (True, None) if instance validates schema.

    # Required parameters

    - schema: a string, the schema name (its kind)
    - instance: a dictionary

    # Returned value

    A (bool, Optional[str]) pair.  If `instance` is a valid instance of
    `schema`, returns `(True, None)`.  If not, returns `(False, error)`.
    """
    try:
        _validator(schema).validate(instance=instance)
    except ValidationError as err:
        return False, str(err)
    return True, None


def read_and_validate(schema: str, filename: str) -> Dict[str, Any]:
    """Read and validate a JSON or YAML file.

    # Required parameters

    - schema: a string, the schema name (its kind)
    - filename: a string, the file name

    # Returned value

    A dictionary, the valid content.

    # Raised exceptions

    An _OSError_ exception is raised if the file cannot be read.

    A _ValueError_ exception is raised if the JSON or YAML file is
    invalid.
    """
    with open(filename, 'r', encoding='utf-8') as cnf:
        config = safe_load(cnf)

    if not isinstance(config, dict):
        raise ValueError('File is not a JSON object.')
    valid, extra = validate_schema(schema or SERVICECONFIG, config)
    if not valid:
        raise ValueError(f'Invalid content: {extra}.')
    return config


########################################################################
# Pipelines Helpers


def validate_pipeline(
    workflow: Dict[str, Any],
) -> Tuple[bool, Union[str, List[List[str]]]]:
    """Validate workflow jobs, looking for circular dependencies.

    # Required parameters

    - workflow: a dictionary

    # Returned value

    A (`bool`, extra) pair.

    If there is a dependency on an non-existing job, returns
    `(False, description (a string))`.

    If there are circular dependencies in the workflow jobs, returns
    `(False, description (a string))`.

    If there are no circular dependencies, returns `(True, jobs)` where
    `jobs` is an ordered list of job names lists.  Each item in the
    returned list is a set of jobs that can run in parallel.
    """
    jobs = {}
    for job_name, job_definition in workflow['jobs'].items():
        if needs := job_definition.get('needs'):
            if isinstance(needs, list):
                jobs[job_name] = set(needs)
            else:
                jobs[job_name] = {needs}
        else:
            jobs[job_name] = set()
    for src, dependencies in jobs.items():
        for dep in dependencies:
            if dep not in jobs:
                return (
                    False,
                    f'Job "{src}" has a dependency on job "{dep}" which does not exist.',
                )
    try:
        return True, [list(items) for items in toposort(jobs)]
    except CircularDependencyError as err:
        return False, str(err)


def validate_workflow(workflow: Dict[str, Any]) -> List[List[str]]:
    """Validate workflow.

    # Required parameters

    - workflow: a dictionary

    # Returned value

    An ordered list of job names lists.  Each item in the returned list
    is a set of jobs that can run in parallel.

    # Raised exceptions

    A _ValueError_ exception is raised if the workflow is not a valid.
    """
    valid, extra = validate_schema(WORKFLOW, workflow)
    if not valid:
        raise ValueError(extra)

    if declaration := workflow.get('inputs'):
        try:
            _validate_defaults(declaration)
        except ValueError as err:
            raise ValueError(
                f'Invalid "inputs" section, default value for {err}'
            ) from None

    valid, extra = validate_pipeline(workflow)
    if not valid:
        raise ValueError(extra)

    return extra


# Inputs Helpers

INPUTSTYPE_VALIDATION = {'string': (str,), 'boolean': (bool,), 'number': (int, float)}


def _normalize_inputs(inputs: Dict[str, Any]) -> None:
    """Normalize inputs.

    The 'normalized' form for inputs is with `-` separators, not `_`.

    Non-normalized inputs are removed from the dictionary.

    # Raised exceptions

    A _ValueError_ exception is raised if an input is provided twice, in
    a normalized as well as a non-normalized form.
    """
    for key in inputs.copy():
        if '_' not in key:
            continue
        normalized = key.replace('_', '-')
        if normalized in inputs:
            raise ValueError(f'Both "{key}" and "{normalized}" specified in inputs.')
        inputs[normalized] = inputs.pop(key)


def _set_default(inputs: Dict[str, Any], key: str, spec: Dict[str, Any]) -> None:
    if (default := spec.get('default')) is not None:
        inputs[key] = default
    elif type_ := spec.get('type'):
        if type_ == 'string':
            inputs[key] = ''
        elif type_ == 'number':
            inputs[key] = 0
        elif type_ == 'boolean':
            inputs[key] = False


def validate_value(spec: Dict[str, Any], val: Any) -> Any:
    """Validate a value.

    # Required parameters

    - spec: a dictionary
    - val: the value to validate

    # Returned value

    The validated value, converted to the expected type if appropriate.

    # Raised exceptions

    A _ValueError_ exception is raised if the validation fails.
    """
    type_ = spec.get('type')

    if type_ == 'choice':
        if val in spec['options']:
            return val
        allowed = '", "'.join(sorted(spec['options']))
        raise ValueError(f'Invalid value "{val}".  Allowed values: "{allowed}".')

    if isinstance(val, INPUTSTYPE_VALIDATION.get(type_, object)):
        return val

    if type_ == 'boolean':
        if isinstance(val, str) and val.lower() in ('true', 'false'):
            return val.lower() == 'true'
        raise ValueError(f'Invalid value "{val}".  Allowed values: "true", "false".')
    if type_ == 'number':
        for cast in (int, float):
            try:
                return cast(val)
            except (ValueError, TypeError):
                pass
        raise ValueError(f'Invalid value "{val}".  Expected a number.')
    if type_ == 'string':
        return str(val)

    raise ValueError(f'Invalid value "{val}".  Expected a {type_}.')


def validate_inputs(
    declaration: Dict[str, Dict[str, Any]],
    inputs: Dict[str, Any],
    additional_inputs: bool = False,
    normalize: bool = True,
) -> None:
    """Validate inputs.

    Default values are filled in `inputs` as appropriate.

    Input names are normalized to use hyphens instead of underscores
    by default (declaration is expected to be normalized in this case).

    If `normalize` is set, non-normalized inputs are removed from the
    dictionary.

    If declaration contains a pattern (a key starting with '{'),
    normalization is ignored.

    Choices values are validated.

    Types are enforced if declared as `boolean`, `number`, or `string`.
    Conversion is performed if needed.

    # Required parameters

    - declaration: a dictionary
    - inputs: a dictionary

    # Optional parameters

    - additional_inputs: a boolean (False by default)
    - normalize: a boolean (True by default)

    # Raised exceptions

    A _ValueError_ exception is raised if inputs do not match
    declaration.
    """
    if normalize and not any(key.startswith('{') for key in declaration):
        _normalize_inputs(inputs)

    for key, spec in declaration.items():
        if key.startswith('{'):
            continue
        if key not in inputs:
            if spec.get('required'):
                raise ValueError(f'Mandatory input "{key}" not provided.')
            _set_default(inputs, key, spec)
            continue
        try:
            inputs[key] = validate_value(spec, inputs[key])
        except ValueError as err:
            raise ValueError(f'Input "{key}": {err}') from None

    if additional_inputs:
        return

    if unexpected := set(inputs) - set(declaration):
        allowed = '", "'.join(sorted(declaration))
        unexpected = '", "'.join(sorted(unexpected))
        raise ValueError(
            f'Unexpected inputs "{unexpected}" found.  Allowed inputs: "{allowed}".'
        )


def _validate_defaults(declaration: Dict[str, Any]) -> None:
    """Validate defaults.

    Ensure `default`, if specified, is of the correct type and range.
    """
    for key, spec in declaration.items():
        type_ = spec.get('type')
        if not (type_ and 'default' in spec):
            continue
        default = spec['default']
        if expected := INPUTSTYPE_VALIDATION.get(type_):
            if not isinstance(default, expected):
                raise ValueError(f'"{key}" must be a {type_}, got {repr(default)}.')
            continue
        if type_ == 'choice' and default not in spec.get('options'):
            allowed = '", "'.join(sorted(spec.get('options')))
            raise ValueError(
                f'"{key}" must be one of "{allowed}", got {repr(default)}.'
            )


def validate_descriptors(descriptors: Iterable[Dict[str, Any]]) -> None:
    """Validate descriptors.

    Validate descriptors against PLUGIN_DESCRIPTOR schema for plugins.

    If applicable, `default` values are checked against the input's
    `type`.

    # Required parameters

    - descriptors: a series of manifests

    # Raised exceptions

    A _ValueError_ exception is raised if a descriptor is invalid.
    """
    for manifest in descriptors:
        try:
            metadata = manifest['metadata']
            what = f'{metadata["name"].lower()} {metadata.get("action", "")}'.strip()
        except Exception as err:
            raise ValueError(f'Missing "metadata.name" section: {err}.') from None
        valid, extra = validate_schema(PLUGIN_DESCRIPTOR, manifest)
        if not valid:
            raise ValueError(f'"{what}": {extra}')
        if declaration := manifest.get('inputs'):
            try:
                _validate_defaults(declaration)
            except ValueError as err:
                raise ValueError(
                    f'"inputs" section for "{what}", default value for {err}'
                ) from None
