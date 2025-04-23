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
"""Live Labs Lab Module

This module contains abstractions around creating the user interface for the individual labs. These lab interfaces
are called worksheets.

The Worksheet data model is used as the standard entry point to creating and customizing a lab worksheet.

## Example
```python
from pathlib import Path

import live_labs
import streamlit as st

from pages import editor_test_tests as TESTS

MESSAGES = live_labs.MessageCatalog.from_page(__file__)
NAME = Path(__file__).stem

EDITOR_DIR = Path("/project/code").joinpath(NAME)
EDITOR_FILES = ["file1.py", "file2.py"]

with live_labs.Worksheet(name=NAME, autorefresh=0).with_editor(EDITOR_DIR, EDITOR_FILES) as worksheet:
    # Header
    st.title(MESSAGES.get("title"))
    st.write(MESSAGES.get("welcome_msg"))
    st.header(MESSAGES.get("header"), divider="gray")

    # Print Tasks
    worksheet.live_lab(MESSAGES, TESTS)
```
"""

import json
from pathlib import Path
from types import ModuleType
from typing import Any, Optional

import streamlit as st
from jinja2 import BaseLoader, Environment
from pydantic import BaseModel, Field, PrivateAttr
from streamlit.delta_generator import DeltaGenerator
from streamlit_autorefresh import st_autorefresh
from streamlit_extras.stateful_button import button

from live_labs import editor, localization, testing

DEFAULT_STATE_FILE = Path("/project/data/scratch/tutorial_state.json")


def _slugify(name: str) -> str:
    """Convert a name into a slugged string."""

    def _is_valid(char: str) -> bool:
        """Only pass lowercase and underscores."""
        return (ord(char) > 96 and ord(char) < 123) or ord(char) == 95

    filtered_name = [x for x in name.lower().replace(" ", "_") if _is_valid(x)]
    return "".join(filtered_name)


class Worksheet(BaseModel):
    """Wrapper to simplify creating a live lab worksheet."""

    name: str
    autorefresh: int = 2500
    ephemeral: bool = False
    state_file: Path = DEFAULT_STATE_FILE

    completed_tasks: int = Field(0, init=False)
    total_tasks: int = Field(0, init=False)

    _body: Optional[DeltaGenerator] = PrivateAttr(None)
    _base_dir: Optional[Path] = PrivateAttr(None)
    _files: Optional[list[str]] = PrivateAttr(None)
    _files_data_init: Optional[list[str]] = PrivateAttr(None)
    _stdout: Optional[DeltaGenerator] = PrivateAttr(None)

    @property
    def stdout(self) -> DeltaGenerator:
        """Return the streamlit container for test output."""
        return self._stdout or st.container(height=1, border=False)

    @stdout.setter
    def stdout(self, val: Any) -> None:
        """Change the stdout output container."""
        type_check = val is None or isinstance(val, DeltaGenerator)
        assert type_check, "STDOUT container must be streamlit object or None."
        self._stdout = val

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
                self._stdout = editor.st_editor(self._base_dir, self._files, self._files_data_init)
            self._body.__enter__()

        return self

    def __exit__(self, _, __, ___):
        """Cache data."""
        if self._body:
            self._body.__exit__(None, None, None)
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

    def run_test(self, fun) -> tuple[bool, None | str, None | Any]:
        """Cache the state of a test once it passes."""
        cached_state: tuple[bool, None | str, None | Any]
        state: tuple[bool, None | str, None | Any]

        mod_name = fun.__module__.split(".")[-1]
        idx = mod_name + "_" + fun.__name__
        # recall state from cache, if it exists
        cached_state = st.session_state.get(idx, None)
        if cached_state is not None:
            return cached_state

        # run the test to evaluate state
        with self.stdout:
            try:
                result = fun()
                state = (True, None, result)
            except testing.TestFail as exc:
                state = (False, str(exc), None)
            else:
                st.session_state[idx] = state

        return state

    def print_task(
        self, task: localization.Task, test_suite: None | ModuleType, messages: localization.MessageCatalog
    ) -> bool:
        """Write tasks out to screen.

        Returns boolean to indicate if task printing should continue."""

        st.write("### " + task.name)
        st.markdown(task.msg, unsafe_allow_html=True)
        # html is allowed to enable <details> blocks

        # Lookup a test from the test module.
        test = task.get_test(test_suite)
        result: str | None = ""

        if test:
            # continue task based on test function
            success, msg, result = self.run_test(test)
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
                done = button(messages.get("next"), key=f"{self.name}_task_{slug}")
            if not done:
                return False

        # show success message after completion
        scs_msg = task.response
        if scs_msg is not None:
            st.write(" ")
            rtemplate = Environment(loader=BaseLoader()).from_string(task.response or "")
            st.success(rtemplate.render(result=result))

        return True

    def live_lab(self, messages: localization.MessageCatalog, test_suite: None | ModuleType = None):
        """Run the lab."""
        self.total_tasks += len(messages.tasks)
        for task in messages.tasks:
            if not self.print_task(task, test_suite, messages):
                break
            self.completed_tasks += 1
        else:
            # Print footer after last task
            msg = messages.get("closing_msg", None)
            if msg:
                st.success(msg)

        st.session_state[f"{self.name}_completed"] = self.completed_tasks
        st.session_state[f"{self.name}_total"] = self.total_tasks
