from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from installer.catalog import CatalogError, EcosystemCatalog

SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def validate(root: str | Path = ROOT) -> dict[str, str]:
    catalog = EcosystemCatalog.load(root)
    for repository, sha in catalog.locks.items():
        if not SHA_RE.fullmatch(sha):
            raise ValueError(f"{repository} is not pinned to an immutable 40-char SHA")

    # Product invariant: selecting the Agent means the complete integrated KITT
    # technology stack, never a silently degraded Agent-only install.
    agent = catalog.resolve(["agent-cli"])
    if set(agent.ids) != set(catalog.modules):
        missing = sorted(set(catalog.modules) - set(agent.ids))
        raise ValueError(
            "agent-cli must resolve the complete integrated ecosystem; "
            f"missing={missing}"
        )
    return dict(catalog.locks)


def main() -> int:
    try:
        components = validate(sys.argv[1] if len(sys.argv) > 1 else ROOT)
    except (OSError, ValueError, CatalogError) as exc:
        print(f"ecosystem catalog/lock invalid: {exc}", file=sys.stderr)
        return 1
    for repository, sha in sorted(components.items()):
        print(f"{repository} {sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
