"""Opt-in VM lab prerequisite checks; never changes the host or installs packages."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


class VMLabPrerequisiteError(ValueError):
    pass


def check_vm_lab(*, provision: bool = False) -> dict:
    if sys.platform != "linux":
        raise VMLabPrerequisiteError("VM autonomy requires a Linux host running QEMU")
    programs = ("qemu-system-x86_64", "qemu-img", "ssh")
    if provision:
        programs += ("cloud-localds", "ssh-keygen")
    missing = [
        program for program in programs
        if not shutil.which(program)
    ]
    if missing:
        raise VMLabPrerequisiteError(
            "Missing VM lab tools: " + ", ".join(missing)
            + ". Install QEMU system + qemu-utils and OpenSSH client using your OS package manager."
        )
    return {
        "ready": True,
        "kvm": os.access("/dev/kvm", os.R_OK | os.W_OK),
        "guest_image_required": not provision,
        "note": "Pinned Debian provisioning requested." if provision else
                "Preflight only; use --vm-image-sha512 to provision explicitly.",
    }


def prepare_guest(root: Path, *, image_sha512: str, gateway_port: int = 3000) -> Path:
    """Delegate to the installed Agent; never fetch a moving Agent ref."""
    check_vm_lab(provision=True)
    if not isinstance(image_sha512, str) or not re.fullmatch(r"[a-f0-9]{128}", image_sha512):
        raise VMLabPrerequisiteError("A trusted Debian SHA512 pin is required")
    if type(gateway_port) is not int or not 0 <= gateway_port <= 65535:
        raise VMLabPrerequisiteError("Invalid model gateway port")
    root = root.expanduser().resolve(strict=True)
    state_path = root / "installed-state.json"
    if state_path.is_symlink() or state_path.stat().st_size > 1024 * 1024:
        raise VMLabPrerequisiteError("Unsafe installation state")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    refs = state.get("repositories") if isinstance(state, dict) else None
    sha = refs.get("rfdetoni/kitt-agent-cli") if isinstance(refs, dict) else None
    if not isinstance(sha, str) or not re.fullmatch(r"[a-f0-9]{40}", sha):
        raise VMLabPrerequisiteError("Installed Agent SHA is missing or malformed")
    python = root / ".venv-agent" / "bin" / "python"
    if not python.is_file():
        raise VMLabPrerequisiteError("Managed Agent interpreter missing")
    folder = root / "vm"
    if folder.is_symlink():
        raise VMLabPrerequisiteError("VM directory cannot be a symlink")
    folder.mkdir(mode=0o700, exist_ok=True)
    if folder.stat().st_uid != os.getuid() or folder.stat().st_mode & 0o077:
        raise VMLabPrerequisiteError("VM directory must be private")
    destination = folder / "debian-agent"
    if destination.exists() or destination.is_symlink():
        raise VMLabPrerequisiteError("Debian destination already exists; use kitt vm doctor to verify it")
    command = [
        str(python), "-m", "kitt.cli.main", "vm", "prepare",
        "--destination", str(destination), "--gateway-port", str(gateway_port),
        "--agent-sha", sha, "--image-sha512", image_sha512,
    ]
    result = subprocess.run(command, cwd=root, stdin=subprocess.DEVNULL, check=False, timeout=2700)
    if result.returncode:
        raise VMLabPrerequisiteError(f"Debian VM bootstrap failed (exit {result.returncode})")
    profile = destination / "profile.json"
    if profile.is_symlink() or not profile.is_file():
        raise VMLabPrerequisiteError("Debian VM profile missing after bootstrap")
    return profile
