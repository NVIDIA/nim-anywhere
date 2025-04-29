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


## Describe the Tools
def prep_tools_list():
    """Write out the tools list."""
    send_keys(
        r"""


        # A list of tools for the LLM
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "add",
                    "description": "Add two integers.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "a": {"type": "integer", "description": "First integer"},
                            "b": {"type": "integer", "description": "Second integer"},
                        },
                        "required": ["a", "b"],
                    },
                },
            }
        ]
        """
    )


## Part 3 - Memory
def prep_messages():
    """Write a comment."""
    send_keys(
        r"""


        # Initilialize some short term memory
        """
    )


@isolate(EDITOR_DIR, PYTHON_EXE)
def test_messages():
    """create a message list"""
    import single_agent  # pyright: ignore[reportMissingImports]

    if not hasattr(single_agent, "messages"):
        print(":TestFail: info_no_messages")
        return

    if single_agent.messages != [{"role": "user", "content": "What is 3 plus 12?"}]:
        print(":TestFail: info_messages_not_correct")
        return


## Run the agent
def prep_run_agent():
    """Write a comment."""
    send_keys(
        r"""


        # Prompt the model for a response to the question and update the memory
        """
    )


@isolate(EDITOR_DIR, PYTHON_EXE)
def test_run_agent():
    """Wait for llm response."""
    import single_agent  # pyright: ignore[reportMissingImports]

    if not hasattr(single_agent, "messages"):
        print(":TestFail: info_no_messages")
        return

    if len(single_agent.messages) < 2:  # noqa
        print(":TestFail: info_messages_too_short")
        return

    if single_agent.messages[1]["role"] != "assistant":
        print(":TestFail: info_bad_message_order")
        return

    print(single_agent.messages[1])


## Part 4 - Routing
def prep_extract_tool():
    """Write some comments."""
    send_keys(
        r"""


        # Extract tool request
        """
    )


@isolate(EDITOR_DIR, PYTHON_EXE)
def test_extract_tool():
    """Wait for tool execution."""
    import single_agent  # pyright: ignore[reportMissingImports]

    # check for variable
    for var, var_type in {"tool_name": str, "tool_args": dict, "tool_id": str}.items():
        if not hasattr(single_agent, var):
            print(f":TestFail: info_no_{var}")
            return

        var_val = getattr(single_agent, var)

        if not isinstance(var_val, var_type):
            print(f":TestFail: info_no_{var}")
            return


## Tool Calling
def prep_execute_tool():
    """Write some comments."""
    send_keys(
        r"""


        # Run the requested tool
        """
    )


@isolate(EDITOR_DIR, PYTHON_EXE)
def test_execute_tool():
    """Wait for tool execution."""
    import numbers

    import single_agent  # pyright: ignore[reportMissingImports]

    # check for variable
    if not hasattr(single_agent, "tool_out"):
        print(":TestFail: info_no_tool_out")
        return

    # check variable type
    if not isinstance(single_agent.tool_out, numbers.Number):
        print(":TestFail: info_tool_out_not_num")
        return


## Update the memory
def prep_update_memory():
    """Write some comments."""
    send_keys(
        r"""


        # Save the tool output into the memory
        tool_result = {"role": "tool", "tool_call_id": tool_id, "name": tool_name, "content": str(tool_out)}
        messages.append(tool_result)
        """
    )


## Loop back to the model
def prep_call_model_again():
    """Write some comments."""
    send_keys(
        r"""


        # Call the model again with the tool output
        """
    )


@isolate(EDITOR_DIR, PYTHON_EXE)
def test_call_model_again():
    """call the model again"""
    import single_agent  # pyright: ignore[reportMissingImports]

    if not hasattr(single_agent, "messages"):
        print(":TestFail: info_no_messages")
        return

    if not isinstance(single_agent.messages, list):
        print(":TestFail: info_messages_all_wrong")
        return

    if len(single_agent.messages) == 3:  # noqa
        print(":TestFail: info_messages_len_3")
        return

    if len(single_agent.messages) != 4:  # noqa
        print(":TestFail: info_messages_all_wrong")
        return

    print(single_agent.messages[3])
