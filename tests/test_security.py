"""Tests for shared HTTP authentication and signed sessions."""

import base64
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parents[1].joinpath("code")))

from nim_anywhere_security import (  # noqa: E402
    AUTH_USERNAME,
    AuthenticationMiddleware,
    InvalidSessionId,
    create_session_id,
    validate_session_id,
    verify_authorization_header,
)


class SecurityTests(unittest.TestCase):
    """Exercise credential comparisons and HMAC session validation."""

    api_key = "a" * 64

    def test_bearer_and_basic_authentication(self) -> None:
        basic = base64.b64encode(f"{AUTH_USERNAME}:{self.api_key}".encode()).decode()
        self.assertTrue(verify_authorization_header(f"Bearer {self.api_key}", self.api_key))
        self.assertTrue(verify_authorization_header(f"Basic {basic}", self.api_key))
        self.assertFalse(verify_authorization_header("Bearer wrong", self.api_key))
        self.assertFalse(verify_authorization_header("Basic not-base64", self.api_key))

    def test_sessions_are_signed_and_tamper_evident(self) -> None:
        with patch.dict(os.environ, {"NIM_ANYWHERE_API_KEY": self.api_key}):
            session_id = create_session_id()
            self.assertEqual(validate_session_id(session_id), session_id)
            with self.assertRaises(InvalidSessionId):
                validate_session_id("x" + session_id)

    def test_middleware_fails_closed_and_keeps_health_public(self) -> None:
        app = FastAPI()
        app.add_middleware(AuthenticationMiddleware)

        @app.get("/healthz")
        def health() -> dict[str, str]:
            return {"status": "ok"}

        @app.get("/private")
        def private() -> dict[str, str]:
            return {"status": "authenticated"}

        with patch.dict(os.environ, {"NIM_ANYWHERE_API_KEY": self.api_key}):
            client = TestClient(app)
            self.assertEqual(client.get("/healthz").status_code, 200)
            self.assertEqual(client.get("/private").status_code, 401)
            response = client.get("/private", headers={"Authorization": f"Bearer {self.api_key}"})
            self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
