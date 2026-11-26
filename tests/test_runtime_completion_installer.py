from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from installer.catalog import EcosystemCatalog
from installer.cli import build_parser, main
from installer.core import EcosystemInstaller, InstallerOptions
from installer.platforms import PlatformAdapter


ROOT = Path(__file__).resolve().parents[1]


class RuntimeCompletionInstallerTests(unittest.TestCase):
    def test_n_minus_one_backup_rollback_repair_and_uninstall(self) -> None:
        catalog = EcosystemCatalog.load(ROOT)
        adapter = PlatformAdapter("linux", posix=True)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "kitt-root"
            bin_dir = Path(temp) / "bin"
            root.mkdir()
            bin_dir.mkdir()
            launcher = adapter.write_launcher(bin_dir, "kitt", ["/v1/python", "-m", "kitt"])
            (root / "installed-state.json").write_text(
                json.dumps({"ecosystem_version": "0.16.75", "launchers": [str(launcher)]}),
                encoding="utf-8",
            )
            inst = EcosystemInstaller(catalog, adapter, InstallerOptions(root=root, bin_dir=bin_dir))
            inst._save_n_minus_one_backup()

            # Simulate interrupted N+1 install & launcher overwrite
            (root / ".staging" / "venv-999").mkdir(parents=True)
            adapter.write_launcher(bin_dir, "kitt", ["/v2/python", "-m", "kitt"])
            (root / "installed-state.json").write_text(
                json.dumps({"ecosystem_version": "0.16.76", "launchers": [str(launcher)]}),
                encoding="utf-8",
            )

            with (
                patch("installer.platforms.shutil.which", return_value=None),
                patch("installer.platforms._run_capture", return_value=(0, "")),
            ):
                rep = inst.repair_interrupted_install()
                self.assertTrue(rep["cleaned_staging"])
                self.assertFalse((root / ".staging").exists())

                rb = inst.rollback_to_previous()
                self.assertEqual(rb["status"], "rolled_back")
                restored_state = json.loads((root / "installed-state.json").read_text(encoding="utf-8"))
                self.assertEqual(restored_state["ecosystem_version"], "0.16.75")
                self.assertIn("/v1/python", launcher.read_text(encoding="utf-8"))

                inst.uninstall()
                self.assertFalse(root.exists())
                self.assertFalse(launcher.exists())

    def test_windows_cmd_launcher_supports_utf8(self) -> None:
        adapter = PlatformAdapter("windows", posix=False)
        with tempfile.TemporaryDirectory() as temp:
            bin_dir = Path(temp) / "José" / "bin"
            cmd = adapter.write_launcher(bin_dir, "kitt", [str(bin_dir / "python.exe"), "--help"])
            text = cmd.read_text(encoding="utf-8")
            self.assertIn("chcp 65001 >nul", text)
            self.assertIn("José", text)

    def test_capabilities_honest_reporting_and_vm_flags(self) -> None:
        args = build_parser().parse_args([
            "--with-vm-lab",
            "--vm-image-sha512", "a" * 128,
            "--vm-image-url", "https://cloud.debian.org/images/cloud/trixie/latest/debian-13-generic-amd64.qcow2",
            "--vm-gpg-keyring", "/tmp/debian.gpg",
        ])
        self.assertIn("debian.org", args.vm_image_url)
        self.assertEqual(main(["--capabilities"]), 0)


if __name__ == "__main__":
    unittest.main()
