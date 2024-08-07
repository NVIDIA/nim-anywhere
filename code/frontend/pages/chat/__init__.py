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

"""The gradio chat app in the frontend."""

import uuid
from pathlib import Path
from typing import AsyncGenerator, Any

import gradio as gr
from httpx import ConnectError, HTTPStatusError
from langserve import RemoteRunnable

from ...common import IMG_DIR, THEME, USE_KB_INITIAL, USE_RERANKER_INITIAL
from ...configuration import config

# load custom style and scripts
_CSS_FILE = Path(__file__).parent.joinpath("style.css")
with open(_CSS_FILE, "r", encoding="UTF-8") as css_file:
    _CSS = css_file.read()
_AVATAR_IMAGES = (
    IMG_DIR.joinpath("user_icon.svg"),
    IMG_DIR.joinpath("bot_icon.svg"),
)
_JS_FILE = Path(__file__).parent.joinpath("scripts.js")
with open(_JS_FILE, "r", encoding="UTF-8") as js_file:
    _HEAD = "<script>" + js_file.read() + "</script>"
_ONLOAD = "async()=>{ registerHandlers(); chatResize(); }"
_CHAIN: RemoteRunnable[dict[str, Any], str] = RemoteRunnable(str(config.chain_url))


# web ui definition
with gr.Blocks(theme=THEME, css=_CSS, head=_HEAD) as page:
    session_id = gr.State("")
    use_kb = gr.Checkbox(USE_KB_INITIAL, elem_id="use_kb", visible=False)
    use_reranker = gr.Checkbox(USE_RERANKER_INITIAL, elem_id="use_reranker", visible=False)

    with gr.Row(elem_id="chatbot-row"):
        chatbot = gr.Chatbot(
            elem_id="chat",
            container=False,
            bubble_full_width=False,
            sanitize_html=True,
            avatar_images=_AVATAR_IMAGES,
            show_copy_button=False,
        )

    with gr.Row(elem_id="input-row"):
        msg = gr.Textbox(container=False, elem_id="msg")
        submit = gr.Button("➤", elem_id="submit")

    page.load(None, js=_ONLOAD)

    @page.load(outputs=session_id)
    def sid_generator() -> str:
        """Generate a new session id."""
        return str(uuid.uuid4())

    @gr.on(
        triggers=[msg.submit, submit.click],
        inputs=[session_id, msg, chatbot, use_kb, use_reranker],
        outputs=[msg, chatbot],
    )
    async def stream_chain(
        sid: str, message: str, chat: list[list[str]], kb: bool, reranker: bool
    ) -> AsyncGenerator[tuple[str, list[list[str]]], None]:
        """Call the chain and stream the result back to Gradio."""
        chat += [[message, ""]]
        chain = _CHAIN.with_config(configurable={"session_id": sid})

        try:
            async for chunk in chain.astream({"question": message, "use_kb": kb, "use_reranker": reranker}):
                chat[-1][1] += chunk.content  # type: ignore  # langchain quirkiness
                yield "", chat
        except (HTTPStatusError, ConnectError) as exc:
            if isinstance(exc, ConnectError) or 400 <= exc.response.status_code < 500:
                chat[-1][1] = (
                    "❌ **Uh oh...**\n"
                    "I can't seem to reach to the chain server. "
                    "Please make sure the chain server is running and the frontend is properly configured. "
                    "For more details, check the logs for the frontend and chain server."
                )
            else:
                chat[-1][1] = (
                    "❌ **Uh oh...**\n"
                    "There was an error inside the chain server. "
                    "Please check the chain server logs for more information on this error."
                )

            yield "", chat
            raise exc
