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
"""Custom filters for Jinja parsing."""

import ast
import json
from typing import Any

from jinja2 import BaseLoader, Environment


def from_json(value: str) -> Any:
    """Convert a JSON string to an object."""
    return json.loads(str(value))


def eval(value: str) -> Any:
    """Parse the string and return the value."""
    return ast.literal_eval(value)


ENVIRONMENT = Environment(loader=BaseLoader())
ENVIRONMENT.filters["from_json"] = from_json
ENVIRONMENT.filters["eval"] = eval
