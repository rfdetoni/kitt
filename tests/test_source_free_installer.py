from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from installer.catalog import EcosystemCatalog, Resolution
from installer.core import InstallerOptions
from installer.platforms import CommandInfo, PlatformAdapter
from installer.source_free import SourceFreeEcosystemInstaller


ROOT = Path(__file__).resolve().parents[1]


class SourceFreeInstallerTests(unittest.TestCase):
    def test_default_job_budget_respects_available_memory(self) -> None:
        with (
            patch.dict("installer.source_free.os.environ", {"KITT_INSTALL_JOBS": ""}),
            patch("installer.source_free.os.cpu_count", return_value=16),
            patch.object(
                SourceFreeEcosystemInstaller,
                "_available_memory_bytes",
                return_value=4 * 1024 ** 3,
            ),
        ):
            self.assertEqual(SourceFreeEcosystemInstaller._resolve_jobs(), 2)

    def test_explicit_job_budget_remains_authoritative(self) -> None:
        with (
            patch.dict("installer.source_free.os.environ", {"KITT_INSTALL_JOBS": "7"}),
            patch.object(
                SourceFreeEcosystemInstaller,
                "_available_memory_bytes",
                return_value=2 * 1024 ** 3,
            ),
        ):
            self.assertEqual(SourceFreeEcosystemInstaller._resolve_jobs(), 7)

    def _installer(self, root: Path) -> SourceFreeEcosystemInstaller:
        return SourceFreeEcosystemInstaller(
            EcosystemCatalog.load(ROOT),
            PlatformAdapter("linux", posix=True),
            InstallerOptions(root=root, bin_dir=root / "bin", start_services=False),
        )

    def _reverse_proxy_source(self, installer: SourceFreeEcosystemInstaller) -> Path:
        source = installer._repo_dir(installer.catalog.modules["reverse-proxy"])
        (source / "dist" / "gateway").mkdir(parents=True)
        (source / "dist" / "cli.js").write_text("console.log('proxy')\n", encoding="utf-8")
        (source / "dist" / "gateway" / "cli.js").write_text(
            "console.log('gateway')\n", encoding="utf-8"
        )
        (source / "node_modules" / "example").mkdir(parents=True)
        (source / "node_modules" / "example" / "index.js").write_text(
            "export {}\n", encoding="utf-8"
        )
        (source / "package.json").write_text(
            json.dumps({"name": "kitt-reverse-proxy", "version": "9.9.9"}) + "\n",
            encoding="utf-8",
        )
        (source / "package-lock.json").write_text(
            json.dumps({"name": "kitt-reverse-proxy", "version": "9.9.9"}) + "\n",
            encoding="utf-8",
        )
        return source

    def test_repository_checkouts_live_only_under_staging(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installer = self._installer(root)
            path = installer._repo_dir(installer.catalog.modules["agent-cli"])

            self.assertEqual(path, root / ".staging" / "sources" / "kitt-agent-cli")
            self.assertNotEqual(path, root / "kitt-agent-cli")

    def test_source_sync_uses_one_remote_fetch_without_clone_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installer = self._installer(root)
            module = installer.catalog.modules["agent-cli"]

            with (
                patch.object(installer, "_run") as run,
                patch.object(installer, "_capture", return_value="a" * 40),
            ):
                installer._sync_repository(module)

            commands = [tuple(call.args[0]) for call in run.call_args_list]
            self.assertTrue(any(command[:2] == ("git", "init") for command in commands))
            self.assertEqual(
                sum(1 for command in commands if "fetch" in command),
                1,
            )
            self.assertFalse(any("clone" in command for command in commands))

    def test_source_free_native_build_only_compiles_runtime_assistant(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installer = self._installer(root)
            resolution = installer.catalog.resolve(("agent-cli",))

            with patch.object(installer, "_cargo_build_cached") as build:
                installer._build_native_components(resolution)

            build.assert_called_once_with(installer.catalog.modules["assistant"])

    def test_heavy_assistant_build_finishes_before_parallel_artifact_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installer = self._installer(root)
            resolution = installer.catalog.resolve(("agent-cli",))
            events: list[str] = []

            def native(_resolution):
                events.append("native")

            def after_native(label: str, result=None):
                self.assertEqual(events[0], "native")
                events.append(label)
                return result

            staged = root / ".staging" / "venv-test"
            with (
                patch.object(installer, "_build_native_components", side_effect=native),
                patch.object(
                    installer,
                    "_build_assistant_ui",
                    side_effect=lambda _resolution: after_native("hud"),
                ),
                patch.object(
                    installer,
                    "_build_reverse_proxy",
                    side_effect=lambda _resolution: after_native("proxy"),
                ),
                patch.object(
                    installer,
                    "_install_python_stack",
                    side_effect=lambda _resolution: after_native("python", staged),
                ),
            ):
                result = installer._build_install_artifacts_parallel(resolution)

            self.assertEqual(result, staged)
            self.assertEqual(events[0], "native")
            self.assertCountEqual(events[1:], ["hud", "proxy", "python"])

    def test_reverse_proxy_runtime_keeps_only_installed_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installer = self._installer(root)
            source = self._reverse_proxy_source(installer)
            (source / "src").mkdir()
            (source / "src" / "do-not-install.ts").write_text("source\n", encoding="utf-8")

            runtime = installer._prepare_reverse_proxy_runtime()

            self.assertEqual(runtime, root / "runtime" / "reverse-proxy")
            self.assertTrue((runtime / "dist" / "cli.js").is_file())
            self.assertTrue((runtime / "node_modules" / "example" / "index.js").is_file())
            self.assertTrue((runtime / "package.json").is_file())
            self.assertFalse((runtime / "src").exists())

    def test_reverse_proxy_launcher_never_points_at_source_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installer = self._installer(root)
            self._reverse_proxy_source(installer)
            module = installer.catalog.modules["reverse-proxy"]
            resolution = Resolution(
                requested=("reverse-proxy",),
                modules=(module,),
                auto_selected_by={},
            )
            node = CommandInfo(argv=("node",), version=(24, 0, 0), version_text="24.0.0")

            with (
                patch.object(installer.platform, "command_info", return_value=node),
                patch.object(installer, "_run"),
            ):
                installer._install_launchers(resolution, None)

            launcher = (root / "bin" / "kitt-reverse-proxy").read_text(encoding="utf-8")
            self.assertIn(str(root / "runtime" / "reverse-proxy" / "dist" / "cli.js"), launcher)
            self.assertNotIn(".staging/sources", launcher)

    def test_assistant_binaries_are_promoted_from_persistent_build_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installer = self._installer(root)
            source = installer._repo_dir(installer.catalog.modules["assistant"])
            release = installer._cargo_target_dir("assistant") / "release"
            release.mkdir(parents=True)
            for name in ("kittctl", "kittd"):
                binary = release / name
                binary.write_text(name, encoding="utf-8")
                binary.chmod(0o755)
            hud = source / "apps" / "kitt-hud" / "dist"
            hud.mkdir(parents=True)
            (hud / "index.html").write_text("hud", encoding="utf-8")

            runtime = installer._prepare_assistant_runtime()

            self.assertTrue((runtime / "bin" / "kittctl").is_file())
            self.assertTrue((runtime / "bin" / "kittd").is_file())
            self.assertTrue((runtime / "hud" / "index.html").is_file())
            self.assertFalse((runtime / "target").exists())
            self.assertFalse((runtime / "apps").exists())

    def test_python_stack_batches_local_packages_without_build_isolation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installer = self._installer(root)
            installer._python = CommandInfo(
                argv=("python3",), version=(3, 14, 0), version_text="3.14.0"
            )
            modules = (
                installer.catalog.modules["protocol"],
                installer.catalog.modules["agent-cli"],
            )
            resolution = Resolution(
                requested=("agent-cli",),
                modules=modules,
                auto_selected_by={},
            )

            with patch.object(installer, "_run") as run:
                installer._install_python_stack(resolution)

            commands = [tuple(str(value) for value in call.args[0]) for call in run.call_args_list]
            pip_commands = [command for command in commands if "pip" in command]
            self.assertTrue(any("setuptools>=68" in command for command in pip_commands))
            self.assertFalse(
                any("prompt-toolkit>=3.0.52,<4" in command for command in pip_commands)
            )

            agent_source = str(installer._repo_dir(installer.catalog.modules["agent-cli"]))
            dependency_passes = [
                command
                for command in pip_commands
                if agent_source in command
                and "--prefer-binary" in command
                and "--no-deps" not in command
            ]
            self.assertEqual(len(dependency_passes), 1)

            authoritative_installs = [
                command for command in pip_commands if "--force-reinstall" in command
            ]
            self.assertEqual(len(authoritative_installs), 2)
            self.assertTrue(all("--no-deps" in command for command in authoritative_installs))
            self.assertNotIn(agent_source, authoritative_installs[0])
            self.assertEqual(authoritative_installs[-1][-1], agent_source)
            self.assertFalse(any("-U" in command and "pip" in command for command in pip_commands))
            self.assertTrue(any(command[-2:] == ("pip", "check") for command in commands))

    def test_service_setup_failure_is_not_silently_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installer = self._installer(root)
            binary = root / "runtime" / "assistant" / "bin" / "kittctl"
            binary.parent.mkdir(parents=True)
            binary.write_text("kittctl", encoding="utf-8")
            resolution = Resolution(
                requested=("assistant",),
                modules=(installer.catalog.modules["assistant"],),
                auto_selected_by={},
            )
            installer.options = InstallerOptions(
                root=root,
                bin_dir=root / "bin",
                start_services=True,
            )

            with (
                patch.object(installer, "_run", side_effect=RuntimeError("service failed")),
                self.assertRaisesRegex(RuntimeError, "service failed"),
            ):
                installer._start_services(resolution)

    def test_staging_cleanup_removes_sources_but_keeps_build_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installer = self._installer(root)
            sources = root / ".staging" / "sources" / "kitt-agent-cli"
            sources.mkdir(parents=True)
            (sources / "source.py").write_text("source\n", encoding="utf-8")
            cached = installer._cargo_target_dir("assistant") / "release" / "cached"
            cached.parent.mkdir(parents=True, exist_ok=True)
            cached.write_text("artifact", encoding="utf-8")

            installer._cleanup_staging()

            self.assertFalse((root / ".staging" / "sources").exists())
            self.assertTrue(cached.is_file())

    def test_success_migration_removes_legacy_managed_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installer = self._installer(root)
            legacy = root / "kitt-reverse-proxy"
            (legacy / ".git").mkdir(parents=True)
            (legacy / "src").mkdir()
            (legacy / "src" / "old.ts").write_text("old\n", encoding="utf-8")
            installer._managed_legacy_sources.add("kitt-reverse-proxy")

            installer._remove_legacy_source_checkouts()

            self.assertFalse(legacy.exists())


if __name__ == "__main__":
    unittest.main()
