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

"""This module contains the error messages that can be returned from the server."""

_SSE_ERROR_MESSAGE = {
    "type": "http.response.body",
    "body": (
        b'event: error\r\ndata: {"status_code": 500, "message": '
        b'"An error has occured in the chain server. '
        b'Please check the chain server logs for more information."}\r\n\r\n'
    ),
    "more_body": True,
}


# pylint: disable-next=too-few-public-methods # interface defined by starlette
class ErrorHandlerMiddleware:
    """A starlette middleware class for rewriting langserve sse errors."""

    def __init__(self, app):
        """Initialize the middleware."""
        self.app = app

    async def __call__(self, scope, receive, send):
        """Run the middleware filter."""
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        async def intercept_sse_errors(message):
            if message["type"] == "http.response.body":
                if message["body"].startswith(b"event: error"):
                    await send(_SSE_ERROR_MESSAGE)
                    return
            await send(message)

        await self.app(scope, receive, intercept_sse_errors)
