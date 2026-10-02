from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from installer.catalog import EcosystemCatalog
from installer.core import EcosystemInstaller, InstallerOptions
from installer.platforms import PlatformAdapter
from installer.source_free import SourceFreeEcosystemInstaller


ROOT = Path(__file__).resolve().parents[1]


class NativeRunnerLifecycleTests(unittest.TestCase):
    def test_full_agent_toolchain_floor_matches_catalog(self) -> None:
        catalog = EcosystemCatalog.load(ROOT)
        resolution = catalog.resolve(["agent-cli"])
        minimums: dict[str, tuple[int, ...]] = {}

        for module in resolution.modules:
            for declaration in module.prerequisites:
                name, minimum = EcosystemInstaller._parse_requirement(declaration)
                if minimum > minimums.get(name, ()):
                    minimums[name] = minimum

        self.assertEqual(minimums["python"], (3, 14))
        self.assertEqual(minimums["node"], (24,))
        self.assertEqual(minimums["rust"], (1, 90))

    def test_native_launcher_update_and_path_resolution(self) -> None:
        adapter = PlatformAdapter.detect()
        with tempfile.TemporaryDirectory() as temp:
            bin_dir = Path(temp) / "bin"
            first = adapter.write_launcher(bin_dir, "kitt", ["old-runtime", "arg"])
            previous = first.read_text(encoding="ascii" if adapter.name == "windows" else "utf-8")

            current = adapter.write_launcher(bin_dir, "kitt", ["new-runtime", "arg"])

            self.assertEqual(current, first)
            content = current.read_text(encoding="ascii" if adapter.name == "windows" else "utf-8")
            self.assertNotEqual(content, previous)
            self.assertIn("new-runtime", content)
            self.assertNotIn("old-runtime", content)
            if adapter.name == "windows":
                self.assertEqual(current.suffix, ".cmd")
                self.assertIn("%*", content)
            else:
                self.assertEqual(current.suffix, "")
                self.assertTrue(os.access(current, os.X_OK))
                self.assertIn('"$@"', content)

            with patch(
                "installer.platforms.shutil.which",
                side_effect=lambda name: str(current) if name == "kitt" else None,
            ):
                self.assertEqual(adapter.launcher_shadow_conflicts(bin_dir), {})

    def test_native_stop_targets_only_resident_kitt_entrypoints(self) -> None:
        adapter = PlatformAdapter.detect()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            launcher_suffix = ".cmd" if adapter.name == "windows" else ""
            (bin_dir / f"kitt{launcher_suffix}").write_text("", encoding="utf-8")
            (bin_dir / f"kittctl{launcher_suffix}").write_text("", encoding="utf-8")

            def which(name: str) -> str | None:
                if adapter.name == "windows" and name in {"powershell", "pwsh"}:
                    return "powershell.exe"
                if adapter.name == "macos" and name == "launchctl":
                    return "/bin/launchctl"
                if adapter.name != "windows" and name == "pgrep":
                    return "/usr/bin/pgrep"
                if adapter.name == "linux" and name == "systemctl":
                    return "/usr/bin/systemctl"
                return None

            def capture(argv):
                if argv[0].endswith("pgrep"):
                    return 1, ""
                return 0, ""

            with (
                patch("installer.platforms.shutil.which", side_effect=which),
                patch("installer.platforms._run_capture", side_effect=capture) as run,
            ):
                adapter.stop_kitt_services(root, bin_dir)

            commands = [tuple(call.args[0]) for call in run.call_args_list]
            self.assertIn((str(bin_dir / f"kittctl{launcher_suffix}"), "service", "stop"), commands)
            self.assertIn((str(bin_dir / f"kitt{launcher_suffix}"), "daemon", "stop"), commands)

            if adapter.name == "windows":
                powershell = next(command for command in commands if command[0] == "powershell.exe")
                self.assertIn("KITT Reverse Proxy", powershell[-1])
                self.assertIn("daemon\\s+run", powershell[-1])
            elif adapter.name == "macos":
                labels = {
                    command[-1]
                    for command in commands
                    if command[:2] == ("/bin/launchctl", "stop")
                }
                self.assertEqual(
                    labels,
                    {
                        "com.kitt.daemon",
                        "com.kitt.assistant",
                        "com.kitt.reverse-proxy",
                        "com.kitt.agent-gateway",
                    },
                )
            else:
                self.assertTrue(
                    any(command[:3] == ("/usr/bin/systemctl", "--user", "stop") for command in commands)
                )

    def test_native_start_and_cleanup_use_managed_runtime_only(self) -> None:
        adapter = PlatformAdapter.detect()
        catalog = EcosystemCatalog.load(ROOT)
        resolution = catalog.resolve(["assistant"])

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installer = SourceFreeEcosystemInstaller(
                catalog,
                adapter,
                InstallerOptions(root=root, bin_dir=root / "bin"),
            )
            suffix = ".exe" if adapter.name == "windows" else ""
            kittctl = root / "runtime" / "assistant" / "bin" / f"kittctl{suffix}"
            kittctl.parent.mkdir(parents=True)
            kittctl.write_text("", encoding="utf-8")

            with patch.object(installer, "_run") as run:
                installer._start_services(resolution)

            self.assertEqual(
                [call.args[0] for call in run.call_args_list],
                [
                    [str(kittctl), "service", "install"],
                    [str(kittctl), "service", "restart"],
                ],
            )

            staging = root / ".staging"
            for name in ("sources", "runtime-next", "runtime-previous", "venv-123", "toolbox-native"):
                (staging / name).mkdir(parents=True, exist_ok=True)
            sentinel = staging / "keep.txt"
            sentinel.write_text("keep", encoding="utf-8")

            installer._cleanup_staging()

            for name in ("sources", "runtime-next", "runtime-previous", "venv-123", "toolbox-native"):
                self.assertFalse((staging / name).exists())
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
