# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Filesystem confinement helpers for Live Labs."""

from collections.abc import Collection
from pathlib import Path


def confined_write_path(root: Path, untrusted_name: object, allowed_suffixes: Collection[str]) -> Path:
    """Return a direct child path suitable for writing an allowlisted file type."""
    if (
        not isinstance(untrusted_name, str)
        or not untrusted_name
        or "\x00" in untrusted_name
        or Path(untrusted_name).name != untrusted_name
    ):
        raise ValueError("Invalid file name.")

    resolved_root = root.resolve(strict=True)
    candidate = resolved_root.joinpath(untrusted_name).resolve(strict=False)
    try:
        candidate.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError("The file is outside the lab directory.") from error

    normalized_suffixes = {suffix.casefold() for suffix in allowed_suffixes}
    if candidate.suffix.lstrip(".").casefold() not in normalized_suffixes:
        raise ValueError("This file type cannot be written.")
    return candidate


def confined_file(root: Path, untrusted_path: object, allowed_suffixes: Collection[str]) -> Path:
    """Resolve a client-provided path and require a regular file beneath ``root``."""
    if not isinstance(untrusted_path, str) or not untrusted_path or "\x00" in untrusted_path:
        raise ValueError("Invalid file path.")

    resolved_root = root.resolve(strict=True)
    candidate = resolved_root.joinpath(untrusted_path).resolve(strict=True)
    try:
        candidate.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError("The selected file is outside the lab directory.") from error
    if not candidate.is_file():
        raise ValueError("The selected file is outside the lab directory.")

    normalized_suffixes = {suffix.casefold() for suffix in allowed_suffixes}
    if candidate.suffix.lstrip(".").casefold() not in normalized_suffixes:
        raise ValueError("This file type cannot be downloaded.")
    return candidate
