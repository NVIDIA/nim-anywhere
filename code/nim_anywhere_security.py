# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Authentication and session security shared by the NIM Anywhere services."""

import base64
import binascii
import hashlib
import hmac
import os
import secrets
from collections.abc import Awaitable, Callable, Collection

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

API_KEY_ENV = "NIM_ANYWHERE_API_KEY"
AUTH_USERNAME = "nim-anywhere"
MINIMUM_API_KEY_LENGTH = 32


class InvalidSessionId(ValueError):
    """Raised when a caller supplies a malformed or forged session identifier."""


def get_api_key() -> str | None:
    """Return a sufficiently strong configured API key, or ``None``."""
    api_key = os.environ.get(API_KEY_ENV, "")
    if len(api_key) < MINIMUM_API_KEY_LENGTH:
        return None
    return api_key


def require_api_key() -> str:
    """Return the configured key, failing closed when it is missing or weak."""
    api_key = get_api_key()
    if api_key is None:
        raise RuntimeError(f"{API_KEY_ENV} must be configured with at least {MINIMUM_API_KEY_LENGTH} characters.")
    return api_key


def bearer_headers() -> dict[str, str]:
    """Build authentication headers for service-to-service requests."""
    return {"Authorization": f"Bearer {require_api_key()}"}


def verify_authorization_header(header: str | None, api_key: str) -> bool:
    """Validate either a Bearer token or browser-friendly HTTP Basic credentials."""
    if not header:
        return False

    scheme, separator, credentials = header.partition(" ")
    if not separator:
        return False

    if scheme.casefold() == "bearer":
        return secrets.compare_digest(credentials, api_key)

    if scheme.casefold() != "basic":
        return False

    try:
        decoded = base64.b64decode(credentials, validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        return False

    username, separator, password = decoded.partition(":")
    return bool(
        separator and secrets.compare_digest(username, AUTH_USERNAME) and secrets.compare_digest(password, api_key)
    )


def create_session_id() -> str:
    """Create an opaque session identifier protected by an HMAC signature."""
    nonce = secrets.token_urlsafe(32)
    signature = hmac.new(require_api_key().encode(), nonce.encode(), hashlib.sha256).hexdigest()
    return f"{nonce}.{signature}"


def validate_session_id(session_id: str) -> str:
    """Validate a signed session identifier before using it as a Redis key."""
    if not isinstance(session_id, str) or len(session_id) > 160:
        raise InvalidSessionId("Invalid session identifier.")

    nonce, separator, supplied_signature = session_id.rpartition(".")
    if not separator or not nonce or len(supplied_signature) != hashlib.sha256().digest_size * 2:
        raise InvalidSessionId("Invalid session identifier.")

    expected_signature = hmac.new(require_api_key().encode(), nonce.encode(), hashlib.sha256).hexdigest()
    if not secrets.compare_digest(supplied_signature, expected_signature):
        raise InvalidSessionId("Invalid session identifier.")
    return session_id


class AuthenticationMiddleware(BaseHTTPMiddleware):  # pylint: disable=too-few-public-methods
    """Require authentication for every request except explicit health checks."""

    def __init__(self, app, public_paths: Collection[str] = ("/healthz",)) -> None:
        super().__init__(app)
        self.public_paths = frozenset(public_paths)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if request.url.path in self.public_paths:
            return await call_next(request)

        api_key = get_api_key()
        if api_key is None:
            return JSONResponse(
                {"detail": f"Server authentication is not configured. Set {API_KEY_ENV}."},
                status_code=503,
            )

        if not verify_authorization_header(request.headers.get("Authorization"), api_key):
            return JSONResponse(
                {"detail": "Authentication required."},
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="NIM Anywhere", charset="UTF-8"'},
            )

        return await call_next(request)
