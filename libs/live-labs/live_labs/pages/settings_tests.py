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
"""Tests for the generic settings page."""
import shutil
from pathlib import Path

import streamlit as st

from live_labs.lab import DEFAULT_STATE_FILE


def remove_labs():
    """Remove artifacts created during the labs."""
    for artifact in st.session_state.get("artifacts", []):
        shutil.rmtree(artifact, ignore_errors=True)


def remove_state_file():
    """Wait for the projects to be deleted."""
    # remove the cached state
    try:
        Path(DEFAULT_STATE_FILE).unlink()
    except FileNotFoundError:
        pass

    # clear the state
    keys = list(st.session_state.keys())
    for key in keys:
        st.session_state.pop(key)
