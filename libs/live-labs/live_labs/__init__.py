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
"""Live Labs

The modules in here contain the basic building blocks of a live lab page.
"""

import shutil
from contextlib import suppress
from pathlib import Path

import streamlit as st

from .lab import DEFAULT_STATE_FILE, Worksheet
from .localization import MessageCatalog
from .shell import AppShell

__all__ = ["AppShell", "MessageCatalog", "Worksheet", "reset_all_progress"]


def reset_all_progress():
    """Remove all files and reset cached progress."""
    # remove artifacts
    for artifact in st.session_state.get("artifacts", []):
        shutil.rmtree(artifact)

    # remove the cached state
    with suppress(FileNotFoundError):
        Path(DEFAULT_STATE_FILE).unlink()

    # clear the state
    keys = list(st.session_state.keys())
    for key in keys:
        st.session_state.pop(key)

    st.rerun()
