from __future__ import annotations

import io
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.validate_ecosystem_main import validate_main_heads


ROOT = Path(__file__).resolve().parents[1]


class EcosystemReleasePinTests(unittest.TestCase):
    def _mock_github(self, stale: bool = False):
        manifest = json.loads((ROOT / "ecosystem.release.json").read_text(encoding="utf-8"))
        by_repo = {
            item["repository"]: item["sha"]
            for item in manifest["components"].values()
        }

        def fake_urlopen(request, timeout=15):
            self.assertEqual(timeout, 15)
            repository = request.full_url.split("/repos/", 1)[1].split("/git/ref/", 1)[0]
            sha = by_repo[repository]
            if stale and repository == "rfdetoni/kitt-reverse-proxy":
                sha = "0" * 40
            return io.BytesIO(json.dumps({"object": {"sha": sha}}).encode())

        return fake_urlopen

    def test_all_current_main_heads_match_release_pins(self) -> None:
        with patch("scripts.validate_ecosystem_main.urlopen", side_effect=self._mock_github()):
            self.assertEqual(len(validate_main_heads(ROOT)), 7)

    def test_stale_main_pin_fails_instead_of_silently_installing_old_code(self) -> None:
        with patch("scripts.validate_ecosystem_main.urlopen", side_effect=self._mock_github(stale=True)):
            with self.assertRaisesRegex(ValueError, "release manifest is behind component main"):
                validate_main_heads(ROOT)


if __name__ == "__main__":
    unittest.main()
