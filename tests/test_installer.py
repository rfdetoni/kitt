from __future__ import annotations

import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from installer.catalog import CatalogError, EcosystemCatalog, Resolution
from installer.cli import _env_flag, _quiet_install_output, build_parser, main
from installer.core import EcosystemInstaller, InstallerError, InstallerOptions
from installer.platforms import PlatformAdapter
from installer.release_manifest import load_release_refs
from installer.ui import _SelectionState, _handle_key


ROOT = Path(__file__).resolve().parents[1]


class CatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = EcosystemCatalog.load(ROOT)

    def test_agent_cli_resolves_every_integrated_ecosystem_module(self) -> None:
        resolution = self.catalog.resolve(["agent-cli"])
        self.assertEqual(set(resolution.ids), set(self.catalog.modules))
        self.assertEqual(resolution.requested, ("agent-cli",))
        for module_id in set(self.catalog.modules) - {"agent-cli"}:
            self.assertIn(module_id, resolution.ids)

    def test_minimal_agent_and_proxy_resolve_only_strict_dependencies(self) -> None:
        resolution = self.catalog.resolve(
            ("agent-cli", "reverse-proxy"),
            include_companions=False,
        )
        self.assertEqual(
            set(resolution.ids),
            {"protocol", "memory", "agent-cli", "reverse-proxy"},
        )
        self.assertNotIn("assistant", resolution.ids)
        self.assertIn("memory", resolution.ids)
        self.assertNotIn("toolbox", resolution.ids)
        self.assertNotIn("ai-workers", resolution.ids)

    def test_agent_proxy_minimal_preset_is_explicit(self) -> None:
        requested = self.catalog.preset("agent-proxy-minimal")
        self.assertEqual(requested, ("agent-cli", "reverse-proxy"))
        resolution = self.catalog.resolve(requested, include_companions=False)
        self.assertEqual(
            set(resolution.ids),
            {"protocol", "memory", "agent-cli", "reverse-proxy"},
        )

    def test_agent_preset_has_same_complete_closure(self) -> None:
        requested = self.catalog.preset("agent")
        self.assertEqual(requested, ("agent-cli",))
        self.assertEqual(
            set(self.catalog.resolve(requested).ids),
            set(self.catalog.modules),
        )

    def test_assistant_pulls_shared_protocol_and_memory(self) -> None:
        ids = set(self.catalog.resolve(["assistant"]).ids)
        self.assertTrue({"assistant", "protocol", "memory"} <= ids)

    def test_every_catalog_repository_defaults_to_main(self) -> None:
        self.assertTrue(
            all(
                self.catalog.resolve_ref(module) == "main"
                for module in self.catalog.modules.values()
            )
        )

    def test_release_manifest_pins_every_component_to_sha(self) -> None:
        refs = load_release_refs(ROOT, self.catalog)
        self.assertEqual(set(refs), set(self.catalog.modules))
        for module_id, ref in refs.items():
            self.assertRegex(ref, r"^[0-9a-f]{40}$")
            self.assertEqual(
                self.catalog.resolve_ref(
                    self.catalog.modules[module_id], component_refs=refs
                ),
                ref,
            )

    def test_unknown_module_fails_closed(self) -> None:
        with self.assertRaises(CatalogError):
            self.catalog.resolve(["not-a-kitt-module"])

    def test_internal_dependency_cannot_be_selected_directly(self) -> None:
        for module_id in ("protocol", "memory"):
            with self.subTest(module_id=module_id), self.assertRaises(CatalogError):
                self.catalog.resolve([module_id])

    def test_full_preset_explicitly_selects_every_public_module(self) -> None:
        requested = self.catalog.preset("full")
        expected_public = tuple(
            module.id
            for module in sorted(
                self.catalog.modules.values(),
                key=lambda module: (module.order, module.id),
            )
            if module.selectable
        )
        self.assertEqual(set(requested), set(expected_public))
        self.assertEqual(
            set(self.catalog.resolve(requested).ids),
            set(self.catalog.modules),
        )


