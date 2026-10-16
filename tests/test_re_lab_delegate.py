"""Installer routes managed RE lab setup only through installed Agent."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from installer import re_lab_delegate as delegate
from installer.re_lab import ReLabError


class ReLabDelegateTests(unittest.TestCase):
    def test_requires_explicit_license_and_yes(self):
        with tempfile.TemporaryDirectory() as location:
            root = Path(location)
            with patch.object(delegate, "check_re_lab"):
                for yes, license in [(False, False), (True, False), (False, True)]:
                    with self.assertRaisesRegex(ReLabError, "--yes and --accept-windows-license"):
                        delegate.provision_with_agent(root, runtime="docker", profile="full",
                            windows="dockurr", version="11", yes=yes, accept_license=license)

    def test_uses_agent_canonical_entrypoint(self):
        with tempfile.TemporaryDirectory() as location:
            root = Path(location)
            python = root / ".venv-agent" / "bin" / "python"
            python.parent.mkdir(parents=True)
            python.touch()
            seen = []
            def run(args, **kwargs):
                seen.append(args)
                self.assertIn("--state-root", args)
                self.assertIn(str(root / "re-lab"), args)
                self.assertEqual(args[3:6], ["re", "lab", "setup"])
                return SimpleNamespace(returncode=0, stdout=json.dumps({
                    "status": "PROVISIONING", "oracle_ready": False}), stderr="")
            with patch.object(delegate, "check_re_lab"), patch.object(delegate.subprocess, "run", side_effect=run):
                report = delegate.provision_with_agent(root, runtime="docker",
                    profile="full", windows="dockurr", version="11",
                    yes=True, accept_license=True)
            self.assertFalse(report["oracle_ready"])
            self.assertEqual(len(seen), 1)

    def test_failed_child_never_claims_ready(self):
        with tempfile.TemporaryDirectory() as location:
            root = Path(location)
            python = root / ".venv-agent" / "bin" / "python"
            python.parent.mkdir(parents=True)
            python.touch()
            error = SimpleNamespace(returncode=2, stdout="", stderr="sensitive")
            with patch.object(delegate, "check_re_lab"), patch.object(delegate.subprocess, "run", return_value=error):
                with self.assertRaisesRegex(ReLabError, "did not succeed"):
                    delegate.provision_with_agent(root, runtime="docker",
                        profile="full", windows="dockurr", version="11",
                        yes=True, accept_license=True)
