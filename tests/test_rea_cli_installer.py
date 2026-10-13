"""REA full-preset boundary tests: runtime validation and owned launchers."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import tempfile
from unittest.mock import patch

from installer.cli import build_parser, main
from installer.rea_cli import (
    REA_VERSION, ReaInstallError, _supported_node, install_rea, remove_rea_launcher,
)


def test_full_preset_has_explicit_override_flags():
    parser = build_parser()
    assert parser.parse_args(["--preset", "full"]).skip_rea is False
    assert parser.parse_args(["--preset", "full", "--skip-rea"]).skip_rea
    assert parser.parse_args(["--preset", "agent", "--with-rea"]).with_rea


def test_rea_node_engine_range_matches_upstream():
    for version in ("v22.19.0", "v22.20.1", "v24.11.0", "v24.13.0", "v26.0.0"):
        assert _supported_node(version)
    for version in ("v20.19.0", "v22.18.0", "v23.9.0", "v24.10.0", "v25.0.0", "not-a-version"):
        assert not _supported_node(version)


def test_rea_pinned_npm_install_and_idempotent_cleanup():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "managed"
        bin_dir = Path(tmp) / "bin"
        calls = []

        def fake_run(argv, **kwargs):
            calls.append(argv)
            if argv == ["/usr/local/bin/node", "--version"]:
                return SimpleNamespace(returncode=0, stdout="v24.11.0\n")
            if argv[:2] == ["/usr/local/bin/npm", "install"]:
                executable = root / "rea" / "bin" / "rea"
                executable.parent.mkdir(parents=True, exist_ok=True)
                executable.write_text("test executable")
                return SimpleNamespace(returncode=0)
            if argv[-1] == "--version":
                return SimpleNamespace(returncode=0, stdout="6.4.0\n")
            raise AssertionError("Unexpected process: " + str(argv))

        def which(program):
            return {"node": "/usr/local/bin/node", "npm": "/usr/local/bin/npm"}.get(program)

        with patch("installer.rea_cli.shutil.which", side_effect=which), \
             patch("installer.rea_cli.subprocess.run", side_effect=fake_run):
            installed = install_rea(root, bin_dir)
            second = install_rea(root, bin_dir)
        assert installed["installed"] and second["installed"]
        assert any("rea-agents@" + REA_VERSION in line for line in calls)
        assert not any("--prefix=" in value for line in calls for value in line)
        assert len([line for line in calls if len(line) > 1 and line[1] == "install"]) == 1
        assert (bin_dir / "rea").is_symlink()
        remove_rea_launcher(root, bin_dir)
        assert not (bin_dir / "rea").exists()
        assert (root / "rea" / "bin" / "rea").exists()


def test_unrelated_rea_is_preserved_and_bad_node_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "managed"
        bin_dir = Path(tmp) / "bin"
        bin_dir.mkdir()
        own = bin_dir / "rea"
        own.write_text("user-managed REA")
        with patch("installer.rea_cli.shutil.which", return_value="/usr/bin/node"), \
             patch("installer.rea_cli.subprocess.run", return_value=SimpleNamespace(
                 returncode=0, stdout="v20.0.0\n")):
            try:
                install_rea(root, bin_dir)
                assert False, "Node 20 should fail"
            except ReaInstallError:
                pass
        remove_rea_launcher(root, bin_dir)
        assert own.read_text() == "user-managed REA"


def test_dry_run_has_no_side_effects_or_network_access():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "managed"
        bin_dir = Path(tmp) / "bin"
        with patch("installer.rea_cli.subprocess.run") as proc:
            result = install_rea(root, bin_dir, dry_run=True)
        assert result["planned"]
        assert not root.exists()
        proc.assert_not_called()


def test_explicit_rea_failure_is_nonzero_after_core_install():
    with tempfile.TemporaryDirectory() as tmp:
        args = ["--preset", "agent", "--minimal", "--with-rea", "--yes", "--verbose",
                "--root", str(Path(tmp) / "root"), "--bin-dir", str(Path(tmp) / "bin")]
        with patch("installer.cli.SourceFreeEcosystemInstaller") as installer, \
             patch("installer.cli._record_source_ref"), \
             patch("installer.cli._ensure_launcher_priority"), \
             patch("installer.rea_cli.install_rea", side_effect=ReaInstallError("Node missing")):
            status = main(args)
        assert status == 1
        installer.return_value.install.assert_called_once()


def test_explicit_vm_image_pull_failure_is_nonzero_after_core_install():
    from installer.vm_containers import VMContainerError

    with tempfile.TemporaryDirectory() as tmp:
        args = ["--preset", "agent", "--minimal", "--with-vm-containers",
                "--vm-pull-images", "--yes", "--verbose",
                "--root", str(Path(tmp) / "root"), "--bin-dir", str(Path(tmp) / "bin")]
        with patch("installer.cli.SourceFreeEcosystemInstaller") as installer, \
             patch("installer.cli._record_source_ref"), \
             patch("installer.cli._ensure_launcher_priority"), \
             patch("installer.vm_containers.check_container_runtime", return_value={}), \
             patch("installer.vm_containers.pull_prebuilt",
                   side_effect=VMContainerError("image unavailable")):
            status = main(args)
        assert status == 1
        installer.return_value.install.assert_called_once()
