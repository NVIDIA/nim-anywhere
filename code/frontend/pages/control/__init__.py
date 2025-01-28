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
import shutil
import glob
from typing import List
import time

import os
import gradio as gr
import jinja2
import yaml

from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_milvus.vectorstores.milvus import Milvus
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from chain_server.configuration import Configuration as ChainConfiguration
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
_UPLOAD_IMG = IMG_DIR.joinpath("upload-button.png")
_PSEUDO_FILE_NAME = "config.yaml 🟢"
with open(config.chain_config_file, "r", encoding="UTF-8") as config_file:
    _STARTING_CONFIG = config_file.read()

# connect to our milvus DB
embedding_model = NVIDIAEmbeddings(
    model=chain_config.embedding_model.name,
    base_url=str(chain_config.embedding_model.url),
    api_key=chain_config.nvidia_api_key,
    truncate="END",
)

vector_store = Milvus(
    embedding_function=embedding_model,
    connection_args={"uri": chain_config.milvus.url},
    collection_name=chain_config.milvus.collection_name,
    auto_id=True,
)

# web ui definition
with gr.Blocks(theme=THEME, css=_CSS, head=mermaid.HEAD) as page:

    # %% contrl panel tab
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
                            save_btn = gr.Button("", icon=str(_SAVE_IMG), elem_classes=["toolbar"])
                            undo_btn = gr.Button("", icon=str(_UNDO_IMG), elem_classes=["toolbar"])
                            reset_btn = gr.Button("", icon=str(_HISTORY_IMG), elem_classes=["toolbar"])
                        with gr.Row(elem_id="config-row-box"):
                            editor = gr.Code(
                                elem_id="config-editor",
                                interactive=True,
                                language="yaml",
                                show_label=False,
                                container=False,
                            )

    # %% knowledge base tab
    with gr.Tab("Knowledge Base", elem_id="kb-tab", elem_classes=["invert-bg"]):

        # upload file button
        upload_btn = gr.UploadButton("Upload PDFs", icon=str(_UPLOAD_IMG), file_types=[".pdf"], file_count="multiple")

        def refresh_button_callback():
            """Refesh docs button action"""

            # grab the first 100 documents in the knowledge base
            results = vector_store.similarity_search("a", k=100)
            document_names = []
            for result in results:
                doc_name = result.metadata.get("source", "Unnamed Document")  # default value 'Unnamed Document'
                doc_name = doc_name.split("/")[-1]  # extract file name from path
                document_names.append(doc_name)

            return gr.CheckboxGroup(
                label="Uploaded Documents",
                choices=document_names,
                elem_classes="checkbox-group",
                visible=True,
                value=[],
                interactive=True,
            )

        uploaded_files = refresh_button_callback()

        # %% refresh and delete buttons
        with gr.Row(equal_height=True):
            refresh_docs_btn = gr.Button("Refresh")

            # Link refresh button to callback
            refresh_docs_btn.click(refresh_button_callback, outputs=uploaded_files)

        with gr.Row(equal_height=True):
            delete_btn = gr.Button("Delete Selected")
            confirm_delete_btn = gr.Button("Confirm delete", variant="stop", visible=False)
            cancel_delete_btn = gr.Button("Cancel", visible=False)

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

        # %% upload document actions
        def upload_document(file_path, file_name) -> None:
            """Helper to upload a document to the milvus DB"""
            loader = PyPDFLoader(str(file_path))
            data = loader.load()

            # Combine pages of document into one document
            combined_content = "\n".join([page.page_content for page in data])
            new_metadata = data[0].metadata
            new_metadata["simple_file_name"] = file_name
            combined_document = [Document(page_content=combined_content, metadata=new_metadata)]

            vector_store.add_documents(documents=combined_document)

        def upload_btn_callback(files) -> str:
            """Upload button action"""

            # Specify chain server reload if inserting into an empty collection
            need_reload = False

            # Search with a filler query to see if there are any docs in the vector store
            docs = vector_store.similarity_search("a")
            if not docs:
                need_reload = True

            # Upload files
            for file in files:
                full_file_path = str(file.name)
                file_name = file.name.split("/")[-1]  # Extract file name from path
                try:
                    upload_document(full_file_path, file_name)
                except Exception as err:
                    raise IOError(f"Failed to upload {file_name}:\n{err}") from err

            # Perform reload
            if need_reload:
                reload_filename = "reload"
                with open(reload_filename, "w", encoding="utf-8") as file:
                    pass  # 'pass' ensures the file is created but does nothing else
                time.sleep(0.5)
                os.remove(reload_filename)

            # Refresh uploaded files checkboxes
            time.sleep(1)
            refresh_results = refresh_button_callback()

            return refresh_results

        # Link upload button to callback
        upload_btn.upload(upload_btn_callback, upload_btn, outputs=uploaded_files)

        # %% Delete document actions
        def delete_button_callback(selected_docs):
            """Delete Button Action (Does not actually delete documents)"""

            if not selected_docs:
                # no docs selected, do nothing
                return [gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)]

            # docs selected, show confirmation button
            return [gr.update(visible=False), gr.update(visible=True), gr.update(visible=True)]

        def confirm_delete_callback(selected_docs):
            """Confirm Delete Button Action (actually deletes docs)"""

            for filename in selected_docs:
                expr = f"simple_file_name == '{filename}'"
                try:
                    vector_store.delete(expr=expr)
                except Exception as err:
                    raise IOError(f"Failed to remove {filename}:\n{err}") from err

            time.sleep(1)
            refresh_results = refresh_button_callback()
            return [
                refresh_results,
                gr.update(visible=True),
                gr.update(visible=False),
                gr.update(visible=False),
            ]

        def cancel_delete_callback():
            """Cancel delete button action"""
            return [gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)]

        delete_btn.click(
            fn=delete_button_callback,
            inputs=[uploaded_files],
            outputs=[delete_btn, confirm_delete_btn, cancel_delete_btn],
        )

        confirm_delete_btn.click(
            fn=confirm_delete_callback,
            inputs=[uploaded_files],
            outputs=[uploaded_files, delete_btn, confirm_delete_btn, cancel_delete_btn],
        )

        cancel_delete_btn.click(
            fn=cancel_delete_callback, inputs=None, outputs=[delete_btn, confirm_delete_btn, cancel_delete_btn]
        )
