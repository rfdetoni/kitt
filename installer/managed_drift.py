from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


_REVERSE_PROXY_DIR = "kitt-reverse-proxy"
_LOCKFILE = "package-lock.json"
_VERSION_SENTINEL = "__kitt_managed_version__"


def _git(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=path,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _normalized_lock(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    packages = payload.get("packages")
    if not isinstance(packages, dict):
        return None
    root_package = packages.get("")
    if not isinstance(root_package, dict):
        return None

    normalized = dict(payload)
    normalized["version"] = _VERSION_SENTINEL
    normalized_packages = dict(packages)
    normalized_root = dict(root_package)
    normalized_root["version"] = _VERSION_SENTINEL
    normalized_packages[""] = normalized_root
    normalized["packages"] = normalized_packages
    return normalized


def _is_version_only_lock_drift(repo: Path) -> bool:
    status = _git(repo, "status", "--porcelain")
    if status.returncode != 0:
        return False

    lines = [line for line in status.stdout.splitlines() if line]
    if len(lines) != 1:
        return False

    line = lines[0]
    if len(line) < 4 or line[:2] != " M" or line[3:] != _LOCKFILE:
        return False

    baseline = _git(repo, "show", f"HEAD:{_LOCKFILE}")
    if baseline.returncode != 0:
        return False

    lock_path = repo / _LOCKFILE
    try:
        baseline_payload = json.loads(baseline.stdout)
        working_payload = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False

    baseline_normalized = _normalized_lock(baseline_payload)
    working_normalized = _normalized_lock(working_payload)
    return (
        baseline_normalized is not None
        and working_normalized is not None
        and baseline_normalized == working_normalized
        and baseline_payload != working_payload
    )


def repair_known_managed_drift(root: Path) -> tuple[Path, ...]:
    """Repair installer-generated metadata drift without discarding real user edits.

    Older K.I.T.T. installs could leave the reverse-proxy lockfile dirty when npm
    normalized only the package version metadata.  That specific shape is safe to
    restore because every dependency and lock entry must still match HEAD after the
    two root version fields are normalized.  Any other change remains blocking and
    is intentionally left untouched for the installer's normal fail-closed check.
    """

    repo = root / _REVERSE_PROXY_DIR
    if not (repo / ".git").is_dir() or not _is_version_only_lock_drift(repo):
        return ()

    restored = _git(repo, "restore", "--worktree", "--", _LOCKFILE)
    if restored.returncode != 0:
        return ()
    return (repo / _LOCKFILE,)
