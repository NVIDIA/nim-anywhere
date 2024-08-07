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

"""Helpers for defining frontend views in pure Python."""

from dataclasses import dataclass, field

import gradio as gr
from fastapi import FastAPI

from .configuration import config


# create the views exposed on the frontend
@dataclass
class View:
    """A representation of a view on the frontpage."""

    name: str
    left: None | gr.Blocks = field(default=None)
    right: None | gr.Blocks = field(default=None)

    @property
    def left_url(self) -> None | str:
        """Return the URL for the left pane."""
        if self.left:
            return f"{config.proxy_prefix}{self.name}-left"
        return None

    @property
    def right_url(self) -> None | str:
        """Return the URL for the right pane."""
        if self.right:
            return f"{config.proxy_prefix}{self.name}-right"
        return None

    @property
    def json(self) -> dict[str, str | None]:
        """Represent the view as dictionary for json."""
        return {"name": self.name, "left": self.left_url, "right": self.right_url}

    def mount_view(self, server: FastAPI) -> FastAPI:
        """Mount the pages in the view to the server."""
        if self.left:
            server = gr.mount_gradio_app(server, self.left, path=self.left_url, root_path=self.left_url)
        if self.right:
            server = gr.mount_gradio_app(server, self.right, path=self.right_url, root_path=self.right_url)
        return server


def mount_views(app: FastAPI, views: list[View]) -> FastAPI:
    """Mount all the views to the web server."""
    for view in views:
        app = view.mount_view(app)
    return app
