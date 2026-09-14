from __future__ import annotations

import io
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from installer.path_priority import _END, _START, ensure_managed_path
from installer.platforms import PlatformAdapter
from installer.progress import InstallProgress, progress_frame


class PathPriorityTests(unittest.TestCase):
    @staticmethod
    def _make_launcher(directory: Path, text: str) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "kitt"
        path.write_text(f"#!/bin/sh\nprintf '%s\\n' '{text}'\n", encoding="utf-8")
        path.chmod(0o755)
        return path

    def test_posix_install_prepends_managed_bin_for_current_and_new_shells(self) -> None:
        adapter = PlatformAdapter("linux", posix=True)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            home.mkdir()
            old_bin = root / "old-bin"
            new_bin = root / "new-bin"
            self._make_launcher(old_bin, "old")
            expected = self._make_launcher(new_bin, "new")

            with (
                patch("installer.path_priority.Path.home", return_value=home),
                patch.dict(
                    os.environ,
                    {"PATH": os.pathsep.join([str(old_bin), str(new_bin)]), "SHELL": "/bin/bash"},
                ),
            ):
                self.assertTrue(ensure_managed_path(adapter, new_bin))
                self.assertEqual(Path(shutil.which("kitt") or ""), expected)
                self.assertEqual(Path(os.environ["PATH"].split(os.pathsep)[0]), new_bin)

                profile = (home / ".profile").read_text(encoding="utf-8")
                bashrc = (home / ".bashrc").read_text(encoding="utf-8")
                self.assertEqual(profile.count(_START), 1)
                self.assertEqual(profile.count(_END), 1)
                self.assertIn(str(new_bin.resolve()), profile)
                self.assertIn(str(new_bin.resolve()), bashrc)

    def test_reinstall_is_idempotent_and_does_not_duplicate_profile_block(self) -> None:
        adapter = PlatformAdapter("linux", posix=True)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            home.mkdir()
            bin_dir = root / "bin"
            self._make_launcher(bin_dir, "managed")

            with (
                patch("installer.path_priority.Path.home", return_value=home),
                patch.dict(os.environ, {"PATH": str(bin_dir), "SHELL": "/bin/bash"}),
            ):
                self.assertTrue(ensure_managed_path(adapter, bin_dir))
                first = (home / ".profile").read_text(encoding="utf-8")
                self.assertTrue(ensure_managed_path(adapter, bin_dir))
                second = (home / ".profile").read_text(encoding="utf-8")

            self.assertEqual(first, second)
            self.assertEqual(second.count(_START), 1)
            self.assertEqual(second.count(_END), 1)

    def test_new_managed_bin_replaces_previous_profile_target(self) -> None:
        adapter = PlatformAdapter("linux", posix=True)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            home.mkdir()
            first_bin = root / "first-bin"
            second_bin = root / "second-bin"
            self._make_launcher(first_bin, "first")
            second_launcher = self._make_launcher(second_bin, "second")

            with (
                patch("installer.path_priority.Path.home", return_value=home),
                patch.dict(
                    os.environ,
                    {"PATH": os.pathsep.join([str(first_bin), str(second_bin)]), "SHELL": "/bin/zsh"},
                ),
            ):
                self.assertTrue(ensure_managed_path(adapter, first_bin))
                self.assertTrue(ensure_managed_path(adapter, second_bin))
                self.assertEqual(Path(shutil.which("kitt") or ""), second_launcher)

            for name in (".profile", ".zprofile", ".zshrc"):
                content = (home / name).read_text(encoding="utf-8")
                self.assertIn(str(second_bin.resolve()), content)
                self.assertNotIn(str(first_bin.resolve()), content)
                self.assertEqual(content.count(_START), 1)


class ProgressTests(unittest.TestCase):
    def test_progress_frame_has_stable_width_and_moves(self) -> None:
        first = progress_frame(0, width=20, span=5)
        later = progress_frame(4, width=20, span=5)
        self.assertEqual(len(first), 20)
        self.assertEqual(len(later), 20)
        self.assertNotEqual(first, later)
        self.assertIn("=", first)

    def test_non_tty_progress_has_clear_start_and_finish_messages(self) -> None:
        stream = io.StringIO()
        progress = InstallProgress("Installing test", stream=stream)
        progress.start()
        progress.finish(True)
        output = stream.getvalue()
        self.assertIn("Installing test...", output)
        self.assertIn("Installing test complete.", output)


if __name__ == "__main__":
    unittest.main()
