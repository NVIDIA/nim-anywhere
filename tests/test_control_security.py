"""Tests for security-sensitive control-panel validation."""

import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace

MODULE_PATH = Path(__file__).parents[1].joinpath("code", "frontend", "pages", "control", "security.py")
SPEC = importlib.util.spec_from_file_location("control_security", MODULE_PATH)
assert SPEC and SPEC.loader
control_security = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(control_security)


class ControlSecurityTests(unittest.TestCase):
    """Verify configuration allowlisting and Milvus expression safety."""

    def test_editable_configuration_omits_secrets_and_urls(self) -> None:
        configuration = SimpleNamespace(
            llm_model=SimpleNamespace(name="llm", url="https://attacker.invalid"),
            embedding_model=SimpleNamespace(name="embed", url="https://attacker.invalid"),
            reranking_model=SimpleNamespace(name="rerank", url="https://attacker.invalid"),
            milvus=SimpleNamespace(collection_name="collection", url="http://milvus:19530"),
            redis_dsn="redis://secret@redis",
            nvidia_api_key="nvapi-secret",
            log_level=SimpleNamespace(value="INFO"),
        )
        public = control_security.editable_configuration(configuration)
        rendered = repr(public)
        self.assertNotIn("url", rendered)
        self.assertNotIn("secret", rendered)

    def test_protected_configuration_fields_are_rejected(self) -> None:
        current = {"llm_model": {"name": "safe", "url": "https://integrate.api.nvidia.com/v1"}}
        with self.assertRaises(control_security.UnsafeConfigurationChange):
            control_security.merge_editable_configuration(
                current,
                {"llm_model": {"url": "https://attacker.invalid"}},
            )
        with self.assertRaises(control_security.UnsafeConfigurationChange):
            control_security.merge_editable_configuration(current, {"nvidia_api_key": "nvapi-stolen"})

    def test_delete_selection_is_server_validated_and_json_escaped(self) -> None:
        attack = "' or simple_file_name != '"
        self.assertEqual(control_security.validate_document_selection([attack], [attack]), [attack])
        expression = control_security.milvus_string_equality("simple_file_name", attack)
        self.assertEqual(expression, "simple_file_name == \"' or simple_file_name != '\"")
        with self.assertRaises(ValueError):
            control_security.validate_document_selection(["not-present.pdf"], ["present.pdf"])


if __name__ == "__main__":
    unittest.main()
