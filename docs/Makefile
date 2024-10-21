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
# See the License for the specifi
SHELL=/bin/bash
PANDOC_HEADER_OPTS =--from gfm --to gfm --extract-media=.static --embed-resources --standalone
PANDOC_OPTS =--from gfm --to gfm --standalone --toc --toc-depth=2 --extract-media=.static --embed-resources --standalone

HEADER_FILE=_HEADER.md
SUMMARY_FILE=_SUMMARY.md
TOC_FILE=_TOC.md

export PYTHONPATH := $(PYTHONPATH):../code

../README.md: *.md* ../code/*/configuration.py
	make --silent _render > ../README.md
	rm -rf ../.static; mv .static ..;


.PHONY: _render _markdown
.SILENT: _render _markdown
.ONESHELL: _markdown
_render: export MERMAID_FILTER_FORMAT=png
_render: export MERMAID_FILTER_WIDTH=800
_render:
	cat $(HEADER_FILE); echo " "
	pandoc $(PANDOC_HEADER_OPTS) $(SUMMARY_FILE); echo " "
	set -eo pipefail; $(MAKE) --silent _markdown | pandoc $(PANDOC_OPTS)
_markdown:
	for page in $$(cat $(TOC_FILE)); do
		if [[ $$page == *.py ]]; then
			./$$page 2> /dev/null || cat $$page || exit 1;
		else
			cat $$page || exit 1;
		fi
		echo " "
	done


.PHONY: clean all
clean:
	rm -rf ../README.md ../.static
all: clean ../README.md
