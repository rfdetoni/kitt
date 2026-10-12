"""Opt-in VM lab prerequisite checks; never changes the host or installs packages."""
from __future__ import annotations

import os
import shutil
import sys


class VMLabPrerequisiteError(ValueError):
    pass


def check_vm_lab() -> dict:
    if sys.platform != "linux":
        raise VMLabPrerequisiteError("VM autonomy requires a Linux host running QEMU")
    missing = [
        program for program in ("qemu-system-x86_64", "qemu-img", "ssh")
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
        "guest_image_required": True,
        "note": "Installer does not create a VM image or relax host security; use kitt vm doctor --profile.",
    }
