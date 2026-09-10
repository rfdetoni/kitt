from __future__ import annotations

import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from installer.catalog import CatalogError, EcosystemCatalog, Resolution
from installer.cli import _env_flag, _quiet_install_output, build_parser
from installer.core import EcosystemInstaller, InstallerOptions
from installer.platforms import PlatformAdapter
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

    def test_every_catalog_repository_is_immutably_locked(self) -> None:
        sha_re = re.compile(r"^[0-9a-f]{40}$")
        repositories = {module.repository for module in self.catalog.modules.values()}
        self.assertEqual(repositories, set(self.catalog.locks))
        self.assertTrue(all(sha_re.fullmatch(sha) for sha in self.catalog.locks.values()))

    def test_unknown_module_fails_closed(self) -> None:
        with self.assertRaises(CatalogError):
            self.catalog.resolve(["not-a-kitt-module"])


class InstallerCliTests(unittest.TestCase):
    def test_verbose_is_opt_in(self) -> None:
        parser = build_parser()
        self.assertFalse(parser.parse_args([]).verbose)
        self.assertTrue(parser.parse_args(["--verbose"]).verbose)
        self.assertTrue(parser.parse_args(["-v"]).verbose)

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


class InstallerUiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = EcosystemCatalog.load(ROOT)

    def test_recommended_selection_starts_on_agent_cli(self) -> None:
        state = _SelectionState.create(self.catalog)
        self.assertEqual(state.ordered_direct(), ("agent-cli",))
        self.assertEqual(set(state.resolution.ids), set(self.catalog.modules))
        self.assertEqual(state.current_id, "agent-cli")

    def test_space_toggles_current_module(self) -> None:
        state = _SelectionState.create(self.catalog, ("protocol",))
        self.assertIn("protocol", state.direct)
        self.assertIsNone(_handle_key(state, "space"))
        self.assertNotIn("protocol", state.direct)
        self.assertIsNone(_handle_key(state, "space"))
        self.assertIn("protocol", state.direct)

    def test_arrow_keys_move_cursor_and_wrap(self) -> None:
        state = _SelectionState.create(self.catalog, ("agent-cli",))
        first = state.cursor
        self.assertIsNone(_handle_key(state, "up"))
        self.assertEqual(state.cursor, (first - 1) % len(state.ordered_ids))
        self.assertIsNone(_handle_key(state, "down"))
        self.assertEqual(state.cursor, first)

    def test_automatic_dependency_can_be_promoted_to_explicit_selection(self) -> None:
        state = _SelectionState.create(self.catalog, ("agent-cli",))
        automatic_id = next(
            module_id
            for module_id in state.resolution.ids
            if module_id != "agent-cli" and module_id not in state.direct
        )
        state.cursor = state.ordered_ids.index(automatic_id)
        self.assertIsNone(_handle_key(state, "space"))
        self.assertIn(automatic_id, state.direct)
        self.assertIn("explicit", state.message.lower())

    def test_promoted_dependency_survives_parent_removal(self) -> None:
        state = _SelectionState.create(self.catalog, ("agent-cli",))
        promoted = next(
            module_id
            for module_id in state.resolution.ids
            if module_id != "agent-cli" and module_id not in state.direct
        )
        state.cursor = state.ordered_ids.index(promoted)
        _handle_key(state, "space")
        state.cursor = state.ordered_ids.index("agent-cli")
        _handle_key(state, "space")
        self.assertNotIn("agent-cli", state.direct)
        self.assertIn(promoted, state.direct)
        self.assertIn(promoted, state.resolution.ids)

    def test_none_prevents_enter_from_installing(self) -> None:
        state = _SelectionState.create(self.catalog)
        self.assertIsNone(_handle_key(state, "n"))
        self.assertEqual(state.direct, set())
        self.assertIsNone(_handle_key(state, "enter"))
        self.assertIn("select at least one", state.message.lower())

    def test_enter_confirms_non_empty_selection(self) -> None:
        state = _SelectionState.create(self.catalog, ("protocol",))
        self.assertEqual(_handle_key(state, "enter"), "install")

    def test_shortcuts_select_all_and_restore_recommended(self) -> None:
        state = _SelectionState.create(self.catalog, ("protocol",))
        _handle_key(state, "a")
        self.assertEqual(state.direct, set(state.ordered_ids))
        _handle_key(state, "r")
        self.assertEqual(state.ordered_direct(), ("agent-cli",))


class PlatformTests(unittest.TestCase):
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
    def test_requirement_parser(self) -> None:
        self.assertEqual(EcosystemInstaller._parse_requirement("python>=3.12"), ("python", (3, 12)))
        self.assertEqual(EcosystemInstaller._parse_requirement("git"), ("git", ()))


class RepositoryStateTests(unittest.TestCase):
    def test_only_generated_cargo_lock_does_not_block_update(self) -> None:
        self.assertFalse(EcosystemInstaller._has_blocking_toolbox_changes("?? Cargo.lock\n"))
        self.assertTrue(
            EcosystemInstaller._has_blocking_toolbox_changes("?? Cargo.lock\n M src/lib.rs\n")
        )
        self.assertTrue(EcosystemInstaller._has_blocking_toolbox_changes(" M Cargo.lock\n"))

    def test_cargo_build_removes_lock_it_generated_on_failure(self) -> None:
        installer = object.__new__(EcosystemInstaller)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)

            def build(*args, **kwargs):
                (path / "Cargo.lock").write_text("generated", encoding="utf-8")
                raise RuntimeError("build failed")

            with (
                patch.object(installer, "_run", side_effect=build),
                self.assertRaisesRegex(RuntimeError, "build failed"),
            ):
                installer._cargo_build(path)

            self.assertFalse((path / "Cargo.lock").exists())


class LauncherTests(unittest.TestCase):
    def test_agent_launcher_uses_stable_venv_python_path(self) -> None:
        catalog = EcosystemCatalog.load(ROOT)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            bin_dir = root / "bin"
            venv = root / ".venv-agent"
            python = venv / "bin" / "python"
            python.parent.mkdir(parents=True)
            python.touch()
            installer = EcosystemInstaller(
                catalog,
                PlatformAdapter("linux", posix=True),
                InstallerOptions(root=root, bin_dir=bin_dir),
            )
            resolution = Resolution(
                requested=("agent-cli",),
                modules=(catalog.modules["agent-cli"],),
                auto_selected_by={},
            )

            installer._install_launchers(resolution, venv)

            launcher = (bin_dir / "kitt").read_text(encoding="utf-8")
            self.assertIn(f"exec '{python}' '-m' 'kitt.cli.main'", launcher)


if __name__ == "__main__":
    unittest.main()
