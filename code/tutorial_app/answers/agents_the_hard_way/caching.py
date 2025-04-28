"""Some helpers for caching LLM calls during development."""

from cachier import cachier

CACHE_DIR = "/project/data/scratch"


def _fail_safe_hash(args, kwds) -> int:
    """Safely create a hash used for the cache."""
    return hash(str(args) + str(kwds))


@cachier(cache_dir=CACHE_DIR, allow_none=False, hash_func=_fail_safe_hash)
def call_llm_cached(model_client, model_name, message_history, tool_list=None):
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
