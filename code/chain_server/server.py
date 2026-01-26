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

# Use the environment variables we set in spec.yaml
llm = ChatNVIDIA(
    base_url=os.getenv("NVIDIA_LLM_URL"),
    model=os.getenv("LLM_MODEL_NAME"),
    temperature=0.1
)

embedder = NVIDIAEmbeddings(
    base_url=os.getenv("NVIDIA_EMBED_URL"),
    model=os.getenv("EMBEDDING_MODEL_NAME")
)

"""The definition of the NVIDIA Conversational RAG API server."""

import os

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.responses import PlainTextResponse, RedirectResponse
from langserve import add_routes
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from . import errors
from .chain import my_chain  # type: ignore

PROXY_PREFIX = os.environ.get("PROXY_PREFIX", None)
app = FastAPI(
    title="NVIDIA Conversational RAG",
    version="0.1.0",
    description="More advanced conversational RAG using NVIDIA components.",
    root_path=PROXY_PREFIX or "",
    middleware=[Middleware(errors.ErrorHandlerMiddleware)],
)


add_routes(
    app,
    my_chain,
)


# add a health check
@app.get("/healthz", response_class=PlainTextResponse)
def healthz() -> str:
    """Report on the liveness of the server."""
    return "success"


@app.get("/", response_class=RedirectResponse)
def root() -> str:
    """Handle requests to the root directory."""
    return f"{PROXY_PREFIX or ''}/playground/"


# enable telemetry
FastAPIInstrumentor.instrument_app(app)
