import sys
import unittest
from unittest.mock import patch

from installer.cli import build_parser
from installer.vm_lab import VMLabPrerequisiteError, check_vm_lab


class VMLabInstallerTests(unittest.TestCase):
    def test_flag_explicit_and_not_default(self):
        parser = build_parser()
        self.assertFalse(parser.parse_args(["--preset", "agent"]).with_vm_lab)
        self.assertTrue(parser.parse_args(["--preset", "agent", "--with-vm-lab"]).with_vm_lab)

    def test_refuses_unsupported_host_or_missing_binaries(self):
        with patch("installer.vm_lab.sys.platform", "win32"):
            with self.assertRaises(VMLabPrerequisiteError):
                check_vm_lab()
        with patch("installer.vm_lab.sys.platform", "linux"), \
             patch("installer.vm_lab.shutil.which", return_value=None):
            with self.assertRaises(VMLabPrerequisiteError):
                check_vm_lab()

    def test_read_only_preflight(self):
        with patch("installer.vm_lab.sys.platform", "linux"), \
             patch("installer.vm_lab.shutil.which", return_value="/usr/bin/fake"), \
             patch("installer.vm_lab.os.access", return_value=False):
            value = check_vm_lab()
        self.assertTrue(value["ready"])
        self.assertFalse(value["kvm"])
        self.assertTrue(value["guest_image_required"])


if __name__ == "__main__":
    unittest.main()
