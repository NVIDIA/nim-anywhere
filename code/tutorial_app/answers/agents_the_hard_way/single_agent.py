import getpass
import json
import os

from openai import OpenAI

# 1. get the API key
if not os.environ.get("NVIDIA_API_KEY"):
    os.environ["NVIDIA_API_KEY"] = getpass.getpass("Enter API key for NVIDIA: ")

# 2. Define the client
client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=os.environ.get("NVIDIA_API_KEY"))


# 3. define the tool
def add(a: int, b: int) -> int:
    """Add two integers.

    Args:
        a: First integer
        b: Second integer
    """
    return a + b


# 4. Define the tools list
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

# 5. Get the response for which tool to use
# TODO define a list of message


response = client.chat.completions.create(
    model="meta/llama-3.3-70b-instruct",
    messages=[{"role": "user", "content": "What is 3 plus 12?"}],
    tools=tools,
    tool_choice="auto",
    temperature=0.2,
    top_p=0.7,
    max_tokens=1024,
    stream=False,
)
print("response: ", response)

# 6. Parse the response and get the tool call parameters
tool_call = response.choices[0].message.tool_calls[0]
tool_name = tool_call.function.name  # 'add'
tool_args = json.loads(tool_call.function.arguments)  # {"a": 3, "b": 12}
tool_id = tool_call.id
# TODO print this in a pretty way on the left column

print("tool_call: ", tool_call)
print("tool_name: ", tool_name)
print("tool_args: ", tool_args)
print("tool_id: ", tool_id)

# TODO pretty print

# 7. Execute the tool

if "add" == tool_name:
    # Get the function from the global namespace
    result = add(**tool_args)
    print(f"Result of {tool_name}({tool_args}): {result}")

# 8. Create a new message list with the tool call + response
# TODO  change this to appending to the message list
messages = [
    {"role": "user", "content": "What's 3 + 12?"},
    response.choices[0].message,  # the assistant's tool call message
    {"role": "tool", "tool_call_id": tool_id, "name": "add", "content": str(result)},
]

# 9. Call again to let the model continue the chat
final_response = client.chat.completions.create(
    model="meta/llama-3.3-70b-instruct", messages=messages, temperature=0.2, max_tokens=512
)

print(final_response.choices[0].message.content)


# Additional content: while loop that let the model decide when to return answer
# langchain tool decorator, parser, influence the model's tool selection behavior using the tool_choice, ...

# # should only select model that support binding tools
# tool_models = [model for model in ChatNVIDIA.get_available_models() if model.supports_tools]
# print(tool_models)
# # 3. bind the tools to the model
# convert_to_openai_tool(tool)
# # How bind work: passed as part of the API request to the LLM — either in the tools field
# # (for OpenAI-like models) or injected into the prompt/system message for others.
# llm_with_tools = llm.bind_tools(tools)