class InstallerCliTests(unittest.TestCase):
    def test_verbose_is_opt_in(self) -> None:
        parser = build_parser()
        self.assertFalse(parser.parse_args([]).verbose)
        self.assertTrue(parser.parse_args(["--verbose"]).verbose)
        self.assertTrue(parser.parse_args(["-v"]).verbose)

    def test_minimal_flag_is_opt_in(self) -> None:
        parser = build_parser()
        self.assertFalse(parser.parse_args([]).minimal)
        self.assertTrue(parser.parse_args(["--minimal"]).minimal)

    def test_main_is_default_ref(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("KITT_REF", None)
            parser = build_parser()
            self.assertEqual(parser.parse_args([]).ref, "main")
            self.assertEqual(parser.parse_args(["--ref", "feature/test"]).ref, "feature/test")

    def test_edge_is_default_channel_and_release_is_explicit(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("KITT_CHANNEL", None)
            parser = build_parser()
            self.assertEqual(parser.parse_args([]).channel, "edge")
            self.assertEqual(
                parser.parse_args(["--channel", "release"]).channel,
                "release",
            )

    def test_environment_flags_accept_common_truthy_values(self) -> None:
        for value in ("1", "true", "TRUE", "yes", "on"):
            with self.subTest(value=value), patch.dict(os.environ, {"KITT_TEST_FLAG": value}):
                self.assertTrue(_env_flag("KITT_TEST_FLAG"))
        with patch.dict(os.environ, {"KITT_TEST_FLAG": "0"}):
            self.assertFalse(_env_flag("KITT_TEST_FLAG"))

    def test_quiet_mode_redirects_process_stdout_and_stderr(self) -> None:
        with _quiet_install_output() as path:
            os.write(1, b"hidden stdout\n")
            os.write(2, b"hidden stderr\n")
        try:
            captured = path.read_text(encoding="utf-8")
            self.assertIn("hidden stdout", captured)
            self.assertIn("hidden stderr", captured)
        finally:
            path.unlink(missing_ok=True)


    def test_requested_rea_install_failure_returns_nonzero(self) -> None:
        from installer.rea_cli import ReaInstallError

        with tempfile.TemporaryDirectory() as tmp:
            args = ["--preset", "agent", "--minimal", "--with-rea", "--yes", "--verbose",
                    "--root", str(Path(tmp) / "root"), "--bin-dir", str(Path(tmp) / "bin")]
            with patch("installer.cli.SourceFreeEcosystemInstaller") as installer, \
                 patch("installer.cli._record_source_ref"), \
                 patch("installer.cli._ensure_launcher_priority"), \
                 patch("installer.rea_cli.install_rea", side_effect=ReaInstallError("Node missing")):
                status = main(args)
            self.assertEqual(status, 1)
            installer.return_value.install.assert_called_once()

    def test_requested_vm_image_failure_returns_nonzero(self) -> None:
        from installer.vm_containers import VMContainerError

        with tempfile.TemporaryDirectory() as tmp:
            args = ["--preset", "agent", "--minimal", "--with-vm-containers",
                    "--vm-pull-images", "--yes", "--verbose",
                    "--root", str(Path(tmp) / "root"), "--bin-dir", str(Path(tmp) / "bin")]
            with patch("installer.cli.SourceFreeEcosystemInstaller") as installer, \
                 patch("installer.cli._record_source_ref"), \
                 patch("installer.cli._ensure_launcher_priority"), \
                 patch("installer.vm_containers.check_container_runtime", return_value={"runtime": "docker"}), \
                 patch("installer.vm_containers.pull_prebuilt",
                       side_effect=VMContainerError("image unavailable")):
                status = main(args)
            self.assertEqual(status, 1)
            installer.return_value.install.assert_called_once()


class InstallerUiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = EcosystemCatalog.load(ROOT)

    def test_recommended_selection_starts_on_agent_cli(self) -> None:
        state = _SelectionState.create(self.catalog)
        self.assertEqual(state.ordered_direct(), ("agent-cli",))
        self.assertEqual(set(state.resolution.ids), set(self.catalog.modules))
        self.assertEqual(state.current_id, "agent-cli")

    def test_space_toggles_current_public_module(self) -> None:
        state = _SelectionState.create(self.catalog, ("assistant",))
        self.assertIn("assistant", state.direct)
        self.assertIsNone(_handle_key(state, "space"))
        self.assertNotIn("assistant", state.direct)
        self.assertIsNone(_handle_key(state, "space"))
        self.assertIn("assistant", state.direct)

    def test_internal_dependency_cannot_be_promoted_in_ui(self) -> None:
        state = _SelectionState.create(self.catalog, ("agent-cli",))
        state.cursor = state.ordered_ids.index("protocol")
        self.assertIsNone(_handle_key(state, "space"))
        self.assertNotIn("protocol", state.direct)
        self.assertIn("internal dependency", state.message.lower())

    def test_arrow_keys_move_cursor_and_wrap(self) -> None:
        state = _SelectionState.create(self.catalog, ("agent-cli",))
        first = state.cursor
        self.assertIsNone(_handle_key(state, "up"))
        self.assertEqual(state.cursor, (first - 1) % len(state.ordered_ids))
        self.assertIsNone(_handle_key(state, "down"))
        self.assertEqual(state.cursor, first)

    def test_selectable_automatic_companion_can_be_promoted(self) -> None:
        state = _SelectionState.create(self.catalog, ("agent-cli",))
        automatic_id = next(
            module_id
            for module_id in state.resolution.ids
            if module_id != "agent-cli"
            and module_id not in state.direct
            and self.catalog.modules[module_id].selectable
        )
        state.cursor = state.ordered_ids.index(automatic_id)
        self.assertIsNone(_handle_key(state, "space"))
        self.assertIn(automatic_id, state.direct)
        self.assertIn("explicit", state.message.lower())

    def test_none_prevents_enter_from_installing(self) -> None:
        state = _SelectionState.create(self.catalog)
        self.assertIsNone(_handle_key(state, "n"))
        self.assertEqual(state.direct, set())
        self.assertIsNone(_handle_key(state, "enter"))
        self.assertIn("select at least one", state.message.lower())

    def test_enter_confirms_non_empty_selection(self) -> None:
        state = _SelectionState.create(self.catalog, ("assistant",))
        self.assertEqual(_handle_key(state, "enter"), "install")

    def test_shortcuts_select_all_public_modules_and_restore_recommended(self) -> None:
        state = _SelectionState.create(self.catalog, ("assistant",))
        _handle_key(state, "a")
        self.assertEqual(
            state.direct,
            {
                module_id
                for module_id in state.ordered_ids
                if self.catalog.modules[module_id].selectable
            },
        )
        self.assertNotIn("protocol", state.direct)
        self.assertNotIn("memory", state.direct)
        _handle_key(state, "r")
        self.assertEqual(state.ordered_direct(), ("agent-cli",))


class PlatformTests(unittest.TestCase):
    def test_unusable_command_wrapper_is_not_reported_as_found(self) -> None:
        adapter = PlatformAdapter("linux", posix=True)
        with (
            patch("installer.platforms.shutil.which", return_value="/usr/bin/cargo"),
            patch("installer.platforms._run_capture", return_value=(1, "rustup has no default toolchain")),
        ):
            self.assertIsNone(adapter.command_info("cargo"))

    def test_rustup_target_matches_supported_platform_architecture(self) -> None:
        with patch("installer.platforms.stdlib_platform.machine", return_value="x86_64"):
            self.assertEqual(
                PlatformAdapter("linux", posix=True)._rustup_target(),
                "x86_64-unknown-linux-gnu",
            )
            self.assertEqual(
                PlatformAdapter("macos", posix=True)._rustup_target(),
                "x86_64-apple-darwin",
            )
            self.assertEqual(
                PlatformAdapter("windows", posix=False)._rustup_target(),
                "x86_64-pc-windows-msvc",
            )

    def test_linux_voice_build_requires_pkg_config_and_alsa(self) -> None:
        adapter = PlatformAdapter("linux", posix=True)
        with patch("installer.platforms.shutil.which", return_value=None):
            self.assertFalse(adapter.assistant_voice_build_available())
        with (
            patch("installer.platforms.shutil.which", return_value="/usr/bin/pkg-config"),
            patch("installer.platforms._run_capture", return_value=(1, "")),
        ):
            self.assertFalse(adapter.assistant_voice_build_available())
        with (
            patch("installer.platforms.shutil.which", return_value="/usr/bin/pkg-config"),
            patch("installer.platforms._run_capture", return_value=(0, "")),
        ):
            self.assertTrue(adapter.assistant_voice_build_available())

    def test_non_linux_voice_build_has_no_alsa_probe(self) -> None:
        self.assertTrue(PlatformAdapter("windows", posix=False).assistant_voice_build_available())
        self.assertTrue(PlatformAdapter("macos", posix=True).assistant_voice_build_available())

    def test_generic_posix_adapter_accepts_posix_modules(self) -> None:
        adapter = PlatformAdapter("haiku", posix=True)
        self.assertTrue(adapter.supports(("windows", "linux", "macos", "posix")))

    def test_posix_launcher_is_portable_sh(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = PlatformAdapter("linux", posix=True).write_launcher(
                Path(temp), "kitt-test", ["/tmp/program", "fixed arg"]
            )
            content = path.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("#!/bin/sh\n"))
            self.assertIn('"$@"', content)

    def test_windows_launcher_is_cmd(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = PlatformAdapter("windows", posix=False).write_launcher(
                Path(temp), "kitt-test", [r"C:\KITT\tool.exe"]
            )
            self.assertEqual(path.suffix, ".cmd")
            self.assertIn("%*", path.read_text(encoding="ascii"))

    def test_python_selection_falls_back_when_newer_python_lacks_venv(self) -> None:
        adapter = PlatformAdapter("linux", posix=True)
        with (
            patch.object(adapter, "_python_candidates", return_value=[("python3.14",), ("python3.13",)]),
            patch("installer.platforms._run_capture", side_effect=[(0, "3.14.4"), (0, "3.13.9")]),
            patch.object(adapter, "_python_supports_venv", side_effect=[False, True]),
        ):
            info = adapter.find_python((3, 12))
        self.assertIsNotNone(info)
        assert info is not None
        self.assertEqual(info.argv, ("python3.13",))
        self.assertEqual(info.version[:2], (3, 13))
        self.assertIsNotNone(adapter._python_without_venv)
        assert adapter._python_without_venv is not None
        self.assertEqual(adapter._python_without_venv.version[:2], (3, 14))

    def test_missing_venv_produces_actionable_linux_hint(self) -> None:
        adapter = PlatformAdapter("linux", posix=True)
        with (
            patch.object(adapter, "_python_candidates", return_value=[("python3.14",)]),
            patch("installer.platforms._run_capture", return_value=(0, "3.14.4")),
            patch.object(adapter, "_python_supports_venv", return_value=False),
        ):
            info = adapter.find_python((3, 12))
        self.assertIsNone(info)
        hint = adapter.prerequisite_hint(("python",))
        self.assertIn("python3.14-venv", hint)
        self.assertIn("venv/ensurepip", hint)


class RequirementTests(unittest.TestCase):
    def test_prerequisite_report_keeps_highest_rust_requirement(self) -> None:
        catalog = EcosystemCatalog.load(ROOT)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installer = EcosystemInstaller(
                catalog,
                PlatformAdapter("linux", posix=True),
                InstallerOptions(root=root, bin_dir=root / "bin"),
            )
            with (
                patch.object(installer.platform, "find_python", return_value=None),
                patch.object(installer.platform, "command_info", return_value=None),
            ):
                report = installer._check_prerequisites(
                    (catalog.modules["memory"], catalog.modules["toolbox"])
                )
            self.assertIn("rust>=1.90", report.missing)
            self.assertNotIn("rust>=1.85", report.missing)

    def test_linux_native_build_fails_early_without_c_compiler(self) -> None:
        catalog = EcosystemCatalog.load(ROOT)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            adapter = PlatformAdapter("linux", posix=True)
            for portable, expected in ((False, True), (True, False)):
                installer = EcosystemInstaller(
                    catalog,
                    adapter,
                    InstallerOptions(root=root, bin_dir=root / "bin", portable=portable),
                )
                with (
                    patch.object(adapter, "find_python", return_value=None),
                    patch.object(adapter, "command_info", return_value=None),
                ):
                    report = installer._check_prerequisites((catalog.modules["assistant"],))
                self.assertEqual("cc" in report.missing, expected)
            self.assertIn("build-essential", adapter.prerequisite_hint(("cc",)))

    def test_missing_rust_minimum_uses_highest_required_version(self) -> None:
        self.assertEqual(
            EcosystemInstaller._missing_rust_minimum(("git", "rust>=1.88", "rust>=1.90")),
            (1, 90),
        )
        self.assertEqual(EcosystemInstaller._missing_rust_minimum(("rust",)), (1, 85))
        self.assertIsNone(EcosystemInstaller._missing_rust_minimum(("git", "node")))

    def test_noninteractive_auto_prerequisite_retry_clears_rust_failure(self) -> None:
        catalog = EcosystemCatalog.load(ROOT)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            adapter = PlatformAdapter("linux", posix=True)
            installer = EcosystemInstaller(
                catalog,
                adapter,
                InstallerOptions(
                    root=root,
                    bin_dir=root / "bin",
                    auto_prerequisites=True,
                ),
            )
            reports = [
                type("Report", (), {
                    "python": None,
                    "missing": ("rust>=1.90",),
                    "found": {},
                })(),
                type("Report", (), {
                    "python": None,
                    "missing": (),
                    "found": {"cargo": "cargo 1.90", "rustc": "rustc 1.90"},
                })(),
            ]
            with (
                patch.object(installer, "_check_prerequisites", side_effect=reports),
                patch.object(adapter, "install_rust") as install_rust,
            ):
                install_rust.return_value = type(
                    "Info", (), {"version_text": "rustc 1.90.0"}
                )()
                report = installer._prepare_prerequisites(
                    (catalog.modules["toolbox"],)
                )
            install_rust.assert_called_once_with((1, 90))
            self.assertEqual(report.missing, ())

    def test_requirement_parser(self) -> None:
        self.assertEqual(EcosystemInstaller._parse_requirement("python>=3.12"), ("python", (3, 12)))
        self.assertEqual(EcosystemInstaller._parse_requirement("git"), ("git", ()))


class NativeBuildTests(unittest.TestCase):
    def test_assistant_falls_back_to_no_default_features_without_alsa(self) -> None:
        catalog = EcosystemCatalog.load(ROOT)
        module = catalog.modules["assistant"]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / ".staging" / "sources" / "kitt-assistant"
            source.mkdir(parents=True)
            (source / "Cargo.toml").write_text("[workspace]\n", encoding="utf-8")
            installer = __import__(
                "installer.source_free",
                fromlist=["SourceFreeEcosystemInstaller"],
            ).SourceFreeEcosystemInstaller(
                catalog,
                PlatformAdapter("linux", posix=True),
                InstallerOptions(root=root, bin_dir=root / "bin"),
            )
            with (
                patch.object(installer.platform, "assistant_voice_build_available", return_value=False),
                patch.object(installer, "_run") as run,
            ):
                installer._cargo_build_cached(module)
            argv = run.call_args.args[0]
            self.assertIn("--no-default-features", argv)

    def test_assistant_keeps_voice_features_when_native_audio_is_available(self) -> None:
        catalog = EcosystemCatalog.load(ROOT)
        module = catalog.modules["assistant"]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / ".staging" / "sources" / "kitt-assistant"
            source.mkdir(parents=True)
            (source / "Cargo.toml").write_text("[workspace]\n", encoding="utf-8")
            installer = __import__(
                "installer.source_free",
                fromlist=["SourceFreeEcosystemInstaller"],
            ).SourceFreeEcosystemInstaller(
                catalog,
                PlatformAdapter("linux", posix=True),
                InstallerOptions(root=root, bin_dir=root / "bin"),
            )
            with (
                patch.object(installer.platform, "assistant_voice_build_available", return_value=True),
                patch.object(installer, "_run") as run,
            ):
                installer._cargo_build_cached(module)
            argv = run.call_args.args[0]
            self.assertNotIn("--no-default-features", argv)


    def test_release_assistant_rejects_lock_mismatch_before_build(self) -> None:
        catalog = EcosystemCatalog.load(ROOT)
        module = catalog.modules["assistant"]
        refs = load_release_refs(ROOT, catalog)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / ".staging" / "sources" / "kitt-assistant"
            source.mkdir(parents=True)
            (source / "Cargo.toml").write_text("[workspace]\n", encoding="utf-8")
            (source / "Cargo.lock").write_text(
                """version = 4

[[package]]
name = "kitt-protocol"
version = "0.0.0"
source = "git+https://github.com/rfdetoni/kitt-protocol.git#0000000000000000000000000000000000000000"

[[package]]
name = "kitt-memory-core"
version = "0.0.0"
source = "git+https://github.com/rfdetoni/kitt-memory.git#0000000000000000000000000000000000000000"

[[package]]
name = "kitt-memory-sqlite"
version = "0.0.0"
source = "git+https://github.com/rfdetoni/kitt-memory.git#0000000000000000000000000000000000000000"
""",
                encoding="utf-8",
            )
            installer = __import__(
                "installer.source_free",
                fromlist=["SourceFreeEcosystemInstaller"],
            ).SourceFreeEcosystemInstaller(
                catalog,
                PlatformAdapter("linux", posix=True),
                InstallerOptions(
                    root=root,
                    bin_dir=root / "bin",
                    component_refs=refs,
                ),
            )
            with patch.object(installer, "_run") as run:
                with self.assertRaisesRegex(
                    InstallerError,
                    "Assistant Cargo.lock does not match release pins",
                ):
                    installer._cargo_build_cached(module)
            run.assert_not_called()


class RepositoryStateTests(unittest.TestCase):
    def test_success_cleanup_removes_only_known_generated_artifacts(self) -> None:
        catalog = EcosystemCatalog.load(ROOT)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installer = EcosystemInstaller(
                catalog,
                PlatformAdapter("linux", posix=True),
                InstallerOptions(root=root, bin_dir=root / "bin"),
            )
            resolution = catalog.resolve(("agent-cli",))
            generated = root / "kitt-protocol" / "sdk/python/build"
            generated.mkdir(parents=True)
            unrelated = root / "kitt-protocol" / "notes.txt"
            unrelated.write_text("keep", encoding="utf-8")

            installer._cleanup_generated_artifacts(resolution)

            self.assertFalse(generated.exists())
            self.assertTrue(unrelated.exists())






class ReLabProvisioningTests(unittest.TestCase):
    def test_cli_accepts_full_dockur_lab_options(self) -> None:
        args = build_parser().parse_args([
            "--preset", "full", "--channel", "release", "--with-re-lab",
            "--re-runtime", "docker", "--re-profile", "full",
            "--re-windows", "dockurr", "--re-windows-version", "11", "--yes",
        ])
        self.assertTrue(args.with_re_lab)
        self.assertEqual((args.re_runtime, args.re_profile, args.re_windows, args.re_windows_version),
                         ("docker", "full", "dockurr", "11"))

    @unittest.skipUnless(os.name == "posix" and __import__("sys").platform == "linux", "Linux Docker only")
    def test_dockur_defaults_allow_short_login_and_autologin(self) -> None:
        from installer.re_lab import _ensure_windows_settings
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "windows.env"
            _ensure_windows_settings(path)
            content = path.read_text()
            self.assertIn("USERNAME=Docker\n", content)
            self.assertIn("PASSWORD=admin\n", content)
            self.assertIn("AUTOLOGIN=Y\n", content)
            self.assertNotIn("USERNAME=Kitt", content)
            self.assertEqual(path.stat().st_mode & 0o077, 0)
            _ensure_windows_settings(path)
            self.assertEqual(path.read_text(), content)

    @unittest.skipUnless(os.name == "posix" and __import__("sys").platform == "linux", "Linux Docker only")
    def test_preexisting_dockur_disk_without_credentials_is_not_reused(self) -> None:
        from installer.re_lab import ReLabError, provision_re_lab
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            python = root / ".venv-agent" / "bin" / "python"
            python.parent.mkdir(parents=True)
            python.touch()
            (root / "re-lab").mkdir(mode=0o700)
            storage = root / "re-lab" / "windows"
            storage.mkdir(mode=0o700)
            (storage / "data.img").write_bytes(b"existing guest")
            with (
                patch("installer.re_lab.check_re_lab"),
                patch("installer.re_lab._existing_container", return_value=False),
            ):
                with self.assertRaisesRegex(ReLabError, "without KITT first-install credentials"):
                    provision_re_lab(root, runtime="docker", profile="full",
                                     windows="dockurr", version="11")
            self.assertEqual((storage / "data.img").read_bytes(), b"existing guest")

    @unittest.skipUnless(os.name == "posix" and __import__("sys").platform == "linux", "Linux Docker only")
    def test_previous_windows_credentials_never_change_installed_guest(self) -> None:
        from installer.re_lab import ReLabError, provision_re_lab
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            python = root / ".venv-agent" / "bin" / "python"
            python.parent.mkdir(parents=True)
            python.symlink_to(__import__("sys").executable)
            lab = root / "re-lab"
            lab.mkdir(mode=0o700)
            storage = lab / "windows"
            storage.mkdir(mode=0o700)
            (storage / "data.img").write_bytes(b"installed Windows")
            credentials = lab / "windows.env"
            old = "VERSION=11\nUSERNAME=Kitt\nPASSWORD=old-random-password\nAUTOLOGIN=N\n"
            credentials.write_text(old)
            credentials.chmod(0o600)
            with (
                patch("installer.re_lab.check_re_lab"),
                patch("installer.re_lab._existing_container", return_value=True),
                patch("installer.re_lab._run") as run,
            ):
                with self.assertRaisesRegex(ReLabError, "Back up the Windows disk"):
                    provision_re_lab(root, runtime="docker", profile="full",
                                     windows="dockurr", version="11")
            run.assert_not_called()
            self.assertEqual(credentials.read_text(), old)
            self.assertEqual((storage / "data.img").read_bytes(), b"installed Windows")

    @unittest.skipUnless(os.name == "posix" and __import__("sys").platform == "linux", "Linux Docker only")
    def test_previous_settings_are_replaced_only_before_guest_creation(self) -> None:
        from installer.re_lab import _ensure_windows_settings
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "windows.env"
            path.write_text("USERNAME=Kitt\nAUTOLOGIN=N\n")
            path.chmod(0o600)
            _ensure_windows_settings(path, fresh_guest=True)
            self.assertIn("USERNAME=Docker\n", path.read_text())
            self.assertIn("AUTOLOGIN=Y\n", path.read_text())

    @unittest.skipUnless(os.name == "posix" and __import__("sys").platform == "linux", "Linux Docker only")
    def test_fresh_dockur_container_receives_credentials_and_localhost_console(self) -> None:
        from installer.re_lab import provision_re_lab
        from subprocess import CompletedProcess
        calls: list[list[str]] = []

        def fake_run(argv: list[str], **kwargs):
            calls.append(argv)
            if argv[:3] == ["docker", "image", "inspect"]:
                return CompletedProcess(argv, 0, "sha256:" + "a" * 64, "")
            if len(argv) >= 2 and argv[1] == "-c":
                return CompletedProcess(argv, 0, "kitt/linux-re:full-0.86.10\n", "")
            return CompletedProcess(argv, 0, "", "")

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            python = root / ".venv-agent" / "bin" / "python"
            python.parent.mkdir(parents=True)
            python.symlink_to(__import__("sys").executable)
            self.assertTrue(python.is_symlink())
            with (
                patch("installer.re_lab.check_re_lab"),
                patch("installer.re_lab._existing_container", return_value=False),
                patch("installer.re_lab._start_existing"),
                patch("installer.re_lab._run", side_effect=fake_run),
            ):
                result = provision_re_lab(root, runtime="docker", profile="full",
                                          windows="dockurr", version="11")
            creates = [call for call in calls if call[:2] == ["docker", "create"]]
            self.assertEqual(len(creates), 2)
            win = next(call for call in creates if "kitt-re-win11" in call)
            linux = next(call for call in creates if "kitt-re-full" in call)
            self.assertIn("--env-file", win)
            self.assertIn("127.0.0.1:8006:8006", win)
            self.assertIn("/dev/kvm", win)
            self.assertIn("NET_ADMIN", win)
            self.assertIn("none", linux)
            self.assertIn("--cap-drop", linux)
            self.assertEqual(result["windows_user"], "Docker")


    @unittest.skipUnless(os.name == "posix" and __import__("sys").platform == "linux", "Linux virtualenv layout")
    def test_optional_vm_image_pull_accepts_venv_python_symlink(self) -> None:
        from installer.vm_containers import pull_prebuilt
        from subprocess import CompletedProcess
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            python = root / ".venv-agent" / "bin" / "python"
            python.parent.mkdir(parents=True)
            python.symlink_to(__import__("sys").executable)
            calls: list[list[str]] = []
            def run(argv, **kwargs):
                calls.append(argv)
                return CompletedProcess(argv, 0)
            with (
                patch("installer.vm_containers.check_container_runtime"),
                patch("installer.vm_containers.subprocess.run", side_effect=run),
            ):
                pull_prebuilt(root, runtime="docker", profile="full")
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0][:3], [str(python), "-m", "kitt.cli.main"])
            self.assertIn("toolbox", calls[1])


    def test_semantic_help_never_runs_installer(self):
        import io
        from contextlib import redirect_stdout
        from installer.cli import main
        output = io.StringIO()
        with redirect_stdout(output):
            result = main(["--semantic-help"])
        self.assertEqual(result, 0)
        self.assertIn("ollama pull", output.getvalue())
        self.assertIn("No model is downloaded", output.getvalue())


    def test_oracle_bootstrap_cli_is_opt_in_and_requires_destructive_flag(self):
        parser = build_parser()
        default = parser.parse_args(["--preset", "full", "--with-re-lab"])
        self.assertFalse(default.re_oracle_bootstrap)
        self.assertFalse(default.re_oracle_recreate)
        configured = parser.parse_args([
            "--preset", "full", "--with-re-lab", "--re-oracle-bootstrap",
            "--re-oracle-recreate", "--accept-windows-license", "--yes",
        ])
        self.assertTrue(configured.re_oracle_bootstrap)
        self.assertTrue(configured.re_oracle_recreate)
        self.assertTrue(configured.accept_windows_license)

    @unittest.skipUnless(os.name == "posix" and __import__("sys").platform == "linux", "Linux only")
    def test_installer_delegates_oracle_to_pinned_agent_without_recreating_twice(self):
        from installer.re_lab import provision_re_lab, _WINDOWS_SETTINGS
        from subprocess import CompletedProcess
        calls = []
        def run(argv, **kwargs):
            calls.append(argv)
            if len(argv) > 3 and argv[1:3] == ["-m", "kitt.cli.main"]:
                return CompletedProcess(argv, 0, json.dumps({
                    "hosts": "/private/hosts.json", "manifest_sha256": "a" * 64}), "")
            return CompletedProcess(argv, 0, "", "")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            python = root / ".venv-agent" / "bin" / "python"
            python.parent.mkdir(parents=True)
            python.symlink_to(__import__("sys").executable)
            lab = root / "re-lab"
            lab.mkdir(mode=0o700)
            storage = lab / "windows"
            storage.mkdir(mode=0o700)
            credentials = lab / "windows.env"
            credentials.write_text(_WINDOWS_SETTINGS)
            credentials.chmod(0o600)
            with (patch("installer.re_lab.check_re_lab"),
                  patch("installer.re_lab._existing_container", return_value=True),
                  patch("installer.re_lab._start_existing"),
                  patch("installer.re_lab._run", side_effect=run)):
                report = provision_re_lab(root, runtime="docker", profile="full",
                    windows="dockurr", version="11", oracle=True, oracle_recreate=True)
            bootstrap = [arg for arg in calls if "bootstrap" in arg]
            self.assertEqual(len(bootstrap), 1)
            self.assertIn("--recreate", bootstrap[0])
            self.assertIn("--accept-license", bootstrap[0])
            self.assertFalse(any(arg[:2] == ["docker", "create"] for arg in calls))
            self.assertEqual(report["oracle_manifest_sha256"], "a" * 64)

if __name__ == "__main__":
    unittest.main()
