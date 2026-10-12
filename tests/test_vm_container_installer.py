"""Installer opt-in Docker/Podman VM preflight; ordinary installs unchanged."""
from __future__ import annotations
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from installer.cli import build_parser
from installer.vm_containers import VMContainerError, check_container_runtime, pull_prebuilt


class InstallerContainerVMTests(unittest.TestCase):
    def test_cli_flag_opt_in_and_profiles(self):
        parser = build_parser()
        default = parser.parse_args(["--preset", "agent"])
        self.assertFalse(default.with_vm_containers)
        self.assertFalse(default.vm_pull_images)
        selected = parser.parse_args(["--preset", "agent", "--with-vm-containers",
                                     "--vm-container-runtime", "podman",
                                     "--vm-container-image-profile", "full",
                                     "--vm-pull-images"])
        self.assertTrue(selected.with_vm_containers)
        self.assertTrue(selected.vm_pull_images)
        self.assertEqual(selected.vm_container_runtime, "podman")

    def test_unsupported_platform_and_missing_runtime(self):
        with patch("installer.vm_containers.sys.platform", "win32"):
            with self.assertRaises(VMContainerError):
                check_container_runtime("podman")
        with patch("installer.vm_containers.sys.platform", "linux"), \
             patch("installer.vm_containers.shutil.which", return_value=None):
            with self.assertRaises(VMContainerError):
                check_container_runtime("docker")
        with self.assertRaises(VMContainerError):
            check_container_runtime("unknown")

    def test_runtime_diagnostic_without_root_permissions(self):
        with patch("installer.vm_containers.sys.platform", "linux"), \
             patch("installer.vm_containers.shutil.which", return_value="/usr/bin/podman"), \
             patch("installer.vm_containers.os.access", return_value=False), \
             patch("installer.vm_containers.subprocess.run", return_value=SimpleNamespace(returncode=0)):
            outcome = check_container_runtime("podman")
        self.assertTrue(outcome["ready"])
        self.assertFalse(outcome["kvm_accessible"])
        self.assertTrue(outcome["requires_user_image"])

    def test_explicit_image_pull_invokes_managed_agent_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            python = root / ".venv-agent" / "bin" / "python"
            python.parent.mkdir(parents=True)
            python.write_text("fixture")
            calls = []
            def run(argv, **kwargs):
                calls.append(argv)
                return SimpleNamespace(returncode=0)
            with patch("installer.vm_containers.check_container_runtime"), \
                 patch("installer.vm_containers.subprocess.run", side_effect=run):
                pull_prebuilt(root, runtime="podman", profile="wine")
            self.assertEqual(len(calls), 2)
            self.assertIn("qemu", calls[0])
            self.assertIn("toolbox", calls[1])
            self.assertIn("wine", calls[1])
            self.assertNotIn("--privileged", str(calls))


if __name__ == "__main__":
    unittest.main()
