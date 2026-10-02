from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .catalog import EcosystemCatalog

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class ReleaseManifestError(ValueError):
    pass


@dataclass(frozen=True)
class ReleaseComponent:
    id: str
    repository: str
    sha: str


class ReleaseManifest:
    def __init__(self, payload: dict):
        if payload.get("schema_version") != 1:
            raise ReleaseManifestError("release manifest schema_version must be 1")
        if payload.get("channel") != "release":
            raise ReleaseManifestError("release manifest channel must be 'release'")
        version = str(payload.get("ecosystem_version") or "").strip()
        if not version:
            raise ReleaseManifestError("release manifest ecosystem_version is required")
        raw_components = payload.get("components")
        if not isinstance(raw_components, dict) or not raw_components:
            raise ReleaseManifestError("release manifest components must be a non-empty object")
        components: dict[str, ReleaseComponent] = {}
        for component_id, raw in raw_components.items():
            if not isinstance(raw, dict):
                raise ReleaseManifestError(f"release component {component_id!r} must be an object")
            repository = str(raw.get("repository") or "").strip()
            sha = str(raw.get("sha") or "").strip().lower()
            if not repository or "/" not in repository:
                raise ReleaseManifestError(f"release component {component_id!r} has invalid repository")
            if not _SHA_RE.fullmatch(sha):
                raise ReleaseManifestError(
                    f"release component {component_id!r} must use an immutable 40-char SHA"
                )
            components[str(component_id)] = ReleaseComponent(
                id=str(component_id), repository=repository, sha=sha
            )
        self.ecosystem_version = version
        self.components = components

    @classmethod
    def load(cls, root: str | Path) -> "ReleaseManifest":
        root_path = Path(root)
        payload = json.loads((root_path / "ecosystem.release.json").read_text(encoding="utf-8"))
        return cls(payload)

    def validate_catalog(self, catalog: EcosystemCatalog) -> None:
        expected = set(catalog.modules)
        actual = set(self.components)
        if actual != expected:
            raise ReleaseManifestError(
                f"release manifest component mismatch: missing={sorted(expected-actual)}, "
                f"extra={sorted(actual-expected)}"
            )
        for component_id, module in catalog.modules.items():
            release = self.components[component_id]
            if release.repository != module.repository:
                raise ReleaseManifestError(
                    f"release component {component_id!r} repository mismatch: "
                    f"{release.repository!r} != {module.repository!r}"
                )

    def refs(self, catalog: EcosystemCatalog) -> dict[str, str]:
        self.validate_catalog(catalog)
        return {component_id: self.components[component_id].sha for component_id in catalog.modules}
