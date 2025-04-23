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
"""A generic settings page."""
from pathlib import Path

import streamlit as st
from streamlit_extras.stateful_button import button as st_toggle_btn
from streamlit_file_browser import st_file_browser

from live_labs import MessageCatalog, Worksheet, reset_all_progress

MESSAGES = MessageCatalog.from_page(__file__)
NAME = Path(__file__).stem

with Worksheet(name=NAME, ephemeral=True) as worksheet:

    # file browser
    with st.container(border=True):
        st.markdown("## Lab Results")
        globs = [path + "/**" for path in st.session_state.get("artifacts", [])]
        file_browser_event = st_file_browser(
            "/project/code",
            glob_patterns=globs,
            extentions=["py", "yaml", "txt"],
            show_preview=False,
        )

        if file_browser_event and file_browser_event.get("type", "") == "SELECT_FILE":
            file = Path("/project/code").joinpath(file_browser_event["target"]["path"])
            with file.open("rb") as ptr:
                st.download_button(label="Download File", data=ptr, file_name=file.name)

    # reset progress
    with st.container(border=True):
        col_1, col_2, col_3 = st.columns([1, 1, 1])
        with col_1:
            reset = st_toggle_btn("Reset your progress.", key="reset")
        if reset:
            with col_2:
                verify_reset = st.button("Are you sure?")
            if verify_reset:
                reset_all_progress()

    # break into two columns
    col_1, col_2 = st.columns([1, 1])

    # information on support logs
    with col_1:
        with st.container(border=True):
            st.header(MESSAGES.get("bundle_header"), divider="gray")
            st.markdown(MESSAGES.get("bundle_msg"))

    # information on developer forum
    with col_2:
        with st.container(border=True):
            st.header(MESSAGES.get("forum_header"), divider="gray")
            st.markdown(MESSAGES.get("forum_msg"))
