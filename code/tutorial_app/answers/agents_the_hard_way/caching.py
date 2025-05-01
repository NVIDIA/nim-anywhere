"""Some helpers for caching LLM calls during development."""

from collections import OrderedDict
from typing import Any

from cachier import cachier
from openai import OpenAI

CACHE_DIR = "/project/data/scratch"


def _call_llm_cached_hash(_: Any, kwds: OrderedDict[str, Any]) -> int:
    """Safely create a hash used for the cache."""
    model_name = kwds.get("model_name", "---")
    message_history = str(kwds.get("message_history"))
    tool_list = str(kwds.get("tool_list"))
    return hash(model_name + message_history + tool_list)


@cachier(cache_dir=CACHE_DIR, allow_none=False, hash_func=_call_llm_cached_hash)
def call_llm_cached(
    model_client: OpenAI,
    model_name: str,
    message_history: list[dict[str, str]],
    tool_list: None | list[dict[str, Any]] = None,
) -> None | dict[str, Any]:
    """Create OpenAI completions request."""
    if tool_list:
        response = model_client.chat.completions.create(
            model=model_name,
            messages=message_history,
            tools=tool_list,
            tool_choice="auto",
        )
    else:
        response = model_client.chat.completions.create(
            model=model_name,
            messages=message_history,
        )
    if response.choices:
        return response.choices[0].message.to_dict()
    else:
        return None
