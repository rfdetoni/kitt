from __future__ import annotations

import json
import re
import sys
from pathlib import Path

EXPECTED = {
    "rfdetoni/kitt-protocol",
    "rfdetoni/kitt-memory",
    "rfdetoni/kitt-toolbox",
    "rfdetoni/kitt-ai-workers",
    "rfdetoni/kitt-assistant",
    "rfdetoni/kitt-agent-cli",
    "rfdetoni/kitt-reverse-proxy",
}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def validate(path: str | Path = "ecosystem.lock.json") -> dict[str, str]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("ecosystem lock schema_version must be 1")
    components = payload.get("components")
    if not isinstance(components, dict):
        raise ValueError("ecosystem lock components must be an object")
    names = set(components)
    if names != EXPECTED:
        missing = sorted(EXPECTED - names)
        extra = sorted(names - EXPECTED)
        raise ValueError(f"ecosystem lock component mismatch; missing={missing}, extra={extra}")
    for repository, sha in components.items():
        if not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
            raise ValueError(f"{repository} is not pinned to an immutable 40-char SHA")
    return {str(key): str(value) for key, value in components.items()}


def main() -> int:
    try:
        components = validate(sys.argv[1] if len(sys.argv) > 1 else "ecosystem.lock.json")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ecosystem lock invalid: {exc}", file=sys.stderr)
        return 1
    for repository, sha in sorted(components.items()):
        print(f"{repository} {sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
