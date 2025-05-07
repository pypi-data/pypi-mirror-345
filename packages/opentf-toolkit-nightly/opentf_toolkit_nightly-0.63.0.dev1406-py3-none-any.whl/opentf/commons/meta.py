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

"""Toolkit metadata helpers."""

from typing import Dict, Iterable, Optional, Tuple


########################################################################
## Constants

CATEGORY_LABEL = 'opentestfactory.org/category'
CATEGORYPREFIX_LABEL = 'opentestfactory.org/categoryPrefix'
CATEGORYVERSION_LABEL = 'opentestfactory.org/categoryVersion'


########################################################################


def set_category_labels(labels: Dict[str, str], category: str) -> None:
    """Set category labels.

    `labels` is updated.

    # Required parameters

    - labels: a dictionary of labels, possibly empty
    - category: a string
    """
    category_prefix = category_version = '_'
    if '/' in category:
        category_prefix, category = category.split('/')
    if '@' in category:
        category, category_version = category.split('@')
    labels[CATEGORY_LABEL] = category
    labels[CATEGORYPREFIX_LABEL] = category_prefix
    labels[CATEGORYVERSION_LABEL] = category_version


def maybe_set_category_labels(
    labels: Dict[str, str],
    prefix: Optional[str],
    cat: Optional[str],
    version: Optional[str],
) -> None:
    """Set category labels if not None.

    `labels` is updated if at least one parameter is not None.
    """
    if cat is not None:
        labels[CATEGORY_LABEL] = cat
    if prefix is not None:
        labels[CATEGORYPREFIX_LABEL] = prefix
    if version is not None:
        labels[CATEGORYVERSION_LABEL] = version


def read_category_labels(
    labels: Dict[str, str], default: Optional[str] = None
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Get categorty items from labels."""
    prefix = labels.get(CATEGORYPREFIX_LABEL, default)
    category = labels.get(CATEGORY_LABEL, default)
    version = labels.get(CATEGORYVERSION_LABEL, default) or None
    return prefix, category, version


def event_match(labels: Dict[str, str], event: Dict[str, str]) -> bool:
    """Return True if event matches labels."""

    def _match(what: str) -> bool:
        return event[what] in ('_', labels.get(f'opentestfactory.org/{what}'))

    if not ('category' in event or 'categoryPrefix' in event):
        return False
    if 'category' in event and 'categoryPrefix' in event:
        match = _match('category') and _match('categoryPrefix')
    elif 'category' in event:
        match = _match('category')
    else:
        match = _match('categoryPrefix')
    if match and 'categoryVersion' in event:
        match = _match('categoryVersion')
    return match


def match_any(labels: Dict[str, str], events: Iterable[Dict[str, str]]) -> bool:
    """Check if any event matches category labels."""
    return any(event_match(labels, event) for event in events)
