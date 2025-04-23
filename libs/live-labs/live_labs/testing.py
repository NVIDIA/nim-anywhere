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
"""Live Labs Testing

Helpers for writing tests.

TestFail is the standard exception to raise when a custom test fails.

isolate is a decorator that will run a test in a custom Python environment.
This can be used to somewhat safely execute test code.

## Example
```python
def sample_test():
    raise TestFail("info_test_test")


@isolate(EDITOR_DIR)
def test_my_string():
    import file1  # pyright: ignore[reportMissingImports]

    print("Looking for my_string.")

    if not hasattr(file1, "my_string"):
        print(":TestFail: info_no_my_string")
        return

    print("Looking for five.")

    if file1.my_string != "five":
        print(":TestFail: info_my_string_not_five")
        return

    print("Looks good!")
```
"""
import functools
import inspect
import selectors
import subprocess
import sys
import time
from functools import partial
from pathlib import Path
from typing import Any, Callable, Iterator, TextIO, cast

import streamlit as st

_TIMEOUT = 10


class TestFail(Exception):
    """Indicates a test failed."""


class Runner:
    """Remote run decorator that streams stdout and stderr using selectors."""

    cwd: str
    exec: str
    _src: str
    _rc: None | int = None
    _testfail: None | str = None

    def __init__(self, cwd: str, exec: str, fun: Callable[..., Any]) -> None:
        """Initialize the Runner.

        Args:
            cwd: Directory to run the subprocess in.
            exec: Path to the Python executable.
            fun:   The function whose body will be sent to the subprocess.
        """
        self.cwd = cwd
        self.exec = exec

        # Read the function source and remove the isolate decorator
        fun_lines = inspect.getsource(fun).splitlines()
        fun_lines = [line for line in fun_lines if not line.startswith("@isolate(")]
        fun_src = "\n".join(fun_lines)

        # append a call to it under __main__
        self._src = f"{fun_src}\n\nif __name__ == '__main__':\n    {fun.__name__}()"
        functools.update_wrapper(self, fun)

    def execute(self) -> Iterator[str]:
        """Run the stored function in a subprocess and stream stdout/stderr.

        Yields:
            Lines of stdout or stderr as they arrive.

        Raises:
            TestFail: If the subprocess exits with a non-zero code.
        """
        sel = selectors.DefaultSelector()
        self._testfail = None
        self._rc = None

        with subprocess.Popen(
            [self.exec, "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=self.cwd,
        ) as proc:
            # start the test
            assert proc.stdin is not None
            proc.stdin.write(self._src)
            proc.stdin.close()

            # update the status
            status = st.empty()
            status.info("Running your code...")

            # register the process output
            if proc.stdout:
                sel.register(proc.stdout, selectors.EVENT_READ)
            if proc.stderr:
                sel.register(proc.stderr, selectors.EVENT_READ)

            # iterate  through stdout + stderr
            yield "```"
            start_time = time.monotonic()
            while time.monotonic() - start_time < _TIMEOUT:
                for key, _ in sel.select(timeout=0.1):
                    pipe = cast(TextIO, key.fileobj)
                    line = pipe.readline()

                    # end of file
                    if line == "":
                        pipe.close()
                        sel.unregister(pipe)
                        continue

                    # test failure occured
                    if line.startswith(":TestFail:"):
                        self._testfail = line[10:].strip()
                        continue

                    # normal terminal output
                    yield line
                    start_time = time.monotonic()

                # process has closed, selectors have finished
                if proc.poll() is not None and not sel.get_map():
                    break

            else:
                self._testfail = "info_test_timeout"
            yield "```"

            # update the status
            self._rc = proc.returncode
            if self._rc == 0:
                status.success("Code run is complete.")
            else:
                status.error("Code run is complete with errors.")

    def __call__(self) -> str:
        """Call the runner, stream to Streamlit, and return the full output."""
        output_text = st.write_stream(self.execute)
        assert isinstance(output_text, str)

        if self._testfail:
            raise TestFail(self._testfail)
        if self._rc and self._rc > 0:
            raise TestFail("info_test_nonzero_exit_code")

        # remove the markdown code block indicators
        output_text = "\n".join(output_text.splitlines()[1:-1])
        return output_text


def isolate(cwd: Path | None = None, exec: str | Path | None = None) -> Callable[[Callable[[], None]], Runner]:
    """Decorator to run a function in an isolated process."""
    valid_cwd = str(cwd or ".")
    valid_exec = str(exec or sys.executable)
    return partial(Runner, valid_cwd, valid_exec)
