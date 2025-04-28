"""An example agent built from scratch."""

import json
import os

from caching import call_llm_cached
from openai import OpenAI

API_KEY = os.environ.get("NGC_API_KEY", "---")
MODEL_URL = "https://integrate.api.nvidia.com/v1"
MODEL_NAME = "meta/llama-3.3-70b-instruct"


# Connect to the model server
client = OpenAI(base_url=MODEL_URL, api_key=API_KEY)


# Create a tool for your agent
def add(a, b):
    return a + b


# Create a list of all the available tools
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


# Initilialize some short term memory
messages = [{"role": "user", "content": "What is 3 plus 12?"}]


# Prompt the model for a response to the question and update the memory
llm_response = call_llm_cached(client, messages, tools)
messages.append(llm_response)


# Get the tool call information from the LLM response
# Let's assume that exactly one tool has been called
tool_call = llm_response.choices[0].message.tool_calls[0]
tool_name = tool_call.function_name
tool_args = json.loads(tool_call.function.arguments)
tool_id = tool_call.id


# Run the requested tool
if tool_name == "add":
    tool_out = add(**tool_args)


# Save the tool output into the memory
tool_result = {"role": "tool", "tool_call_id": tool_id, "name": tool_name, "content": str(tool_out)}
messages.append(tool_result)


# Prompt the model again, this time with the tool output
final_response = call_llm_cached(client, messages, tools)
