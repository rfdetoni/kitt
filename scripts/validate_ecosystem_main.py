from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from installer.catalog import CatalogError, EcosystemCatalog
from installer.release_manifest import load_release_components


def validate(root: str | Path = ROOT) -> dict[str, str]:
    root_path = Path(root)
    if (root_path / "ecosystem.lock.json").exists():
        raise ValueError("legacy ecosystem.lock.json must not exist; use ecosystem.release.json")

    catalog = EcosystemCatalog.load(root_path)
    load_release_components(root_path, catalog)
    refs = {module.repository: catalog.resolve_ref(module) for module in catalog.modules.values()}
    if any(ref != "main" for ref in refs.values()):
        raise ValueError("edge component refs must default to main")

    agent = catalog.resolve(["agent-cli"])
    if set(agent.ids) != set(catalog.modules):
        raise ValueError("agent-cli must resolve the complete integrated ecosystem")
    return refs


def main() -> int:
    release = "--release" in sys.argv[1:]
    try:
        catalog = EcosystemCatalog.load(ROOT)
        if release:
            for component_id, (repository, sha) in sorted(
                load_release_components(ROOT, catalog).items()
            ):
                print(f"{component_id} {repository} {sha}")
        else:
            for repository, ref in sorted(validate().items()):
                print(f"{repository} {ref}")
    except (OSError, ValueError, CatalogError) as exc:
        print(f"ecosystem policy invalid: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
