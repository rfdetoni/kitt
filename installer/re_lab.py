"""Explicit, opt-in KITT reverse-engineering lab on Docker and Dockur.

The Windows account is configured only during the first unattended installation;
never claim that changing Docker environment variables updates an installed OS.
"""
from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys


class ReLabError(ValueError):
    """Provisioning error: no implicit root escalation or deletion of guest disks."""


def _run(argv: list[str], *, timeout: int = 60, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(argv, capture_output=True, text=True, check=False, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReLabError(f"Cannot run {argv[0]} {argv[1] if len(argv) > 1 else ''}: {exc}") from exc
    if check and result.returncode:
        detail = (result.stderr or result.stdout or "").strip()[-800:]
        raise ReLabError(f"Command failed: {argv[0]} {argv[1] if len(argv) > 1 else ''}: {detail}")
    return result


def check_re_lab(*, runtime: str, profile: str, windows: str, version: str) -> None:
    if runtime != "docker" or profile != "full" or windows != "dockurr" or version != "11":
        raise ReLabError("Initial RE lab supports --re-runtime docker --re-profile full --re-windows dockurr --re-windows-version 11")
    if sys.platform != "linux":
        raise ReLabError("Dockur RE lab requires a Linux host with Docker Engine and KVM")
    if not shutil.which("docker"):
        raise ReLabError("Docker Engine is missing; install Docker and grant access to its daemon")
    _run(["docker", "info"], timeout=20)
    for dev in ("/dev/kvm", "/dev/net/tun"):
        if not os.path.exists(dev) or not os.access(dev, os.R_OK | os.W_OK):
            raise ReLabError(f"{dev} must be accessible before provisioning Dockur; KITT will not use sudo/privileged")


def _image_id(tag: str) -> str:
    result = _run(["docker", "image", "inspect", "--format", "{{.Id}}", tag])
    image = result.stdout.strip()
    if not image.startswith("sha256:") or len(image) != 71:
        raise ReLabError(f"Could not pin image digest: {tag}")
    return image


def _existing_container(name: str, *, role: str, lab: Path) -> bool:
    result = _run(["docker", "container", "inspect", "--format", "{{json .Config.Labels}}", name], check=False)
    if result.returncode:
        if "No such object" not in result.stderr and "No such container" not in result.stderr:
            raise ReLabError(f"Cannot inspect existing container {name}: {result.stderr.strip()}")
        return False
    try:
        labels = json.loads(result.stdout)
    except (ValueError, TypeError) as exc:
        raise ReLabError(f"Cannot validate container ownership: {name}") from exc
    if not isinstance(labels, dict) or labels.get("dev.kitt.re-lab") != "v1" or labels.get("dev.kitt.re-role") != role or labels.get("dev.kitt.re-root") != str(lab):
        raise ReLabError(f"Container {name} already exists but is not owned by this KITT lab; no replacement performed")
    return True


def _start_existing(name: str) -> None:
    result = _run(["docker", "inspect", "--format", "{{.State.Running}}", name])
    if result.stdout.strip() != "true":
        _run(["docker", "start", name], timeout=90)


def _labels(lab: Path, role: str) -> list[str]:
    return ["--label", "dev.kitt.re-lab=v1", "--label", f"dev.kitt.re-role={role}",
            "--label", f"dev.kitt.re-root={lab}"]


def _private_dir(path: Path) -> None:
    if path.is_symlink():
        raise ReLabError(f"Unsafe lab directory is a symlink: {path}")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.is_symlink() or (path.stat().st_mode & 0o077):
        raise ReLabError(f"Lab directory must be private (0700): {path}")


def _create_secret(path: Path) -> None:
    if path.exists() or path.is_symlink():
        if path.is_symlink() or not path.is_file() or (path.stat().st_mode & 0o077):
            raise ReLabError("Existing Windows credentials are not a private regular file (0600)")
        return
    password = secrets.token_hex(16)
    lines = ["VERSION=11", "USERNAME=Kitt", f"PASSWORD={password}", "AUTOLOGIN=N",
             "LANGUAGE=Portuguese", "RAM_SIZE=8G", "CPU_CORES=4", "DISK_SIZE=100G", "SAMBA=N"]
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ReLabError("Windows credentials created concurrently; retry") from exc
    with os.fdopen(fd, "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")


def _toolbox_tag(python: Path) -> str:
    result = _run([str(python), "-c", "from kitt.vm_container import IMAGES; print(IMAGES['full'])"])
    tag = result.stdout.strip()
    if not tag.startswith("kitt/linux-re:full-") or "\n" in tag:
        raise ReLabError("Invalid full toolbox image tag from installed Agent")
    return tag


def provision_re_lab(root: Path, *, runtime: str, profile: str, windows: str, version: str) -> dict[str, str]:
    check_re_lab(runtime=runtime, profile=profile, windows=windows, version=version)
    root = root.expanduser().resolve()
    python = root / ".venv-agent" / "bin" / "python"
    if python.is_symlink() or not python.is_file():
        raise ReLabError("KITT Agent CLI must be installed before provisioning RE lab")
    lab = root / "re-lab"
    _private_dir(lab)
    with (lab / ".lock").open("a+") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ReLabError("Another KITT RE lab provisioner is running") from exc
        workspace, storage = lab / "workspace", lab / "windows"
        _private_dir(workspace)
        _private_dir(storage)

        toolbox_exists = _existing_container("kitt-re-full", role="toolbox", lab=lab)
        windows_exists = _existing_container("kitt-re-win11", role="windows", lab=lab)
        creds = lab / "windows.env"
        if not windows_exists and any(storage.iterdir()) and not creds.is_file():
            raise ReLabError("Windows disk state already exists without KITT first-install credentials. No account reset or disk deletion performed; use a fresh lab directory")
        if windows_exists and not creds.is_file():
            raise ReLabError("KITT Windows container exists without its original credentials file")

        if not toolbox_exists:
            tag = _toolbox_tag(python)
            pulled = _run([str(python), "-m", "kitt.cli.main", "vm", "container", "pull",
                           "--runtime", runtime, "--image", "toolbox", "--profile", "full"],
                          timeout=1800, check=False)
            if pulled.returncode:
                built = _run([str(python), "-m", "kitt.cli.main", "vm", "container", "build",
                              "--runtime", runtime, "--image", "toolbox", "--profile", "full"],
                             timeout=3000, check=False)
                if built.returncode:
                    raise ReLabError("Cannot pull or build KITT Linux RE full toolbox image")
            image = _image_id(tag)
            _run(["docker", "create", "--name", "kitt-re-full", "--restart", "unless-stopped",
                  "--network", "none", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                  "--user", f"{os.getuid()}:{os.getgid()}",
                  "--tmpfs", "/tmp:rw,nosuid,nodev,size=1g,mode=1777",
                  "--env", "HOME=/tmp", "--env", "XDG_CACHE_HOME=/tmp/.cache",
                  "--env", "XDG_CONFIG_HOME=/tmp/.config",
                  "--mount", f"type=bind,src={workspace},dst=/workspace", "--workdir", "/workspace",
                  *_labels(lab, "toolbox"), image, "sleep", "infinity"], timeout=120)
        _start_existing("kitt-re-full")

        if not windows_exists:
            _create_secret(creds)
            _run(["docker", "pull", "dockurr/windows"], timeout=1800)
            image = _image_id("dockurr/windows")
            _run(["docker", "create", "--name", "kitt-re-win11", "--restart", "unless-stopped",
                  "--device", "/dev/kvm", "--device", "/dev/net/tun", "--cap-add", "NET_ADMIN",
                  "--stop-timeout", "120", "--env-file", str(creds),
                  "--publish", "127.0.0.1:8006:8006",
                  "--mount", f"type=bind,src={storage},dst=/storage",
                  *_labels(lab, "windows"), image], timeout=120)
        _start_existing("kitt-re-win11")

        return {"workspace": str(workspace), "windows_url": "http://127.0.0.1:8006",
                "windows_user": "Kitt", "credentials_file": str(creds),
                "warning": "Dockur applies USERNAME/PASSWORD only during initial Windows installation; confirm login after setup. Docker inspect can reveal guest credentials."}
