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

"""Helpers for using mermaid with gradio."""

import gradio as gr

HEAD = """
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.0/dist/mermaid.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.12.1/css/all.min.css">
"""

_ONLOAD = """
async()=>{ mermaid.run(); }
"""


def to_html(mmd: str, theme: str = "dark") -> str:
    """Wrap a mermaid graph with html tags."""
    return f"""
<pre class="mermaid">
---
config:
  theme: {theme}
---

{mmd}
</pre>"""


def to_gradio(mmd: str, theme: str = "dark") -> gr.HTML:
    """Create a Gradio HTML component for a mermaid graph."""
    html = to_html(mmd, theme)
    mmd = gr.HTML(html)
    # pylint: disable-next=no-member # false positive
    mmd.change(None, js="mermaid.init")
    return mmd


def init(gr_blks: gr.Blocks) -> None:
    """Initialize the mermaid diagram."""
    # pylint: disable-next=no-member # false positive
    gr_blks.load(None, js=_ONLOAD)
