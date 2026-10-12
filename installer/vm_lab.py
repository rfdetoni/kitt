"""Opt-in, unattended Debian agent VM bootstrap; never installs host packages."""
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


TOOLS = ("qemu-system-x86_64", "qemu-img", "cloud-localds",
         "ssh", "ssh-keygen", "ssh-keyscan", "git")


def check_vm_lab() -> dict:
    if sys.platform != "linux":
        raise VMLabPrerequisiteError("Debian VM autonomy needs a Linux host")
    missing = [program for program in TOOLS if not shutil.which(program)]
    if missing:
        raise VMLabPrerequisiteError(
            "Missing VM bootstrap dependencies: " + ", ".join(missing)
            + ". Install qemu-system-x86, qemu-utils, cloud-image-utils, "
              "openssh-client and git with your Linux package manager."
        )
    return {
        "ready": True,
        "kvm": os.access("/dev/kvm", os.R_OK | os.W_OK),
        "guest_image_required": False,
        "note": "Debian 13 guest is provisioned once by kitt vm prepare after Agent installation.",
    }


def prepare_guest(root: Path, *, gateway_port: int = 3000) -> Path:
    """Run provisioning through the installed KITT Agent CLI, pinned to installed SHA."""
    check_vm_lab()
    if type(gateway_port) is not int or not 0 <= gateway_port <= 65535:
        raise VMLabPrerequisiteError("Invalid model gateway port")
    root = root.expanduser().resolve(strict=True)
    state = json.loads((root / "installed-state.json").read_text(encoding="utf-8"))
    if not isinstance(state, dict) or not isinstance(state.get("repositories"), dict):
        raise VMLabPrerequisiteError("Agent installation state missing")
    agent_sha = state["repositories"].get("rfdetoni/kitt-agent-cli")
    if not isinstance(agent_sha, str) or not re.fullmatch(r"[a-f0-9]{40}", agent_sha):
        raise VMLabPrerequisiteError("Installed Agent SHA is missing or malformed")
    python = root / ".venv-agent" / "bin" / "python"
    if not python.is_file():
        raise VMLabPrerequisiteError("Managed Agent Python interpreter missing")
    folder = root / "vm"
    if folder.is_symlink():
        raise VMLabPrerequisiteError("VM directory cannot be a symlink")
    folder.mkdir(mode=0o700, exist_ok=True)
    if os.name == "posix":
        os.chmod(folder, 0o700)
    destination = folder / "debian-agent"
    command = [
        str(python), "-m", "kitt.cli.main", "vm", "prepare",
        "--destination", str(destination),
        "--gateway-port", str(gateway_port),
        "--agent-sha", agent_sha,
    ]
    result = subprocess.run(command, cwd=root, stdin=subprocess.DEVNULL,
                            check=False, timeout=2700)
    if result.returncode:
        raise VMLabPrerequisiteError(
            f"Debian VM bootstrap failed (exit {result.returncode}); "
            "inspect guest bootstrap diagnostics and retry."
        )
    profile = destination / "profile.json"
    if not profile.is_file():
        raise VMLabPrerequisiteError("Debian VM profile missing after bootstrap")
    return profile
