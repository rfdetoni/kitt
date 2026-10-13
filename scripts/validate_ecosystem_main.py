from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen

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


def validate_main_heads(root: str | Path = ROOT) -> dict[str, str]:
    """Check that every immutable release pin matches the current component main.

    This is an online CI/release freshness gate, not an install-time network
    dependency. A release still installs its immutable SHAs without consulting
    moving branch heads.
    """
    root_path = Path(root)
    catalog = EcosystemCatalog.load(root_path)
    pins = load_release_components(root_path, catalog)
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "kitt-release-pin-check"}
    token = os.environ.get("GH_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    stale: list[str] = []
    heads: dict[str, str] = {}
    for component, (repository, pinned_sha) in sorted(pins.items()):
        url = f"https://api.github.com/repos/{repository}/git/ref/heads/main"
        try:
            with urlopen(Request(url, headers=headers), timeout=15) as response:
                payload = json.load(response)
            head = payload["object"]["sha"]
            if not isinstance(head, str) or len(head) != 40:
                raise ValueError("invalid SHA from GitHub")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise ValueError(f"unable to verify {repository} main: {type(exc).__name__}") from exc
        heads[component] = head
        if head != pinned_sha:
            stale.append(f"{component}: pin {pinned_sha} != main {head}")

    if stale:
        raise ValueError("release manifest is behind component main:\n" + "\n".join(stale))
    return heads


def main() -> int:
    release = "--release" in sys.argv[1:]
    check_heads = "--check-main-heads" in sys.argv[1:]
    try:
        catalog = EcosystemCatalog.load(ROOT)
        if release:
            for component_id, (repository, sha) in sorted(
                load_release_components(ROOT, catalog).items()
            ):
                print(f"{component_id} {repository} {sha}")
        elif check_heads:
            for component_id, sha in sorted(validate_main_heads().items()):
                print(f"{component_id} {sha}")
        else:
            for repository, ref in sorted(validate().items()):
                print(f"{repository} {ref}")
    except (OSError, ValueError, CatalogError) as exc:
        print(f"ecosystem policy invalid: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
