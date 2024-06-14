#!/usr/bin/env python3
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

import argparse
from dataclasses import dataclass
from functools import cached_property
import logging
from pathlib import Path
import sys
import subprocess
from typing import Any, Optional,  TypeVar
import yaml


logging.basicConfig()
_LOGGER = logging.getLogger("manager")
EMPTY =  "__empty__"

def run_or_die(cmd: list[str], error_msg: str="Error running command.") -> tuple[bytes, bytes]:
    """Run a command and raise a RuntimeError if there is a problem."""
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"{error_msg}:\n{proc.stderr}")
    return (proc.stdout, proc.stderr)


ValueT = TypeVar("ValueT")


def safe_index(needle: ValueT, haystack: list[ValueT]) -> Optional[int]:
    """Find an item in a list, but return None if not found."""
    try:
        return haystack.index(needle)
    except ValueError:
        return None


@dataclass
class RuntimeEnvironment:
    """The possible runtime options."""

    uninstall: bool = False
    app: str =  ""
    verbose: bool = False

    @classmethod
    def from_args(cls) -> "RuntimeEnvironment":
        """Parse the CLI Arguments."""
        parser = argparse.ArgumentParser(prog="NVWB App Manager")
        parser.add_argument(
            "-u", "--uninstall", help="Uninstall the application from the menu.", action="store_true"
        )
        parser.add_argument(
            "-v", "--verbose", help="Increase output verbosity.", action="store_true"
        )
        parser.add_argument("app", type=str, help="Path to the application to install/uninstall.")
        args = parser.parse_args()
        opts = RuntimeEnvironment(**vars(args))

        if opts.verbose:
            _LOGGER.setLevel(logging.DEBUG)

        _LOGGER.info("Using options: %s", opts)
        return opts

    @cached_property
    def root(self) -> str:
        """Return the file path to the project root."""
        stdout, _ = run_or_die(["git", "rev-parse", "--show-toplevel"], "Error finding git repo's root.")
        out = stdout.strip().decode("ascii")
        return Path(out).absolute()

    @cached_property
    def variables(self) -> str:
        """Return the file path to the project's variables file."""
        return self.root.joinpath("variables.env")

    @cached_property
    def spec(self) -> str:
        """Return the file path to the project's variables file."""
        return self.root.joinpath(".project").joinpath("spec.yaml")


class App:
    """A representation of an nvwb app."""

    def __init__(self, path: str) -> None:
        """Initialize the class."""
        self._path =  Path(path).absolute()

        if not self._path.exists():
            raise RuntimeError(f"The specified application does not exist: {str(self._path)}")

    @cached_property
    def config(self) -> dict[str, str]:
        """Return the application's configuration values."""
        _LOGGER.info("Reading configuration for %s", str(self._path))
        _, stderr = run_or_die([(self._path), "config"], "Unable to read config from application.")

        return dict(
            [
                list(map(lambda x: x.decode("ascii"), line.split(b"=")))
                for line in stderr.strip().split(b"\n")
            ]
        )

    @cached_property
    def meta(self) -> dict[str, Any]:
        """Read the application's metadata entry."""
        _LOGGER.info("Reading metadata for %s", str(self._path))
        _, stderr = run_or_die([(self._path), "meta"], "Unable to read metadata from application.")
        return yaml.safe_load(stderr)



def update_variables(path: Path, config: dict[str, str], uninstall=False) -> None:
    """Update the variables file with the app's config."""
    existing_lines = open(path, "r").readlines()
    existing_lines_index = [line.split("=")[0] for line in existing_lines]
    if not existing_lines[-1].endswith("\n"):
        existing_lines[-1] =  existing_lines[-1] + "\n"
    file_changed = False

    for new_var, new_value in config.items():
        exists_line_ind = safe_index(new_var, existing_lines_index)
        exists =  exists_line_ind is not None

        if exists and uninstall:
            # remove the line from existing lines
            _LOGGER.debug("Removing %s from variables.", new_var)
            existing_lines.pop(exists_line_ind)
            existing_lines_index.pop(exists_line_ind)
            file_changed = True

        elif not exists and not uninstall:
            # add the line to the existing lines
            _LOGGER.debug("Adding %s to variables.", new_var)
            new_line = f"{new_var}={new_value}\n"
            existing_lines.append(new_line)
            existing_lines_index.append(new_var)
            file_changed = True

    # write the variables file
    if file_changed:
        _LOGGER.debug("Saving new variables file.")
        open(path, "w").writelines(existing_lines)
        return
    _LOGGER.warning("App configuration is already installed.")


def update_spec(path: Path, app_meta: dict[str, str], uninstall=False) -> None:
    """Update the projects specfile for this application."""
    with open(path, "r") as spec_file:
        spec  = yaml.load(spec_file, Loader=yaml.SafeLoader)
    changed = False

    found = False
    for app_ind, app in enumerate(spec.get("execution", {}).get("apps", [])):
        if app.get("name", EMPTY) == app_meta.get("name", EMPTY):
            found = True
            break

    if found and uninstall:
        _LOGGER.debug("Removing application from spec file.")
        spec["execution"]["apps"].pop(app_ind)
        changed = True

    elif not found and not uninstall:
        _LOGGER.debug("Adding the application to the spec file.")
        execution =  spec.get("execution", {})
        execution["apps"] = execution.get("apps", [])
        execution["apps"].append(app_meta)
        changed = True

    if changed:
        _LOGGER.debug("Saving updated project spec file.")
        with open(path, "w") as spec_file:
            yaml.safe_dump(spec, spec_file)
        return
    _LOGGER.warning("App is already loaded in spec file.")


def main() -> int:
    """The main routine for the app manager."""
    _LOGGER.setLevel(logging.INFO)
    env = RuntimeEnvironment.from_args()
    app = App(env.app)

    _LOGGER.info("Updating project environment variables.")
    update_variables(env.variables, app.config, env.uninstall)

    _LOGGER.info("Updating project spec file.")
    update_spec(env.spec, app.meta, env.uninstall)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as err:
        _LOGGER.error(str(err))
        sys.exit(1)
