from __future__ import annotations

import json
import re
from pathlib import Path

from .catalog import EcosystemCatalog

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def load_release_components(
    root: str | Path,
    catalog: EcosystemCatalog,
) -> dict[str, tuple[str, str]]:
    root_path = Path(root)
    payload = json.loads((root_path / "ecosystem.release.json").read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or payload.get("channel") != "release":
        raise ValueError("invalid ecosystem.release.json header")
    version = (root_path / "VERSION").read_text(encoding="utf-8").strip()
    if str(payload.get("ecosystem_version") or "").strip() != version:
        raise ValueError("ecosystem.release.json version does not match VERSION")

    raw = payload.get("components")
    if not isinstance(raw, dict) or set(raw) != set(catalog.modules):
        raise ValueError("ecosystem.release.json must pin every catalog component exactly once")

    components: dict[str, tuple[str, str]] = {}
    for component_id, module in catalog.modules.items():
        item = raw[component_id]
        if not isinstance(item, dict):
            raise ValueError(f"invalid release component {component_id!r}")
        repository = str(item.get("repository") or "").strip()
        sha = str(item.get("sha") or "").strip().lower()
        if repository != module.repository or not _SHA_RE.fullmatch(sha):
            raise ValueError(f"invalid release pin for {component_id!r}")
        components[component_id] = (repository, sha)
    return components


def load_release_refs(root: str | Path, catalog: EcosystemCatalog) -> dict[str, str]:
    return {
        component_id: sha
        for component_id, (_, sha) in load_release_components(root, catalog).items()
    }
