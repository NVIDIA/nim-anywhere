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
"""Helpers for testing lab steps."""
import functools
import inspect
import subprocess
import sys
from functools import partial
from pathlib import Path
from textwrap import dedent
from typing import Any

import streamlit as st


class TestFail(Exception):
    """Indicates a test failed."""


def run_test(fun) -> tuple[bool, None | str, None | Any]:
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
    try:
        result = fun()
        state = (True, None, result)
    except TestFail as exc:
        state = (False, str(exc), None)
    else:
        st.session_state[idx] = state

    return state


class Runner:  # pylint: disable=too-few-public-methods
    """Remote run decorator."""

    cwd: str
    exec: str
    _src: str

    def __init__(self, cwd: str, exec: str, fun: Any):
        """Initialize the class."""
        self.cwd = cwd
        self.exec = exec

        # read the function and strip off the signature
        fun_src = inspect.getsource(fun)
        fun_lines = [line for line in fun_src.splitlines() if line and line[0] == " "]
        self._src = dedent("\n".join(fun_lines))
        functools.update_wrapper(self, fun)

    def __call__(self):
        proc = subprocess.run(
            [self.exec, "-"], input=self._src, text=True, capture_output=True, cwd=self.cwd, check=False
        )
        if proc.returncode > 0:
            raise TestFail(proc.stderr)
        if proc.stderr:
            err_code = ("\n" + proc.stderr).splitlines()[-1]
            raise TestFail(err_code)


def isolate(cwd: Path | None = None, exec: str | Path | None = None):
    """Decorator to run a function in an isolated process."""

    valid_cwd = str(cwd or ".")
    valid_exec = str(exec or sys.executable)

    return partial(Runner, valid_cwd, valid_exec)
