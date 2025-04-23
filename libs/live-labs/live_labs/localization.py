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

"""Live Labs Localization

This module is abstractions around retrieving message catalogs in the correct language.

The MessageCatalog data model represents the localized messages for a particular lab.

## Example
```python
MESSAGES = live_labs.MessageCatalog.from_page(__file__)
```
"""

from pathlib import Path
from typing import Any, Callable, cast

import streamlit as st
from pydantic import BaseModel, ConfigDict, Field
from pydantic_yaml import parse_yaml_raw_as

DEFAULT_LOCALE = "en_US"


class Task(BaseModel):
    """Representation of a single task."""

    name: str
    msg: str
    response: None | str = None
    test: None | str = None

    def get_test(self, tests: Any) -> None | Callable[[], str]:
        """Find a test for this task."""
        if self.name and self.test and tests:
            out = cast(Callable[[], str], getattr(tests, self.test, None))
            return out
        return None


class MessageCatalog(BaseModel):
    """Representation of a localization catalog files."""

    __pydantic_extra__: dict[str, None | str | list[Task]] = Field(init=False)  # type: ignore
    model_config = ConfigDict(extra="allow")

    tasks: list[Task] = []

    @classmethod
    def from_yaml(cls, path: Path) -> "MessageCatalog":
        """Load the message catalog data from yaml."""
        with open(path, "r", encoding="UTF-8") as ptr:
            yml = ptr.read()

        return parse_yaml_raw_as(cls, yml)

    @classmethod
    def from_page(cls, page_path: Path | str) -> "MessageCatalog":
        """Load the message catalog data from the file path to the associate page."""
        if isinstance(page_path, str):
            page_path = Path(page_path)

        locale_code = (st.context.locale or DEFAULT_LOCALE).replace("-", "_")

        for lang in [locale_code, DEFAULT_LOCALE]:
            catalog_path = page_path.with_suffix(f".{lang}.yaml")
            if catalog_path.is_file():
                return cls.from_yaml(catalog_path)
        return cls()

    def get(self, key: str, default_value: Any = None) -> Any:
        """Get a value from this class."""
        try:
            return getattr(self, key)
        except AttributeError:
            return default_value
