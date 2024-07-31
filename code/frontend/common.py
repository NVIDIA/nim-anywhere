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

"""A few common values used by all Gradio pages."""

from pathlib import Path

import gradio as gr

ASSETS_DIR = Path(__file__).parent.joinpath("_assets")
STATIC_DIR = Path(__file__).parent.joinpath("_static")
JS_DIR = STATIC_DIR.joinpath("js")
IMG_DIR = STATIC_DIR.joinpath("images")

USE_KB_INITIAL = True
USE_RERANKER_INITIAL = True

THEME = gr.themes.Default().load(ASSETS_DIR.joinpath("theme.json"))
