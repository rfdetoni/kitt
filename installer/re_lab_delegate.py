"""Central installer delegates opt-in RE lab setup to the installed Agent CLI.

This module is intentionally small: there is only one Docker/OEM provisioner.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

from .re_lab import ReLabError, check_re_lab


def provision_with_agent(root: Path, *, runtime: str, profile: str,
                         windows: str, version: str, accept_license: bool,
                         yes: bool) -> dict:
    if not accept_license or not yes:
        raise ReLabError("RE lab requires --yes and --accept-windows-license")
    check_re_lab(runtime=runtime, profile=profile, windows=windows, version=version)
    python = root / ".venv-agent" / "bin" / "python"
    if not python.is_file():
        raise ReLabError("Agent CLI is not installed in the managed Python runtime")
    args = [str(python), "-m", "kitt.cli.main", "re", "lab", "setup",
            "--runtime", "docker", "--windows", "11", "--linux-profile", "full",
            "--state-root", str(root / "re-lab"), "--yes", "--accept-license"]
    try:
        result = subprocess.run(args, check=False, capture_output=True,
                                text=True, timeout=3600)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReLabError("Agent RE lab setup failed or timed out") from exc
    if result.returncode or len(result.stdout) > 65536:
        # Never forward opaque Docker/OEM logs containing possible credentials.
        raise ReLabError("Agent RE lab setup did not succeed; run kitt re lab doctor")
    try:
        payload = json.loads(result.stdout)
    except ValueError as exc:
        raise ReLabError("Agent RE lab returned invalid JSON") from exc
    if not isinstance(payload, dict) or payload.get("status") not in (
        "PROVISIONING", "EXISTING_UNVERIFIED"
    ):
        raise ReLabError("Agent RE lab returned an unrecognized provisioning state")
    return payload
