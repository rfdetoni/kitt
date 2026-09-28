from __future__ import annotations

import unittest

from scripts.validate_component_pins import dependency_checks


class ComponentPinArchitectureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.components = {
            "rfdetoni/kitt-protocol": "p" * 40,
            "rfdetoni/kitt-memory": "m" * 40,
            "rfdetoni/kitt-toolbox": "t" * 40,
            "rfdetoni/kitt-ai-workers": "w" * 40,
            "rfdetoni/kitt-assistant": "s" * 40,
            "rfdetoni/kitt-agent-cli": "a" * 40,
            "rfdetoni/kitt-reverse-proxy": "r" * 40,
        }

    def test_component_ci_fixtures_are_not_ecosystem_dependency_pins(self) -> None:
        checks = dependency_checks(self.components)
        paths = [path for _, path, _, _ in checks]
        self.assertFalse(any(path.startswith(".github/workflows/") for path in paths))

    def test_runtime_dependency_edges_remain_enforced(self) -> None:
        checks = {
            (repository, path): expected
            for repository, path, _, expected in dependency_checks(self.components)
        }
        self.assertEqual(
            checks[("rfdetoni/kitt-agent-cli", "pyproject.toml")],
            ("p" * 40,),
        )
        self.assertEqual(
            checks[("rfdetoni/kitt-ai-workers", "packages/kitt-evolution/pyproject.toml")],
            ("a" * 40,),
        )
        self.assertEqual(
            checks[("rfdetoni/kitt-assistant", "apps/kittd/Cargo.toml")],
            ("p" * 40, "m" * 40),
        )


if __name__ == "__main__":
    unittest.main()
