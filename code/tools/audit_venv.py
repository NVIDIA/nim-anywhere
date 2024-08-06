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
"""Check the version of all the dependencies."""

# pylint: disable=bad-builtin,global-statement

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pprint import pprint
from typing import Any, Dict, List, Tuple

import requests
from pip._vendor.packaging.specifiers import SpecifierSet
from tqdm import tqdm

NOW = datetime.now()
VULN_MIRROR = "https://pyup.io/aws/safety/free/insecure_full.json"
VULN_DB = requests.get(VULN_MIRROR, timeout=15).json()
EXIT_CODE = 0


def _parse_arguments() -> argparse.Namespace:
    """Parse the CLI arguments."""
    parser = argparse.ArgumentParser("Dependency Auditor")
    parser.add_argument(
        "--ignore-healthy",
        action="store_true",
        default=False,
        help="If set, only dependencies at yellow, red, or unknown are displayed.",
    )
    parser.add_argument(
        "--max-age",
        type=int,
        default=30,
        help="Maximum number of days for a dependency to be considered old.",
    )
    return parser.parse_args()


def _read_dependencies() -> Tuple[List[Tuple[str, str]], Dict[str, List[str]]]:
    """Find all the dependencies of this project."""
    dep_tree = json.loads(
        subprocess.run(["pipdeptree", "--json", "--python", sys.executable], check=True, capture_output=True).stdout
    )

    all_deps = [(row["package"]["key"], row["package"]["installed_version"]) for row in dep_tree]
    dep_map: Dict[str, List[str]] = defaultdict(list)
    for row in dep_tree:
        for dep in row["dependencies"]:
            dep_map[dep["key"]].append(row["package"]["key"])

    return all_deps, dep_map


def _latest_ver(package: str, report: Dict[str, Any]) -> None:
    """Lookup the latest version of a package."""
    # lookup package in pip
    req = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=5)
    if req.status_code != 200:
        return
    metadata = req.json()

    # calculate age
    installed = report.get("installed", "0")
    installed_meta = metadata["releases"].get(installed)
    released = datetime.fromisoformat(installed_meta[0]["upload_time"])
    report["age_days"] = (NOW - released).days

    # find latest
    report["latest"] = metadata["info"]["version"]


def _security(package: str, report: Dict[str, Any], max_age: int) -> None:
    """Lookup the safety of a package."""
    global EXIT_CODE

    installed = report.get("installed", "0")
    latest = report.get("latest", "")
    age_days = report.get("age_days", "-1")

    # check for cves
    active_cves: List[Tuple[str, str]] = []
    db_records: List[Dict[str, Any]] = VULN_DB.get(package, [])
    for cve in db_records:
        for vuln_spec in cve["specs"]:
            if SpecifierSet(vuln_spec).contains(installed):
                active_cves.append(
                    (
                        cve["cve"],
                        f"https://nvd.nist.gov/vuln/detail/{cve['cve']}",
                    )
                )

    # assume an out of date copy
    report["health"] = "🟡"

    # the installed version is comprimised
    if active_cves:
        report["health"] = "🔴"
        report["cves"] = active_cves
        EXIT_CODE = 1

    # package was not found in pypi
    if age_days == -1:
        report["health"] = "⁇"

    # the installed version is not comprimised and (latest or relatively new-ish)
    if latest == installed or age_days < max_age:
        report["health"] = "🟢"


def main() -> None:
    """Execute main routine."""
    # lookup package information
    args = _parse_arguments()
    full_report = {}
    print("Reading project dependencies...")
    all_packages, depdency_map = _read_dependencies()

    print("Processing and scoring dependencies...")
    for pkg, installed in tqdm(all_packages):
        pkg_report = {"installed": installed}
        if depdency_map.get(pkg):
            pkg_report["required_by"] = depdency_map[pkg]
        _latest_ver(pkg, pkg_report)  # add age_days and latest
        _security(pkg, pkg_report, args.max_age)  # add cves and health score

        if not args.ignore_healthy or pkg_report.get("health", "🟢") != "🟢":
            full_report[pkg] = pkg_report

    print("\nFinal Report:")
    pprint(full_report, sort_dicts=False)

    sys.exit(EXIT_CODE)


if __name__ == "__main__":
    main()
