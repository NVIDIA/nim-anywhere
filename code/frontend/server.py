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

"""A fastapi server to host gradio interface."""

from fastapi import FastAPI
from fastapi.responses import (
    FileResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
)
from fastapi.staticfiles import StaticFiles
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from . import pages, view
from .common import ASSETS_DIR, STATIC_DIR
from .configuration import config

INDEX_FILE = ASSETS_DIR.joinpath("index.html")


# %% create the web server
app = FastAPI()

# %% define and mount the views
views: list[view.View] = [
    view.View("Portability", left=pages.control, right=pages.chat),
]
app = view.mount_views(app, views)


@app.get(f"{config.proxy_prefix}views")
async def list_views() -> JSONResponse:
    """Enumerate the views available on the frontend."""
    return JSONResponse([view.json for view in views])


# %% mount the root page to the server
@app.get(config.proxy_prefix[:-1])
async def force_slash() -> RedirectResponse:
    """Force there to be a trailing slash on the URL for help with proxies."""
    return RedirectResponse(url=config.proxy_prefix)


@app.get(config.proxy_prefix)
async def root() -> FileResponse:
    """Render the main interface."""
    return FileResponse(INDEX_FILE)


# %% mount the static files to the server
app.mount(f"{config.proxy_prefix}static", StaticFiles(directory=STATIC_DIR), name="static")

# %% enable telemetry
FastAPIInstrumentor.instrument_app(app)


# %% add a health check
@app.get("/healthz", response_class=PlainTextResponse)
def healthz() -> str:
    """Report on the liveness of the server."""
    return "success"
