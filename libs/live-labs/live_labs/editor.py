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
"""Live Labs Editor

Abstractions for creating a minimal IDE in browser.

st_editor is called to create a new set of ACE editors with tabs.
It can only be called once per page and should probably not be called outside of the Worksheet class.
"""

import json
from collections.abc import Generator
from pathlib import Path
from textwrap import dedent

import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from streamlit_ace import st_ace
from streamlit_javascript import st_javascript

_JS_CODE = Path(__file__).parent.joinpath("js", "editor.js").read_text("UTF-8").strip()
_JS_SEND_KEYS_CODE = Path(__file__).parent.joinpath("js", "editor.send_keys.js").read_text("UTF-8").strip()
_CSS = Path(__file__).parent.joinpath("css", "editor.css").read_text("UTF-8").strip()


def _new_ace_ide(base_dir: Path, key: str, value: str) -> None:
    """Create the streamlit object and sync with  filesystem."""
    code = st_ace(
        value=value,
        placeholder="Write your code here.",
        height="500px",
        font_size=20,
        language="python",
        theme="crimson_editor",
        key=key,
        show_print_margin=True,
        auto_update=True,
    )

    last_code_hash = st.session_state.get(f"{key}_hash", "")
    code_hash = hash(code)

    if last_code_hash != code_hash:
        st.session_state["code_change_derived"] = True
        base_dir.joinpath(key).write_text(code)
        st.session_state[f"{key}_hash"] = code_hash


def st_editor(base_dir: Path, files: list[str], init_data: list[str]) -> DeltaGenerator:
    """Add an editor to the page."""
    with st.container():
        tab_names = [f":material/data_object: {fname}" for fname in files] + [":material/terminal: Terminal Output"]
        editor_tabs = st.tabs(tab_names)
        for file_idx, file_tab in enumerate(editor_tabs[:-1]):
            with file_tab:
                _new_ace_ide(base_dir, files[file_idx], init_data[file_idx])

    with st.container(height=1, border=False):
        st_javascript(_JS_CODE)
        st.html(f"<style>{_CSS}</style>")

    return editor_tabs[-1]


def _sanitize_text(text: str) -> Generator[str]:
    """Internal generator for removing happy accidents from strings."""
    text = dedent(text)
    found_content = False

    for line in text.splitlines():
        clean_line = line.rstrip()
        if found_content or line:
            found_content = True
            yield clean_line


def send_keys(text: str) -> bool:
    """Write the text to the on screen editor."""
    if isinstance(text, bytes):
        text = text.decode("UTF-8")

    text = "\n".join(_sanitize_text(text))

    code = _JS_SEND_KEYS_CODE.replace("ARG", json.dumps(text))
    with st.container(height=1, border=False):
        st_javascript(code)

    return True
