from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from installer.managed_drift import repair_known_managed_drift


class InstallerManagedDriftTests(unittest.TestCase):
    def _git(self, repo: Path, *args: str) -> str:
        proc = subprocess.run(
            ["git", *args],
            cwd=repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return proc.stdout.strip()

    def _repo(self, root: Path) -> Path:
        repo = root / "kitt-reverse-proxy"
        repo.mkdir()
        self._git(repo, "init")
        self._git(repo, "config", "user.name", "KITT Test")
        self._git(repo, "config", "user.email", "kitt@example.invalid")
        lock = {
            "name": "kitt-reverse-proxy",
            "version": "3.0.2",
            "lockfileVersion": 3,
            "requires": True,
            "packages": {
                "": {
                    "name": "kitt-reverse-proxy",
                    "version": "3.0.2",
                    "dependencies": {"express": "5.2.1"},
                },
                "node_modules/express": {"version": "5.2.1"},
            },
        }
        (repo / "package-lock.json").write_text(
            json.dumps(lock, indent=2) + "\n",
            encoding="utf-8",
        )
        self._git(repo, "add", "package-lock.json")
        self._git(repo, "commit", "-m", "baseline")
        return repo

    def test_repairs_version_only_reverse_proxy_lock_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = self._repo(root)
            lock_path = repo / "package-lock.json"
            payload = json.loads(lock_path.read_text(encoding="utf-8"))
            payload["version"] = "3.0.3"
            payload["packages"][""]["version"] = "3.0.3"
            lock_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

            repaired = repair_known_managed_drift(root)

            self.assertEqual(repaired, (lock_path,))
            restored = json.loads(lock_path.read_text(encoding="utf-8"))
            self.assertEqual(restored["version"], "3.0.2")
            self.assertEqual(restored["packages"][""]["version"], "3.0.2")
            self.assertEqual(self._git(repo, "status", "--porcelain"), "")

    def test_dependency_changes_remain_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = self._repo(root)
            lock_path = repo / "package-lock.json"
            payload = json.loads(lock_path.read_text(encoding="utf-8"))
            payload["version"] = "3.0.3"
            payload["packages"][""]["version"] = "3.0.3"
            payload["packages"]["node_modules/express"]["version"] = "5.3.0"
            lock_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

            repaired = repair_known_managed_drift(root)

            self.assertEqual(repaired, ())
            current = json.loads(lock_path.read_text(encoding="utf-8"))
            self.assertEqual(current["packages"]["node_modules/express"]["version"], "5.3.0")
            self.assertIn("package-lock.json", self._git(repo, "status", "--porcelain"))

    def test_other_dirty_files_are_never_repaired(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = self._repo(root)
            lock_path = repo / "package-lock.json"
            payload = json.loads(lock_path.read_text(encoding="utf-8"))
            payload["version"] = "3.0.3"
            payload["packages"][""]["version"] = "3.0.3"
            lock_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            (repo / "local-change.txt").write_text("keep me\n", encoding="utf-8")

            repaired = repair_known_managed_drift(root)

            self.assertEqual(repaired, ())
            current = json.loads(lock_path.read_text(encoding="utf-8"))
            self.assertEqual(current["version"], "3.0.3")
            self.assertTrue((repo / "local-change.txt").exists())


if __name__ == "__main__":
    unittest.main()
