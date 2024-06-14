#!/usr/bin/env python3

import jinja2
from chain_server import configuration
from frontend import configuration as fe_configuration


def resolve_child(schema, pinfo):
    ref = pinfo.get("$ref", "")
    if ref.startswith("#/$defs"):
        child = ref.split("/")[-1]
        return schema["$defs"][child]
    return None


def to_yaml(schema, level=0, env_var_prefixes=[("APP_", "__")]):
    indent = " " * 4 * level
    out = ""

    if schema["type"] == "object":
        for prop_name, prop in schema["properties"].items():
            prop_type = prop.get("anyOf", [{"type": prop.get("type")}])
            prop_desc = prop.get("description", "")
            prop_child = resolve_child(schema, prop)
            prop_default = "" if prop_child else (prop.get("default") or "~")

            # print the property description
            if prop_desc:
                out += f"{indent}# {prop_desc}\n"

            # print the property environment variables
            env_vars = prop.get("extra_env_vars", []) + [
                f"{prefix[0]}{prop_name.upper()}" for prefix in env_var_prefixes
            ]
            if not prop_child and env_vars:
                out += f"{indent}# ENV Variables: "
                out += ", ".join(env_vars)
                out += "\n"

            # print variable type
            if prop_type[0].get("type"):
                out += f"{indent}# Type: "
                out += ", ".join([t["type"] for t in prop_type])
                out += "\n"

            # print out the property
            out += f"{indent}{prop_name}: {prop_default}\n"

            # if the property references a child, print the child
            if prop_child:
                new_env_var_prefixes = [
                    (f"{prefix[0]}{prop_name.upper()}{prefix[1]}", prefix[1]) for prefix in env_var_prefixes
                ]
                out += to_yaml(prop_child, level=level + 1, env_var_prefixes=new_env_var_prefixes)

            out += "\n"

    return out


environment = jinja2.Environment(loader=jinja2.BaseLoader)
environment.filters["to_yaml"] = to_yaml

doc_page = environment.from_string(
    """

# {{docstring}}

## Chain Server config schema

```yaml
{{ cs_schema | to_yaml }}
```

## Chat Frontend config schema

The chat frontend has a few configuraiton options as well. They can be set in the same manner as the chain server.

```yaml
{{ fe_schema | to_yaml }}
```

"""
)

env_var_prefixes = [
    (source.prefix, source.nested_separator)
    for source in configuration.config.CONFIG_SOURCES
    if hasattr(source, "prefix")
]
docs = doc_page.render(
    docstring=configuration.__doc__,
    cs_schema=configuration.config.model_json_schema(),
    fe_schema=fe_configuration.config.model_json_schema(),
)
print(docs)
