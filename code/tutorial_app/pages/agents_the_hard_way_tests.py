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

from live_labs.editor import send_keys
from live_labs.testing import isolate

NAME = "agents_the_hard_way"
EDITOR_DIR = Path("/project/code").joinpath(NAME)
PYTHON_EXE = "/usr/bin/python"

# TODO test if the openai module is in single_agent.__dict__


def prep_imports_and_api_key() -> str:
    """Prepare the imports and api key."""
    return send_keys(
        r'''
        """An example agent built from scratch."""

        import json
        import os

        from cachier import cachier
        from openai import OpenAI

        API_KEY = os.environ.get("NVIDIA_API_KEY", "")
        MODEL_URL = "https://integrate.api.nvidia.com/v1"
        MODEL_NAME = "meta/llama-3.3-70b-instruct"


        '''
    )


# dir(dir of the running code)/python exe to use(import langgraph...)
@isolate(EDITOR_DIR, PYTHON_EXE)
def define_client():
    """define the client"""
    import single_agent  # pyright: ignore[reportMissingImports]
    from openai import OpenAI  # pyright: ignore[reportMissingImports]

    # intentionally same file name with answer
    if not hasattr(single_agent, "client"):
        print(":TestFail: info_no_client")
        return

    if not isinstance(single_agent.client, OpenAI):
        print(":TestFail: info_wrong_client_type")
        return


@isolate(EDITOR_DIR, PYTHON_EXE)
def define_adding_tool():
    """make sure its an add function"""
    import single_agent  # pyright: ignore[reportMissingImports]

    if not hasattr(single_agent, "add"):
        print(":TestFail: info_no_add")
        return

    if single_agent.add(7, 8) != 15:
        print(":TestFail: info_add_not_working")
        return


@isolate(EDITOR_DIR, PYTHON_EXE)
def define_tools_list():
    """make sure its a list"""
    import pprint

    import single_agent  # pyright: ignore[reportMissingImports]

    def strip_descriptions(d):
        """Recursively remove 'description' keys from a dictionary."""
        if isinstance(d, dict):
            return {k: strip_descriptions(v) for k, v in d.items() if k != "description"}
        elif isinstance(d, list):
            return [strip_descriptions(item) for item in d]
        else:
            return d

    tools_target = {
        "type": "function",
        "function": {
            "name": "add",
            "parameters": {
                "type": "object",
                "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                "required": ["a", "b"],
            },
        },
    }

    if not hasattr(single_agent, "tools"):
        print(":TestFail: info_no_tools")
        return

    if not isinstance(single_agent.tools, list):
        print(":TestFail: info_tools_not_list")
        return

    if len(single_agent.tools) != 1:
        print(":TestFail: info_tools_list_length")
        return

    if not isinstance(single_agent.tools[0], dict):
        print(":TestFail: info_tools_list_dict")
        return

    if strip_descriptions(single_agent.tools[0]) != tools_target:
        print(":TestFail: info_tools_list_content")
        return

    pprint.pprint(single_agent.tools)


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
