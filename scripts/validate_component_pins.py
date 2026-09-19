from __future__ import annotations

import base64
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "ecosystem.lock.json"


class PinValidationError(RuntimeError):
    pass


def _fetch_text(repository: str, path: str, ref: str) -> str:
    encoded_path = urllib.parse.quote(path, safe="/")
    encoded_ref = urllib.parse.quote(ref, safe="")
    url = f"https://api.github.com/repos/{repository}/contents/{encoded_path}?ref={encoded_ref}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "kitt-component-pin-validator",
    }
    token = os.environ.get("GH_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    raw = payload.get("content")
    if not isinstance(raw, str):
        raise PinValidationError(f"{repository}@{ref}:{path}: GitHub returned no file content")
    return base64.b64decode(raw).decode("utf-8")


def _require(text: str, expected: str, label: str) -> None:
    if expected not in text:
        raise PinValidationError(f"{label} does not reference expected revision {expected}")


def _reject_mutable_vcs_ref(text: str, label: str) -> None:
    needles = (
        "git+https://github.com/rfdetoni/kitt-protocol.git@main",
        "git+https://github.com/rfdetoni/kitt-agent-cli.git@main",
        "git+https://github.com/rfdetoni/kitt-assistant.git@main",
        "git+https://github.com/rfdetoni/kitt-memory.git@main",
        "git+https://github.com/rfdetoni/kitt-toolbox.git@main",
    )
    for needle in needles:
        if needle in text:
            raise PinValidationError(f"{label} contains mutable internal dependency {needle}")


def validate(root: Path = ROOT) -> None:
    payload = json.loads((root / "ecosystem.lock.json").read_text(encoding="utf-8"))
    components = payload["components"]

    protocol = components["rfdetoni/kitt-protocol"]
    memory = components["rfdetoni/kitt-memory"]
    assistant = components["rfdetoni/kitt-assistant"]
    agent = components["rfdetoni/kitt-agent-cli"]
    workers = components["rfdetoni/kitt-ai-workers"]

    checks: list[tuple[str, str, str, tuple[str, ...]]] = [
        (
            "rfdetoni/kitt-agent-cli",
            "pyproject.toml",
            agent,
            (protocol,),
        ),
        (
            "rfdetoni/kitt-agent-cli",
            ".github/workflows/ci.yml",
            agent,
            (assistant,),
        ),
        (
            "rfdetoni/kitt-agent-cli",
            ".github/workflows/pr-checks.yml",
            agent,
            (assistant,),
        ),
        (
            "rfdetoni/kitt-agent-cli",
            ".github/workflows/prime-architecture.yml",
            agent,
            (assistant,),
        ),
        (
            "rfdetoni/kitt-agent-cli",
            ".github/workflows/release.yml",
            agent,
            (assistant,),
        ),
        (
            "rfdetoni/kitt-assistant",
            "crates/kitt-domain/Cargo.toml",
            assistant,
            (memory,),
        ),
        (
            "rfdetoni/kitt-assistant",
            "crates/kitt-infrastructure/Cargo.toml",
            assistant,
            (memory,),
        ),
        (
            "rfdetoni/kitt-assistant",
            "apps/kittd/Cargo.toml",
            assistant,
            (protocol, memory),
        ),
        (
            "rfdetoni/kitt-assistant",
            "apps/kittctl/Cargo.toml",
            assistant,
            (protocol,),
        ),
        (
            "rfdetoni/kitt-assistant",
            "apps/kitt-hud/package.json",
            assistant,
            (protocol,),
        ),
        (
            "rfdetoni/kitt-ai-workers",
            "pyproject.toml",
            workers,
            (protocol,),
        ),
        (
            "rfdetoni/kitt-ai-workers",
            "packages/kitt-evolution/pyproject.toml",
            workers,
            (agent,),
        ),
        (
            "rfdetoni/kitt-ai-workers",
            "packages/kitt-evals/pyproject.toml",
            workers,
            (agent,),
        ),
    ]

    for repository, path, ref, expected_revisions in checks:
        label = f"{repository}@{ref}:{path}"
        text = _fetch_text(repository, path, ref)
        _reject_mutable_vcs_ref(text, label)
        for expected in expected_revisions:
            _require(text, expected, label)
        print(f"{label}: coherent")

    # The lock itself must retain the same refs used during this validation.
    current = json.loads((root / "ecosystem.lock.json").read_text(encoding="utf-8"))["components"]
    if current != components:
        raise PinValidationError("ecosystem.lock.json changed during validation")


def main() -> int:
    try:
        validate(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT)
    except (OSError, KeyError, ValueError, urllib.error.URLError, PinValidationError) as exc:
        print(f"ecosystem component pins invalid: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
