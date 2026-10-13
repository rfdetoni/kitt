"""Optional container-based QEMU VM prerequisites and explicit prebuilt image fetch."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys


class VMContainerError(ValueError):
    pass


def check_container_runtime(runtime: str) -> dict:
    if sys.platform != "linux":
        raise VMContainerError("QEMU Docker/Podman backend requires Linux host")
    if runtime not in ("docker", "podman"):
        raise VMContainerError("Choose Docker or Podman")
    binary = shutil.which(runtime)
    if not binary:
        raise VMContainerError(f"Missing {runtime}. Install the container runtime first.")
    try:
        result = subprocess.run([binary, "info"], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, check=False, timeout=20)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise VMContainerError(f"{runtime} is not available to current user") from exc
    if result.returncode:
        raise VMContainerError(f"{runtime} daemon/rootless runtime is not ready")
    return {
        "runtime": runtime, "ready": True,
        "kvm_accessible": os.access("/dev/kvm", os.R_OK | os.W_OK),
        "requires_user_image": True,
        "note": "Windows/Linux ISOs are supplied by operator. No privileged containers are installed.",
    }


def pull_prebuilt(root: Path, *, runtime: str, profile: str) -> None:
    check_container_runtime(runtime)
    if profile not in ("base", "wine", "full"):
        raise VMContainerError("Unknown RE image profile")
    python = root / ".venv-agent" / "bin" / "python"
    # The managed venv may expose its interpreter through bin/python symlinks.
    if not python.is_file():
        raise VMContainerError("Managed KITT Agent interpreter unavailable")
    for image in ("qemu", "toolbox"):
        argv = [str(python), "-m", "kitt.cli.main", "vm", "container", "pull",
                "--runtime", runtime, "--image", image]
        if image == "toolbox":
            argv.extend(["--profile", profile])
        result = subprocess.run(argv, stdin=subprocess.DEVNULL,
                                check=False, timeout=1800)
        if result.returncode:
            raise VMContainerError(
                "Prebuilt image not available. Try: "
                f"kitt vm container build --runtime {runtime} --image {image}"
            )
