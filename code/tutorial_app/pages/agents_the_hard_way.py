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
"""Excercise page layout."""

from pathlib import Path

import live_labs
import streamlit as st

from pages import agents_the_hard_way_tests as TESTS

MESSAGES = live_labs.MessageCatalog.from_page(__file__)
NAME = Path(__file__).stem

EDITOR_DIR = Path("/project/code").joinpath(NAME)
EDITOR_FILES = ["single_agent.py"]
# name of the editor file

with live_labs.Worksheet(name=NAME, autorefresh=0).with_editor(EDITOR_DIR, EDITOR_FILES) as worksheet:
    # Header
    st.title(MESSAGES.get("title"))
    st.write(MESSAGES.get("welcome_msg"))
    st.header(MESSAGES.get("header"), divider="gray")
    # TODO define in yaml

    # Print Tasks
    worksheet.live_lab(MESSAGES, TESTS)
