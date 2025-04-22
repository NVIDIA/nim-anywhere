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
"""Common code that is used to render and style boilerplate streamlit objects."""

import json
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, Optional

import streamlit as st
from jinja2 import BaseLoader, Environment
from pydantic import BaseModel, Field
from streamlit_autorefresh import st_autorefresh
from streamlit_extras.stateful_button import button

from live_labs import editor, localization, testing

if TYPE_CHECKING:
    from streamlit.delta_generator import DeltaGenerator

DEFAULT_STATE_FILE = Path("/project/data/scratch/tutorial_state.json")


def _slugify(name: str) -> str:
    """Convert a name into a slugged string."""

    def _is_valid(char: str) -> bool:
        """Only pass lowercase and underscores."""
        return (ord(char) > 96 and ord(char) < 123) or ord(char) == 95

    filtered_name = [x for x in name.lower().replace(" ", "_") if _is_valid(x)]
    return "".join(filtered_name)


def print_task(
    parent: str, task: localization.Task, test_suite: None | ModuleType, messages: localization.MessageCatalog
) -> bool:
    """Write tasks out to screen.

    Returns boolean to indicate if task printing should continue."""

    st.write("### " + task.name)
    st.markdown(task.msg, unsafe_allow_html=True)
    # html is allowed to enable <details> blocks

    # Lookup a test from the test module.
    test = None
    test_name = task.test
    if test_name and test_suite is not None:
        test = getattr(test_suite, test_name, None)
    result: Any = None

    if test:
        # continue task based on test function
        success, msg, result = testing.run_test(test)
        if not success:
            st.write("***")
            st.write("**" + messages.get("testing_msg", "") + "**")
        if msg is not None:
            st.info(messages.get(msg, msg) or msg)
        if not success:
            return False

    else:
        # continue task based on user input
        slug = _slugify(task.name)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("**" + messages.get("waiting_msg", "") + "**")
        with col2:
            done = button(messages.get("next"), key=f"{parent}_task_{slug}")
        if not done:
            return False

    # show success message after completion
    scs_msg = task.response
    if scs_msg is not None:
        st.write(" ")
        rtemplate = Environment(loader=BaseLoader()).from_string(task.response or "")
        st.success(rtemplate.render(result=result))

    return True


class Worksheet(BaseModel):
    """Wrapper to simplify creating a live lab worksheet."""

    autorefresh: int = 2500
    ephemeral: bool = False
    state_file: Path = DEFAULT_STATE_FILE

    completed_tasks: int = Field(0, init=False)
    total_tasks: int = Field(0, init=False)

    _body: Optional["DeltaGenerator"] = None
    _base_dir: Optional[Path] = None
    _files: Optional[list[str]] = None
    _files_data_init: Optional[list[str]] = None

    def __enter__(self) -> "Worksheet":
        """Initialize the theme."""
        # configure the main page
        with st.container(height=1, border=False):
            self.load_state()
            if self.autorefresh > 0:
                st_autorefresh(interval=self.autorefresh, key="autorefresh")

        # configure the editor
        if self._files and self._files_data_init and self._base_dir:
            self._body, editor_col = st.columns([1, 2])
            with editor_col:
                editor.st_editor(self._base_dir, self._files, self._files_data_init)
            self._body.__enter__()

        return self

    def __exit__(self, _, __, ___):
        """Cache data."""
        if not self.ephemeral:
            self.save_state()

    def with_editor(self, base_dir: Path, files: list[str]):
        """Enable the in page code editor."""
        self._base_dir = base_dir
        self._files = files
        self._files_data_init = [""] * len(files)

        if not base_dir.exists():
            base_dir.mkdir()
            artifacts = st.session_state.get("artifacts", []) + [str(base_dir)]
            st.session_state["artifacts"] = artifacts

        for idx, file in enumerate(self._files):
            fpath = self._base_dir.joinpath(file)
            if fpath.exists():
                self._files_data_init[idx] = fpath.read_text("utf-8")

        return self

    def load_state(self):
        """Load the state from json file."""
        if "_loaded" in st.session_state:
            return

        try:
            with self.state_file.open("r", encoding="UTF-8") as ptr:
                loaded_state = json.load(ptr)
        except (IOError, OSError):
            loaded_state = {}

        st.session_state.update(loaded_state)
        st.session_state["_loaded"] = True

    def save_state(self):
        """Save the session state for all sessions."""
        # compare states
        state_dict = st.session_state.to_dict()
        last_state_json = state_dict.pop("last_state", "{}")  # dont recurse and save last state
        # dont save autorefresh runtime var
        # dont save session scoped variables (*_derived)
        remove_keys = ["autorefresh"] + [key for key in state_dict.keys() if key.endswith("_derived")]
        _ = [state_dict.pop(key, None) for key in remove_keys]
        state_json = json.dumps(state_dict)

        # save state when changed
        if state_json != last_state_json:
            with self.state_file.open("w", encoding="UTF-8") as ptr:
                ptr.write(state_json)
            st.session_state["last_state"] = state_json

    def live_lab(self, name: str, messages: localization.MessageCatalog, test_suite: None | ModuleType = None):
        """Run the lab."""
        self.total_tasks += len(messages.tasks)
        for task in messages.tasks:
            if not print_task(name, task, test_suite, messages):
                break
            self.completed_tasks += 1
        else:
            # Print footer after last task
            msg = messages.get("closing_msg", None)
            if msg:
                st.success(msg)

        st.session_state[f"{name}_completed"] = self.completed_tasks
        st.session_state[f"{name}_total"] = self.total_tasks
