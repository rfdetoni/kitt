from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from installer.catalog import CatalogError, EcosystemCatalog
from installer.release_manifest import ReleaseManifest, ReleaseManifestError


def validate(root: str | Path = ROOT) -> dict[str, str]:
    root_path = Path(root)
    if (root_path / "ecosystem.lock.json").exists():
        raise ValueError("legacy ecosystem.lock.json must not exist; use ecosystem.release.json")

    catalog = EcosystemCatalog.load(root_path)
    ReleaseManifest.load(root_path).validate_catalog(catalog)
    refs = {
        module.repository: catalog.resolve_ref(module)
        for module in catalog.modules.values()
    }
    stale = {repository: ref for repository, ref in refs.items() if ref != "main"}
    if stale:
        raise ValueError(f"all default component refs must be main: {stale}")

    agent = catalog.resolve(["agent-cli"])
    if set(agent.ids) != set(catalog.modules):
        missing = sorted(set(catalog.modules) - set(agent.ids))
        raise ValueError(
            "agent-cli must resolve the complete integrated ecosystem; "
            f"missing={missing}"
        )
    return refs


def main() -> int:
    try:
        refs = validate(sys.argv[1] if len(sys.argv) > 1 else ROOT)
    except (OSError, ValueError, CatalogError, ReleaseManifestError) as exc:
        print(f"ecosystem main policy invalid: {exc}", file=sys.stderr)
        return 1
    for repository, ref in sorted(refs.items()):
        print(f"{repository} {ref}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
