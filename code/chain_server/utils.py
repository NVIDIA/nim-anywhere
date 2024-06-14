# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utility functions that help with operating the chain."""

from typing import TypeVar

__empty__ = object()
_ItemT = TypeVar("_ItemT")


# pylint: disable-next=invalid-name # this mirrors the built in name
class itemgetter:
    """Modified version of the built in itemgetter to allow for default values.

    This is useful as sometimes the itemgetters will raise exceptions that mask
    more informative exceptions.

    The builtin itemgetter is typed as final and shouldn't be subclassed.
    """

    __slots__ = ("_default", "_item")

    def __init__(self, item: str, default: _ItemT = __empty__) -> None:
        """Initialize this class."""
        self._item = item
        self._default = default

    def __call__(self, obj: dict[str, _ItemT]) -> _ItemT:
        """Call the itemgetter."""
        try:
            return obj[self._item]
        except KeyError as exc:
            if self._default is not __empty__:
                return self._default
            raise exc

    def __repr__(self) -> str:
        """Return a string representation of self."""
        return f"{self.__class__.__module__}.{self.__class__.__name__}({self._item},{self._default})"
