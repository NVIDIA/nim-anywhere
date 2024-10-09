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

"""The control panel web app."""

from pathlib import Path

import gradio as gr
import jinja2
import yaml
from chain_server.configuration import Configuration as ChainConfiguration

from ... import mermaid
from ...common import IMG_DIR, THEME, USE_KB_INITIAL, USE_RERANKER_INITIAL
from ...configuration import config

# load custom style and scripts
_CSS_FILE = Path(__file__).parent.joinpath("style.css")
with open(_CSS_FILE, "r", encoding="UTF-8") as css_file:
    _CSS = css_file.read()
_MMD_FILE = Path(__file__).parent.joinpath("diagram.mmd.j2")
with open(_MMD_FILE, "r", encoding="UTF-8") as mmd_file:
    _MMD_TEMPLATE = mmd_file.read()
_MMD = environment = jinja2.Environment().from_string(_MMD_TEMPLATE)

_KB_TOGGLE_JS = """
async(val) => {
    window.top.postMessage({"use_kb": val}, '*');
}
"""
_RERANKER_TOGGLE_JS = """
async(val) => {
    window.top.postMessage({"use_reranker": val}, '*');
}
"""

KB_RERANKER_TOGGLE_JS = """
async(val) => {
    window.top.postMessage({"use_reranker": val}, '*');
}
"""

_CONFIG_CHANGES_JS = """
async() => {
    title = document.querySelector("div#config-toolbar p");
    if (! title.innerHTML.endsWith("🟠")) { title.innerHTML = title.innerHTML.slice(0,-2) + "🟠"; };
}
"""
_SAVE_CHANGES_JS = """
async() => {
    title = document.querySelector("div#config-toolbar p");
    if (! title.innerHTML.endsWith("🟢")) { title.innerHTML = title.innerHTML.slice(0,-2) + "🟢"; };
}
"""
_SAVE_IMG = IMG_DIR.joinpath("floppy.png")
_UNDO_IMG = IMG_DIR.joinpath("undo.png")
_HISTORY_IMG = IMG_DIR.joinpath("history.png")
_PSEUDO_FILE_NAME = "config.yaml 🟢"
with open(config.chain_config_file, "r", encoding="UTF-8") as config_file:
    _STARTING_CONFIG = config_file.read()

# web ui definition
with gr.Blocks(theme=THEME, css=_CSS, head=mermaid.HEAD) as page:
    with gr.Tab("Control Panel", elem_id="cp-tab", elem_classes=["invert-bg"]):

        # %% architecture control box
        with gr.Accordion(label="Retrieval Configuration"):
            with gr.Row(elem_id="kb-row"):
                with gr.Column():
                    use_kb = gr.Checkbox(USE_KB_INITIAL, label="Use knowledge base", interactive=True)
                    use_reranker = gr.Checkbox(USE_RERANKER_INITIAL, label="Use reranker", interactive=True)
            with gr.Row(elem_id="mmd-row"):
                mmd = mermaid.to_gradio(
                    _MMD.render(use_kb=USE_KB_INITIAL, use_reranker=USE_RERANKER_INITIAL, use_rewrite=False)
                )

        # %% chain server configuration text box
        with gr.Accordion(label="Chain Server Configuration"):
            with gr.Row(elem_id="config-row"):
                with gr.Column():
                    with gr.Group(elem_id="config-wrapper"):
                        with gr.Row(elem_id="config-toolbar", elem_classes=["toolbar"]):
                            file_title = gr.Markdown(_PSEUDO_FILE_NAME, elem_id="editor-title")
                            save_btn = gr.Button("", icon=_SAVE_IMG, elem_classes=["toolbar"])
                            undo_btn = gr.Button("", icon=_UNDO_IMG, elem_classes=["toolbar"])
                            reset_btn = gr.Button("", icon=_HISTORY_IMG, elem_classes=["toolbar"])
                        with gr.Row(elem_id="config-row-box"):
                            editor = gr.Code(
                                elem_id="config-editor",
                                interactive=True,
                                language="yaml",
                                show_label=False,
                                container=False,
                            )

        # %% common helpers
        def read_chain_config() -> str:
            """Read the chain config file."""
            with open(config.chain_config_file, "r", encoding="UTF-8") as cf:
                return cf.read()

        # %% updates a checkbox to be off and non-interactive
        def toggle_checkbox_interactivity(use_kb_value):
            """Enable or disable the second checkbox based on the first checkbox's value."""
            return gr.Checkbox(interactive=use_kb_value, value=False)

        # %% configure page events
        mermaid.init(page)
        page.load(read_chain_config, outputs=editor)

        # %% use kb toggle actions
        @gr.on(triggers=[use_kb.change, use_reranker.change], inputs=[use_kb, use_reranker], outputs=mmd)
        def kb_toggle(kb: bool, rerank: bool) -> str:
            """Toggle the knowledge base."""
            return mermaid.to_html(_MMD.render(use_kb=kb, use_reranker=rerank, use_rewrite=False))

        use_kb.change(None, use_kb, None, js=_KB_TOGGLE_JS)

        # %% turn off reranker option when knowledge base is not selected
        use_kb.change(fn=toggle_checkbox_interactivity, inputs=use_kb, outputs=use_reranker)

        # %% use reranker toggle actions
        use_reranker.change(None, use_reranker, None, js=_RERANKER_TOGGLE_JS)

        # %% undo button actions
        undo_btn.click(read_chain_config, outputs=editor)
        undo_btn.click(None, js=_SAVE_CHANGES_JS)

        # %% reset button actions
        @reset_btn.click(outputs=editor)
        def reset_demo() -> str:
            """Reset the configuration to the starting config."""
            return _STARTING_CONFIG

        # %% save button actions
        @save_btn.click(inputs=editor)
        def save_chain_config(config_txt: str) -> None:
            """Save the user's config file."""
            # validate yaml
            try:
                config_data = yaml.safe_load(config_txt)
            except Exception as err:
                raise SyntaxError(f"Error validating YAML syntax:\n{err}") from err

            # validate configuration
            try:
                _ = ChainConfiguration.model_validate(config_data)
            except Exception as err:
                raise SyntaxError(f"Error validating configuration content:\n{err}") from err

            # save configuration
            with open(config.chain_config_file, "w", encoding="UTF-8") as cf:
                cf.write(config_txt)

        save_btn.click(None, js=_SAVE_CHANGES_JS)

        # %% editor actions
        editor.input(None, js=_CONFIG_CHANGES_JS)
