"""Explicit, opt-in KITT reverse-engineering lab on Docker and Dockur.

The Windows account is configured only during the first unattended installation;
never claim that changing Docker environment variables updates an installed OS.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
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
        if not os.path.exists(dev):
            raise ReLabError(f"{dev} is missing. Dockur requires hardware virtualization and TUN support")


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


_WINDOWS_SETTINGS = (
    "VERSION=11\nUSERNAME=Docker\nPASSWORD=admin\nAUTOLOGIN=Y\n"
    "LANGUAGE=Portuguese\nRAM_SIZE=8G\nCPU_CORES=4\nDISK_SIZE=100G\nSAMBA=N\n"
)


def _ensure_windows_settings(path: Path, *, fresh_guest: bool = False) -> None:
    """Use Dockur's documented defaults; never change an installed guest's account."""
    if path.exists() or path.is_symlink():
        if path.is_symlink() or not path.is_file() or (path.stat().st_mode & 0o077):
            raise ReLabError("Existing Windows settings are not a private regular file (0600)")
        if path.read_text(encoding="utf-8") == _WINDOWS_SETTINGS:
            return
        if not fresh_guest:
            raise ReLabError(
                "Existing Windows lab uses previous credentials or autologin settings. "
                "Changing Docker variables will not update an installed Windows guest. "
                "Back up the Windows disk and reprovision a fresh guest (see docs/RELEASE_0.15.14.md)."
            )
        path.write_text(_WINDOWS_SETTINGS, encoding="utf-8")
        return
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ReLabError("Windows settings created concurrently; retry") from exc
    with os.fdopen(fd, "w", encoding="utf-8") as file:
        file.write(_WINDOWS_SETTINGS)


def _toolbox_tag(python: Path) -> str:
    result = _run([str(python), "-c", "from kitt.vm_container import IMAGES; print(IMAGES['full'])"])
    tag = result.stdout.strip()
    if not tag.startswith("kitt/linux-re:full-") or "\n" in tag:
        raise ReLabError("Invalid full toolbox image tag from installed Agent")
    return tag


def provision_re_lab(root: Path, *, runtime: str, profile: str, windows: str, version: str,
                     oracle: bool = False, oracle_recreate: bool = False) -> dict[str, str]:
    check_re_lab(runtime=runtime, profile=profile, windows=windows, version=version)
    import fcntl  # Linux-only; do not prevent a helpful platform error on Windows
    root = root.expanduser().resolve()
    python = root / ".venv-agent" / "bin" / "python"
    # python -m venv normally symlinks bin/python to a usable interpreter.
    if not python.is_file():
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
        # Fail before touching the toolbox if an installed guest still uses the old
        # random password or disabled autologin. Never overwrite a guest disk.
        if windows_exists:
            _ensure_windows_settings(creds)
        elif creds.exists() or creds.is_symlink():
            _ensure_windows_settings(creds, fresh_guest=not any(storage.iterdir()))

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

        oracle_plan = None
        if oracle:
            # Do not infer guest configuration from container state.
            _ensure_windows_settings(creds, fresh_guest=not any(storage.iterdir()))
            _run(["docker", "pull", "dockurr/windows"], timeout=1800)
            command = [str(python), "-m", "kitt.cli.main", "re", "oracle", "bootstrap",
                       "--yes", "--accept-license"]
            if oracle_recreate:
                command.append("--recreate")
            # Installer and Agent use the same RE lab lock; yield it to the
            # child, whose bootstrap owns locking and checks container identity.
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
            try:
                result = _run(command, timeout=400, check=False)
            finally:
                try:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError as exc:
                    raise ReLabError("Concurrent RE lab change detected after Oracle bootstrap") from exc
            if result.returncode:
                raise ReLabError("Windows Oracle bootstrap failed; inspect KITT logs")
            try:
                oracle_plan = json.loads(result.stdout)
            except ValueError as exc:
                raise ReLabError("Oracle bootstrap did not return expected JSON") from exc
        elif not windows_exists:
            _ensure_windows_settings(creds, fresh_guest=not any(storage.iterdir()))
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
                "windows_user": "Docker", "credentials_file": str(creds),
                "warning": "Only an isolated test Windows VM; SSH/Oracle readiness is not assumed.",
                **({"oracle_hosts": oracle_plan["hosts"],
                    "oracle_manifest_sha256": oracle_plan["manifest_sha256"]}
                   if oracle_plan else {})}
