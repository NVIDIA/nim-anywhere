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

import shutil
from pathlib import Path

from live_labs.editor import send_keys
from live_labs.testing import isolate

NAME = "agents_the_hard_way"
ANSWER_DIR = Path(__file__).parent.parent.joinpath("answers", NAME)
EDITOR_DIR = Path("/project/code").joinpath(NAME)
PYTHON_EXE = "/usr/bin/python"


## Setup the environment
def prep_imports() -> None:
    """Prepare the imports and api key."""
    cache_answer = ANSWER_DIR.joinpath("caching.py")
    cache_lib = EDITOR_DIR.joinpath("caching.py")
    shutil.copy(cache_answer, cache_lib)

    send_keys(
        r'''
        """An example agent built from scratch."""

        import json
        import os

        from caching import call_llm_cached
        from openai import OpenAI
        '''
    )


## Load the configuration
def prep_api_key() -> None:
    """Prepare the imports and api key."""
    send_keys(
        r"""

        API_KEY = os.environ.get("NGC_API_KEY", "---")
        MODEL_URL = "https://integrate.api.nvidia.com/v1"
        MODEL_NAME = "meta/llama-3.3-70b-instruct"
        """
    )


## Part 1 - The Model
def prep_define_client() -> None:
    """Add some comments."""
    send_keys(
        r"""


        # Connect to the model server
        """
    )


@isolate(EDITOR_DIR, PYTHON_EXE)
def test_define_client():
    """define the client"""
    import caching  # pyright: ignore[reportMissingImports]
    import openai  # pyright: ignore[reportMissingImports]
    import single_agent  # pyright: ignore[reportMissingImports]

    MODEL_NAME = "meta/llama-3.3-70b-instruct"

    # look for the value
    if not hasattr(single_agent, "client"):
        print(":TestFail: info_no_client")
        return

    # ensure the correct type
    if not isinstance(single_agent.client, openai.OpenAI):
        print(":TestFail: info_wrong_client_type")
        return

    # ensure it works
    messages = [{"role": "user", "content": "Hello!"}]
    try:
        _ = caching.call_llm_cached(single_agent.client, MODEL_NAME, messages)
    except openai.BadRequestError:
        print(":TestFail: info_client_bad_request")
    except openai.AuthenticationError:
        print(":TestFail: info_client_bad_auth")
    except openai.NotFoundError:
        print(":TestFail: info_test_bad_url")


## Part 2 - Tools
def prep_adding_tool() -> None:
    """Add some comments."""
    send_keys(
        r"""


        # Create a tool for your agents
        """
    )


@isolate(EDITOR_DIR, PYTHON_EXE)
def test_adding_tool():
    """make sure its an add function"""
    import inspect

    import single_agent  # pyright: ignore[reportMissingImports]s

    if not hasattr(single_agent, "add"):
        print(":TestFail: info_no_add")
        return

    if not callable(single_agent.add):
        print(":TestFail: info_add_not_fun")

    signature = inspect.signature(single_agent.add)
    args = list(signature.parameters.keys())
    if args != ["a", "b"]:
        print(":TestFail: info_bad_add_args")

    if single_agent.add(7, 8) != 7 + 8:
        print(":TestFail: info_add_not_working")
        return


## TODO
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


@isolate(EDITOR_DIR, PYTHON_EXE)
def payload_tool_selection():
    """Wait for my_string to be ready."""
    import json

    import single_agent  # pyright: ignore[reportMissingImports]

    if not hasattr(single_agent, "response"):
        print(":TestFail: info_no_response")
        return

    tool_call = single_agent.response.choices[0].message.tool_calls[0]
    if json.loads(tool_call.function.arguments) != {"a": 3, "b": 12}:
        print(":TestFail: info_parameters_not_correct")
        return

    print("Looks good!")
    # TODO: response formatt bug


@isolate(EDITOR_DIR, PYTHON_EXE)
def execute_tool():
    """execute the tool"""
    import single_agent  # pyright: ignore[reportMissingImports]

    if not hasattr(single_agent, "tool_call"):
        print(":TestFail: info_no_tool_call")
        return
    # how to check if a conditional statement exists?


@isolate(EDITOR_DIR, PYTHON_EXE)
def create_message_list():
    """create a message list"""
    import single_agent  # pyright: ignore[reportMissingImports]

    if not hasattr(single_agent, "messages"):
        print(":TestFail: info_no_messages")
        return

    if single_agent.messages != [{"role": "user", "content": "What is 3 plus 12?"}]:
        # TODO: message is not complete
        print(":TestFail: info_messages_not_correct")
        return


@isolate(EDITOR_DIR, PYTHON_EXE)
def call_model_again():
    """call the model again"""
    import single_agent  # pyright: ignore[reportMissingImports]

    if not hasattr(single_agent, "final_response"):
        print(":TestFail: info_no_final_response")
        return


if __name__ == "__main__":
    sys.stdout.write("---------------\n")
    # you can use this space for testing while you are
    # developing your tests
