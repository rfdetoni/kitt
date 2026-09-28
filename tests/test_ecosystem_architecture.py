from __future__ import annotations

import unittest
from pathlib import Path

from scripts.validate_architecture import validate


ROOT = Path(__file__).resolve().parents[1]


class EcosystemArchitectureTests(unittest.TestCase):
    def test_catalog_matches_documented_bounded_contexts(self) -> None:
        owners = validate(ROOT)
        self.assertIn("agent-cli", owners)
        self.assertEqual(owners["agent-cli"], "rfdetoni/kitt-agent-cli")
        self.assertEqual(len(owners), len(set(owners.values())))


if __name__ == "__main__":
    unittest.main()
