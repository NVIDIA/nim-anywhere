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

import os
import gradio as gr
import jinja2
import yaml
from chain_server.configuration import Configuration as ChainConfiguration

# NEW
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_milvus.vectorstores.milvus import Milvus
import shutil
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chain_server.configuration import config as chain_config



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
# new
_UPLOAD_IMG = IMG_DIR.joinpath("upload-button.png")
_PSEUDO_FILE_NAME = "config.yaml 🟢"
with open(config.chain_config_file, "r", encoding="UTF-8") as config_file:
    _STARTING_CONFIG = config_file.read()

# connect to our milvus DB
#new
embedding_model = NVIDIAEmbeddings(
    model=chain_config.embedding_model.name,
    base_url=str(chain_config.embedding_model.url),
    api_key=chain_config.nvidia_api_key,
    truncate="END"
)

vector_store = Milvus(
    embedding_function=embedding_model,
    connection_args={"uri": chain_config.milvus.url},
    collection_name=chain_config.milvus.collection_name,
    auto_id=True,
)

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

    # knowledge base tab
    with gr.Tab("Knowledge Base", elem_id="kb-tab", elem_classes=["invert-bg"]):

        # helper to upload a document to the milvus DB
        def upload_document(file_path):
            loader = PyPDFLoader(str(file_path))
            data = loader.load()
            text_splitter = RecursiveCharacterTextSplitter()
            all_splits = text_splitter.split_documents(data)
            vector_store.add_documents(documents=all_splits)

        # upload button action
        def upload_btn_callback(files):
            messages = []
            for file in files:
              full_file_path = str(file.name)
              file_name = file.name.split('/')[-1]  # Extract file name from path
              try:
                upload_document(full_file_path)
                messages.append(f"Successfully uploaded {file_name}")
              except ValueError as e:
                messages.append(f"Failed to upload {file_name}")
            return "<br>".join(messages)

        # refesh docs button action
        def list_documents_callback() -> str:

            # dummy value, uppre bound 100 documents
            results = vector_store.similarity_search("a", k=100)

            document_names = []

            for result in results:
                doc_name = result.metadata.get("source", "Unnamed Document")  # Default to 'Unnamed Document' 
                doc_name = doc_name.split('/')[-1]  # Extract file name from path
                document_names.append(doc_name)

            return "<br>".join(f"- {name}" for name in document_names)



        # %% upload file box
        with gr.Group(elem_id="upload-file-group"):
            upload_btn = gr.UploadButton("Upload PDFs", icon=_UPLOAD_IMG, file_types=[".pdf"], file_count="multiple")
            status = gr.Markdown(value="", visible=True)
            upload_btn.upload(upload_btn_callback, upload_btn, status)


        # %% Existing files box
        with gr.Group(elem_id="existing-files-group"):
            gr.Markdown("### Uploaded PDFs")
            output = gr.Markdown()
            output = list_documents_callback()
            refresh_docs_btn = gr.Button("Refresh")
            refresh_docs_btn.click(list_documents_callback, outputs=output)


        

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
