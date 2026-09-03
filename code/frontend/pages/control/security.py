# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Pure validation helpers for security-sensitive control-panel actions."""

import copy
import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

_EDITABLE_FIELDS: dict[str, frozenset[str] | None] = {
    "llm_model": frozenset({"name"}),
    "embedding_model": frozenset({"name"}),
    "reranking_model": frozenset({"name"}),
    "milvus": frozenset({"collection_name"}),
    "log_level": None,
}
_MAX_DOCUMENT_NAME_LENGTH = 255


class UnsafeConfigurationChange(ValueError):
    """Raised when web input attempts to change a protected configuration field."""


def editable_configuration(configuration: Any) -> dict[str, Any]:
    """Return only fields that are safe to display and change in the web UI."""
    log_level = configuration.log_level
    if hasattr(log_level, "value"):
        log_level = log_level.value
    return {
        "llm_model": {"name": configuration.llm_model.name},
        "embedding_model": {"name": configuration.embedding_model.name},
        "reranking_model": {"name": configuration.reranking_model.name},
        "milvus": {"collection_name": configuration.milvus.collection_name},
        "log_level": log_level,
    }


def merge_editable_configuration(current: Mapping[str, Any], requested: Any) -> dict[str, Any]:
    """Merge an allowlisted UI update without accepting secrets, URLs, or DSNs."""
    if not isinstance(requested, Mapping):
        raise UnsafeConfigurationChange("Configuration must be a YAML mapping.")

    unknown_top_level = set(requested) - set(_EDITABLE_FIELDS)
    if unknown_top_level:
        raise UnsafeConfigurationChange(
            "These fields cannot be changed in the web UI: " + ", ".join(sorted(unknown_top_level))
        )

    merged = copy.deepcopy(dict(current))
    for section, value in requested.items():
        allowed_nested_fields = _EDITABLE_FIELDS[section]
        if allowed_nested_fields is None:
            merged[section] = value
            continue

        if not isinstance(value, Mapping):
            raise UnsafeConfigurationChange(f"{section} must be a YAML mapping.")
        unknown_nested_fields = set(value) - allowed_nested_fields
        if unknown_nested_fields:
            names = ", ".join(f"{section}.{field}" for field in sorted(unknown_nested_fields))
            raise UnsafeConfigurationChange(f"These fields cannot be changed in the web UI: {names}")

        current_section = merged.setdefault(section, {})
        if not isinstance(current_section, dict):
            current_section = {}
            merged[section] = current_section
        current_section.update(value)

    return merged


def validate_document_selection(selected: Any, available: Iterable[str]) -> list[str]:
    """Require every requested deletion to match a current server-side document name."""
    if not isinstance(selected, (list, tuple, set)):
        raise ValueError("Document selection must be a list.")

    available_names = set(available)
    validated: list[str] = []
    for filename in selected:
        if (
            not isinstance(filename, str)
            or not filename
            or len(filename) > _MAX_DOCUMENT_NAME_LENGTH
            or any(character in filename for character in ("\x00", "\r", "\n"))
            or filename not in available_names
        ):
            raise ValueError("The document selection is invalid or stale. Refresh and try again.")
        validated.append(filename)
    return validated


def validate_pdf_filename(file_path: str) -> str:
    """Return a bounded basename for an uploaded PDF."""
    filename = Path(file_path).name
    if (
        not filename
        or len(filename) > _MAX_DOCUMENT_NAME_LENGTH
        or any(character in filename for character in ("\x00", "\r", "\n"))
        or Path(filename).suffix.casefold() != ".pdf"
    ):
        raise ValueError("Uploaded files must have a valid PDF filename.")
    return filename


def milvus_string_equality(field: str, value: str) -> str:
    """Build a Milvus equality expression with a JSON-escaped string literal."""
    if field != "simple_file_name":
        raise ValueError("Unsupported Milvus field.")
    return f"{field} == {json.dumps(value, ensure_ascii=True)}"
