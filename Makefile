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

## Help command
default: help
.PHONY: help
help: # Show help for each of the Makefile recipes.
	@echo "Available targets:"
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

## CI Pipeline logic
.PHONY: ci lint format typecheck test check-notebooks
ci: lint format typecheck check-notebooks test # Run the ci pipeline locally

lint: # Examing the code with linters
	ruff check .

format: # Check the code formatting
	ruff format --check .

format-fix: # Autofix the code formatting where it is possible

typecheck: # Check the type hints in the code
	mypy .

test: # Run unit tests
	# pytest --quiet

check-notebooks:  # Ensure the jupyter notebooks have no saved
	find . -name "*.ipynb" -exec jupyter nbconvert --clear-output --inplace {} +
	git diff --exit-code || (echo "Notebooks have output. Clear it before committing." && exit 1)
