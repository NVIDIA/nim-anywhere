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
"""Tests for auto continuing associated tasks."""

import sys
from pathlib import Path

from live_labs.testing import TestFail, isolate

NAME = "editor_test"
EDITOR_DIR = Path("/project/code").joinpath(NAME)


def sample_test():
    """Test a project using built in helpers."""
    # The testing module contains some test compatible helpers.
    # These helpers can either get an object or ensure the state of an object.
    # If there is an error in these helpers, they will raise TestFail automatically.
    raise TestFail("info_test_test")


@isolate(EDITOR_DIR)
def test_my_string():
    """Wait for my_string to be ready."""
    import file1  # pyright: ignore[reportMissingImports]

    print("Looking for my_string.")

    if not hasattr(file1, "my_string"):
        print(":TestFail: info_no_my_string")
        return

    print("Looking for five.")

    if file1.my_string != "five":
        print(":TestFail: info_my_string_not_five")
        return

    print("Looks good!")


if __name__ == "__main__":
    sys.stdout.write("---------------\n")
    # you can use this space for testing while you are
    # developing your tests
    test_my_string()
