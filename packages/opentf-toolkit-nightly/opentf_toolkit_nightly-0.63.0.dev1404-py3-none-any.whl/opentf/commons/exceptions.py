# Copyright (c) 2024 Henix, Henix.fr
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

"""Helpers for the OpenTestFactory orchestrator exceptions.

```plaintext
OpentfError
|- ConfigError
|- ServiceError
|  |- AlreadyExistsError
|  |- BadRequestError
|  |- ConflictError
|  |- InvalidRequestError
|  |- NotFoundError
|  |- UnauthorizedError
|- ExecutionError
```
"""


class OpentfError(Exception):
    """Base orchestrator exceptions."""


class ConfigError(OpentfError):
    """Invalid configuration file."""


class ServiceError(OpentfError):
    """Base exception for request errors."""

    status_name = 'ServiceError'

    def __init__(self, msg, details=None):
        self.msg = msg
        self.details = details

    @property
    def http_status_name(self):
        return self.status_name


class AlreadyExistsError(ServiceError):
    """AlreadyExists exception."""

    status_name = 'AlreadyExists'


class BadRequestError(ServiceError):
    """BadRequest exception."""

    status_name = 'BadRequest'


class ConflictError(ServiceError):
    """Invalid exception."""

    status_name = 'Conflict'


class InvalidRequestError(ServiceError):
    """Invalid exception."""

    status_name = 'Invalid'


class NotFoundError(ServiceError):
    """NotFound exception."""

    status_name = 'NotFound'


class UnauthorizedError(ServiceError):
    """Invalid exception."""

    status_name = 'Unauthorized'


########################################################################
## Exception helpers


class ExecutionError(OpentfError):
    """An ExecutionError exception.

    Only expected to be raised in a workflow thread.  Will publish
    the corresponding ExecutionError event if in this context.
    """

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        return str(self.message)
