"""Pinned, user-scoped REA CLI setup for the explicit full ecosystem preset.

No system-wide npm installation, Node updates, shell execution, or
unapproved MCP server registration. REA runs through KITT's optional plugin.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

REA_VERSION = "6.4.0"
_PACKAGE = f"rea-agents@{REA_VERSION}"


class ReaInstallError(ValueError):
    pass


def _supported_node(version: str) -> bool:
    """REA 6.4.0 engines: ^22.19.0 || ^24.11.0 || >=26.0.0."""
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", version.strip())
    if not match:
        return False
    major, minor, _ = (int(x) for x in match.groups())
    return (major == 22 and minor >= 19) or (major == 24 and minor >= 11) or major >= 26


def _check_node() -> str:
    node, npm = shutil.which("node"), shutil.which("npm")
    if not node or not npm:
        raise ReaInstallError("REA 6.4.0 requires Node.js 24.11+ and npm. Install Node 24 LTS.")
    try:
        result = subprocess.run([node, "--version"], capture_output=True, text=True,
                                check=False, timeout=15)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReaInstallError("Could not determine Node.js version") from exc
    if result.returncode or not _supported_node(result.stdout):
        raise ReaInstallError("REA 6.4.0 requires Node 22.19+, 24.11+, or 26+ (not Node 23/25)")
    return npm


def _binary(prefix: Path) -> Path:
    if os.name == "nt":
        return prefix / "rea.cmd"
    return prefix / "bin" / "rea"


def _installed_version(executable: Path) -> bool:
    if not executable.is_file():
        return False
    try:
        result = subprocess.run([str(executable), "--version"],
                                capture_output=True, text=True, check=False, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0 and (
        result.stdout.strip().splitlines()[:1] == [REA_VERSION]
        or result.stdout.strip().splitlines()[:1] == [f"rea {REA_VERSION}"]
    )


def install_rea(root: Path, bin_dir: Path, *, dry_run: bool = False) -> dict:
    """Install pinned REA into KITT's user-owned prefix and expose an owned launcher."""
    prefix = root / "rea"
    destination = _binary(prefix)
    launcher = bin_dir / ("rea.cmd" if os.name == "nt" else "rea")
    if dry_run:
        return {"planned": True, "version": REA_VERSION, "prefix": str(prefix)}
    npm = _check_node()
    if not _installed_version(destination):
        prefix.mkdir(parents=True, exist_ok=True)
        # Keep npm scoped to KITT's prefix. Never alter the global npm prefix.
        argv = [npm, "install", "--global", "--prefix", str(prefix),
                "--no-audit", "--no-fund", "--ignore-scripts", "--no-package-lock", _PACKAGE]
        try:
            outcome = subprocess.run(argv, check=False, timeout=900)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ReaInstallError("REA npm installation failed or timed out") from exc
        if outcome.returncode or not _installed_version(destination):
            raise ReaInstallError(
                "REA installation was incomplete. Check npm output, Node version and network access."
            )
    bin_dir.mkdir(parents=True, exist_ok=True)
    if launcher.is_symlink():
        if launcher.resolve(strict=False) != destination.resolve(strict=False):
            # A user-managed launcher must never be replaced.
            return {"installed": True, "version": REA_VERSION, "launcher": "existing", "prefix": str(prefix)}
    elif launcher.exists():
        return {"installed": True, "version": REA_VERSION, "launcher": "existing", "prefix": str(prefix)}
    else:
        if os.name == "nt":
            # Local npm-generated wrapper must be invoked from its owning directory.
            # Windows paths cannot contain double quotes, so they remain quoted.
            launcher.write_text(f'@echo off\r\ncall "{destination}" %*\r\n', encoding="utf-8")
        else:
            launcher.symlink_to(destination)
    return {"installed": True, "version": REA_VERSION, "launcher": str(launcher), "prefix": str(prefix)}
