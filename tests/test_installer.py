from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from installer.catalog import CatalogError, EcosystemCatalog
from installer.core import EcosystemInstaller
from installer.platforms import PlatformAdapter


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


class RequirementTests(unittest.TestCase):
    def test_requirement_parser(self) -> None:
        self.assertEqual(EcosystemInstaller._parse_requirement("python>=3.12"), ("python", (3, 12)))
        self.assertEqual(EcosystemInstaller._parse_requirement("git"), ("git", ()))


if __name__ == "__main__":
    unittest.main()
