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
"""Live Labs Helpers functions and constants."""

import json
import shutil
from contextlib import suppress
from pathlib import Path

import streamlit as st
from streamlit_javascript import st_javascript

_JS_SCROLL_TO_CODE = Path(__file__).parent.joinpath("js", "helpers.scroll_to.js").read_text("UTF-8").strip()

DEFAULT_STATE_FILE = Path("/project/data/scratch/tutorial_state.json")


def scroll_to(header_title: str):
    """Scroll the document to the requested header."""
    anchor = slugify(header_title, "-")
    code = _JS_SCROLL_TO_CODE.replace("ARG", json.dumps(anchor))
    with st.container(height=1, border=False):
        st_javascript(code, key=anchor)


def slugify(name: str, space: str = "_") -> str:
    """Convert a name into a slugged string."""

    def _is_valid(char: str) -> bool:
        """Only pass lowercase and spaces."""
        return (ord(char) > 96 and ord(char) < 123) or char == space  # noqa: PLR2004

    name = name.lower()
    name = name.replace(" ", space)
    return "".join([x for x in name if _is_valid(x)])


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
