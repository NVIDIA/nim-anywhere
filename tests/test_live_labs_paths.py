"""Tests for Live Labs read/write path confinement."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1].joinpath("libs", "live-labs", "live_labs", "paths.py")
SPEC = importlib.util.spec_from_file_location("live_labs_paths", MODULE_PATH)
assert SPEC and SPEC.loader
live_labs_paths = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(live_labs_paths)


class PathSecurityTests(unittest.TestCase):
    """Verify traversal and symlink escapes are rejected."""

    def test_confined_file_rejects_traversal_and_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            root = base.joinpath("root")
            root.mkdir()
            allowed = root.joinpath("result.txt")
            allowed.write_text("safe", encoding="UTF-8")
            outside = base.joinpath("secret.txt")
            outside.write_text("secret", encoding="UTF-8")
            root.joinpath("link.txt").symlink_to(outside)

            self.assertEqual(live_labs_paths.confined_file(root, "result.txt", {"txt"}), allowed.resolve())
            with self.assertRaises(ValueError):
                live_labs_paths.confined_file(root, "../secret.txt", {"txt"})
            with self.assertRaises(ValueError):
                live_labs_paths.confined_file(root, "link.txt", {"txt"})

    def test_confined_write_requires_direct_python_child(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            expected = root.joinpath("lesson.py")
            self.assertEqual(live_labs_paths.confined_write_path(root, "lesson.py", {"py"}), expected.resolve())
            with self.assertRaises(ValueError):
                live_labs_paths.confined_write_path(root, "../lesson.py", {"py"})
            with self.assertRaises(ValueError):
                live_labs_paths.confined_write_path(root, "lesson.sh", {"py"})


if __name__ == "__main__":
    unittest.main()
