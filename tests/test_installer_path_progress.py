from __future__ import annotations

import io
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from installer.cli import _ensure_launcher_priority
from installer.core import InstallerError
from installer.path_priority import _END, _START, ensure_managed_path
from installer.platforms import PlatformAdapter
from installer.progress import InstallProgress, progress_frame


@unittest.skipIf(os.name == "nt", "POSIX shell profile semantics")
class PathPriorityTests(unittest.TestCase):
    @staticmethod
    def _make_launcher(directory: Path, text: str) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "kitt"
        path.write_text(f"#!/bin/sh\nprintf '%s\\n' '{text}'\n", encoding="utf-8")
        path.chmod(0o755)
        return path

    @staticmethod
    def _resolved_command(name: str) -> Path:
        active = shutil.which(name)
        if not active:
            return Path()
        return Path(active).resolve()

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
                self.assertEqual(self._resolved_command("kitt"), expected.resolve())
                self.assertEqual(
                    Path(os.environ["PATH"].split(os.pathsep)[0]).resolve(),
                    new_bin.resolve(),
                )

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
                self.assertEqual(self._resolved_command("kitt"), second_launcher.resolve())

            for name in (".profile", ".zprofile", ".zshrc"):
                content = (home / name).read_text(encoding="utf-8")
                self.assertIn(str(second_bin.resolve()), content)
                self.assertNotIn(str(first_bin.resolve()), content)
                self.assertEqual(content.count(_START), 1)

    def test_fish_conf_d_is_managed_and_idempotent(self) -> None:
        adapter = PlatformAdapter("linux", posix=True)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            home.mkdir()
            bin_dir = root / "bin"
            self._make_launcher(bin_dir, "managed")

            with (
                patch("installer.path_priority.Path.home", return_value=home),
                patch.dict(os.environ, {"PATH": str(bin_dir), "SHELL": "/usr/bin/fish"}),
            ):
                self.assertTrue(ensure_managed_path(adapter, bin_dir))
                fish_file = home / ".config" / "fish" / "conf.d" / "kitt-path.fish"
                first = fish_file.read_text(encoding="utf-8")
                self.assertTrue(ensure_managed_path(adapter, bin_dir))
                second = fish_file.read_text(encoding="utf-8")

            self.assertEqual(first, second)
            self.assertEqual(second.count(_START), 1)
            self.assertEqual(second.count(_END), 1)
            self.assertIn(str(bin_dir.resolve()), second)
            self.assertIn("set -gx PATH", second)

    def test_path_persistence_failure_is_reported(self) -> None:
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
                patch("installer.path_priority._atomic_write", side_effect=OSError("read-only profile")),
            ):
                self.assertFalse(ensure_managed_path(adapter, bin_dir))


class LauncherPriorityFinalizationTests(unittest.TestCase):
    def test_install_finalization_fails_when_durable_path_cannot_be_guaranteed(self) -> None:
        platform = PlatformAdapter("linux", posix=True)
        with (
            patch("installer.cli.ensure_managed_path", return_value=False),
            patch.object(platform, "launcher_shadow_conflicts", return_value={}),
        ):
            with self.assertRaises(InstallerError):
                _ensure_launcher_priority(platform, Path("managed-bin"))

    def test_install_finalization_fails_when_launcher_is_shadowed(self) -> None:
        platform = PlatformAdapter("linux", posix=True)
        with (
            patch("installer.cli.ensure_managed_path", return_value=True),
            patch.object(
                platform,
                "launcher_shadow_conflicts",
                return_value={"kitt": "/usr/local/bin/kitt"},
            ),
        ):
            with self.assertRaises(InstallerError):
                _ensure_launcher_priority(platform, Path("managed-bin"))


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
