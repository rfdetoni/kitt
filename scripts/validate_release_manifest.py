from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from installer.catalog import CatalogError, EcosystemCatalog
from installer.release_manifest import ReleaseManifest, ReleaseManifestError


def validate(root: str | Path = ROOT) -> dict[str, tuple[str, str]]:
    root_path = Path(root)
    catalog = EcosystemCatalog.load(root_path)
    manifest = ReleaseManifest.load(root_path)
    manifest.validate_catalog(catalog)
    version = (root_path / "VERSION").read_text(encoding="utf-8").strip()
    if manifest.ecosystem_version != version:
        raise ReleaseManifestError(
            "release manifest ecosystem_version does not match VERSION: "
            f"{manifest.ecosystem_version!r} != {version!r}"
        )
    return {
        component_id: (
            manifest.components[component_id].repository,
            manifest.components[component_id].sha,
        )
        for component_id in catalog.modules
    }


def main() -> int:
    try:
        components = validate(sys.argv[1] if len(sys.argv) > 1 else ROOT)
    except (OSError, ValueError, CatalogError, ReleaseManifestError) as exc:
        print(f"release manifest invalid: {exc}", file=sys.stderr)
        return 1
    for component_id, (repository, sha) in sorted(components.items()):
        print(f"{component_id} {repository} {sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
