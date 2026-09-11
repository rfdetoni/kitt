from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from installer.catalog import EcosystemCatalog
from installer.cli import build_parser
from installer.platforms import PlatformAdapter


ROOT = Path(__file__).resolve().parents[1]


class InstallerUpdateRegressionTests(unittest.TestCase):
    def test_default_install_tracks_main(self) -> None:
        with patch.dict(os.environ, {"KITT_REF": ""}):
            args = build_parser().parse_args([])
        self.assertEqual(args.ref, "main")

    def test_environment_can_select_locked_install(self) -> None:
        with patch.dict(os.environ, {"KITT_REF": "locked"}):
            args = build_parser().parse_args([])
        self.assertEqual(args.ref, "locked")

    def test_locked_ref_aliases_use_ecosystem_lock(self) -> None:
        catalog = EcosystemCatalog.load(ROOT)
        module = catalog.modules["agent-cli"]
        expected = catalog.locks[module.repository]
        self.assertEqual(catalog.locked_ref(module, "locked"), expected)
        self.assertEqual(catalog.locked_ref(module, "lock"), expected)
        self.assertEqual(catalog.locked_ref(module, None), expected)
        self.assertEqual(catalog.locked_ref(module, "main"), "main")
        self.assertEqual(catalog.locked_ref(module, "v1.2.3"), "v1.2.3")

    def test_reinstall_replaces_existing_launcher(self) -> None:
        adapter = PlatformAdapter("linux", posix=True)
        with tempfile.TemporaryDirectory() as temp:
            bin_dir = Path(temp)
            path = adapter.write_launcher(bin_dir, "kitt", ["/old/python", "-m", "old.module"])
            old = path.read_text(encoding="utf-8")

            replaced = adapter.write_launcher(
                bin_dir,
                "kitt",
                ["/new/python", "-m", "kitt.cli.main"],
            )

            self.assertEqual(replaced, path)
            current = path.read_text(encoding="utf-8")
            self.assertNotEqual(current, old)
            self.assertIn("/new/python", current)
            self.assertNotIn("/old/python", current)
            self.assertTrue(os.access(path, os.X_OK))

    @unittest.skipIf(os.name == "nt", "symlink replacement requires POSIX symlink semantics")
    def test_reinstall_replaces_symlink_instead_of_overwriting_its_target(self) -> None:
        adapter = PlatformAdapter("linux", posix=True)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            legacy_target = root / "legacy-kitt"
            legacy_target.write_text("legacy executable", encoding="utf-8")
            launcher = bin_dir / "kitt"
            launcher.symlink_to(legacy_target)

            adapter.write_launcher(bin_dir, "kitt", ["/new/python", "-m", "kitt.cli.main"])

            self.assertFalse(launcher.is_symlink())
            self.assertEqual(legacy_target.read_text(encoding="utf-8"), "legacy executable")
            self.assertIn("/new/python", launcher.read_text(encoding="utf-8"))

    def test_shadowed_launcher_is_detected(self) -> None:
        adapter = PlatformAdapter("linux", posix=True)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            old_bin = root / "old-bin"
            new_bin = root / "new-bin"
            old_bin.mkdir()
            new_bin.mkdir()

            old = old_bin / "kitt"
            old.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            old.chmod(0o755)
            new = adapter.write_launcher(new_bin, "kitt", ["/new/python", "-m", "kitt.cli.main"])

            with (
                patch.dict(os.environ, {"PATH": os.pathsep.join([str(old_bin), str(new_bin)])}),
                patch("installer.platforms.shutil.which", side_effect=lambda name: str(old) if name == "kitt" else None),
            ):
                conflicts = adapter.launcher_shadow_conflicts(new_bin)
                self.assertEqual(Path(conflicts["kitt"]), old)
                self.assertFalse(adapter.ensure_user_path(new_bin))

            with (
                patch.dict(os.environ, {"PATH": os.pathsep.join([str(new_bin), str(old_bin)])}),
                patch("installer.platforms.shutil.which", side_effect=lambda name: str(new) if name == "kitt" else None),
            ):
                self.assertEqual(adapter.launcher_shadow_conflicts(new_bin), {})
                self.assertTrue(adapter.ensure_user_path(new_bin))


if __name__ == "__main__":
    unittest.main()
