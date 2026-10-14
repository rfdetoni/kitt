import tempfile
import unittest
from pathlib import Path

from scripts.audit_ecosystem_sources import REPOS, inventory, report


class SourceAuditTests(unittest.TestCase):
    def test_all_seven_roots_scanned_without_executing_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for repo in REPOS:
                (root / repo).mkdir()
            (root / REPOS[0] / "sample.py").write_text(
                "class Thing:\n"
                "    def _private(self):\n"
                "        return 1\n"
                "\n"
                "def handle(value):\n"
                "    if value:\n"
                "        return True\n"
                "    return False\n", encoding="utf-8")
            payload = inventory(root)
            self.assertEqual(payload["file_count"], 1)
            self.assertEqual(len(payload["repositories"]), 7)
            self.assertIn("Thing._private", [m["name"] for m in payload["methods"]])
            self.assertIn("_private", [m["symbol"] for m in payload["unreferenced_private_candidates"]])
            self.assertIn("kitt-agent-cli", report(payload))

    def test_fails_if_any_repository_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                inventory(Path(tmp))


if __name__ == "__main__":
    unittest.main()
