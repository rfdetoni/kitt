# KITT 0.15.12 — opt-in RE lab Full with Docker and Dockur Windows 11

## Official single-command installation

This command works on a Linux x86_64 host with **Docker Engine already installed and operational**, `/dev/kvm` and `/dev/net/tun` present, and KITT full native build prerequisites (Python 3.14, Node >=24, npm, a C compiler/linker, and Rust or rustup bootstrap):

```sh
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh |
  sh -s -- \
    --preset full \
    --channel release \
    --with-re-lab \
    --re-runtime docker \
    --re-profile full \
    --re-windows dockurr \
    --re-windows-version 11 \
    --yes
```

**This is real installer functionality, not an example of hypothetical flags.** The KITT installer does not install Docker Engine or grant sudo/root access. Missing prerequisites are rejected before source synchronization.

## What it creates

1. The pin-locked KITT full ecosystem and the REA CLI in a private KITT prefix. REA MCP still requires `kitt plugins enable kitt-rea` in the operator's authorized workspace.
2. A persistent **`kitt-re-full`** Docker container, based on the pinned `kitt/linux-re:full-0.86.10` image from the Agent CLI. The installer first tries GHCR pull and falls back to a local build if unavailable. This container runs as the host UID/GID, **without networking or Linux capabilities**, with HOME/cache in a temporary filesystem and only the dedicated RE lab workspace mounted.
3. A persistent **`kitt-re-win11`** Windows virtual machine via the official `dockurr/windows` image, with KVM, 8 GiB RAM, 4 vCPUs, 100 GiB virtual disk and browser console bound **only to 127.0.0.1:8006**. RDP is not published. Dockur downloads and installs Windows on first start; the installer does not assert that guest setup has finished.

The lab paths are `~/.local/share/kitt/re-lab/workspace`, `~/.local/share/kitt/re-lab/windows` and `~/.local/share/kitt/re-lab/windows.env` by default. Docker container images are pinned by ID when containers are created. Subsequent installer runs reuse tagged KITT-owned containers rather than deleting Windows disks or overriding container ownership.

## First-install credentials: known Dockur limitation

Dockur's `USERNAME` and `PASSWORD` environment variables are consumed during creation of the Windows unattended **installation answer file**. They are **not** a method for changing credentials of an already-installed Windows disk; see [Dockur documentation](https://github.com/dockur/windows/blob/master/docs/environment.md) and [issue #951](https://github.com/dockur/windows/issues/951).

KITT writes a `0600` environment file **before the first Windows container creation**, with:

- `USERNAME=Kitt`
- A generated random `PASSWORD` (stored, not printed in installer logs)
- `AUTOLOGIN=N` so the Windows account login is visible for verification
- `VERSION=11`, `LANGUAGE=Portuguese`, `RAM_SIZE=8G`, `CPU_CORES=4`, `DISK_SIZE=100G`, `SAMBA=N`

Read the password privately from `~/.local/share/kitt/re-lab/windows.env`; do not publish that file. Docker administrators can inspect container environment variables, so do not put high-value reusable credentials here.

For an unknown existing `/storage` Windows volume **without KITT first-install credentials**, setup fails without modifying or deleting the disk. To use a fresh account, back up the old Windows disk and create a new lab state (or change the account **inside Windows**); changing Docker environment variables alone does nothing to an installed guest. The operator must test the first actual Windows login to confirm successful provisioning; this cannot be proved by unit tests on Linux.

## Operations

```sh
docker ps --filter label=dev.kitt.re-lab=v1
docker exec -it kitt-re-full /bin/sh
docker logs -f kitt-re-win11
# Windows console: http://127.0.0.1:8006
cd ~/.local/share/kitt/re-lab/workspace
kitt plugins enable kitt-rea
kitt
```

The toolbox is **not a guest VM**, and sharing the kernel means it must not execute unknown hostile samples. Dockur's Windows guest can access a network to download the installer, so **do not use the default guest for malware execution** without establishing a separate network-isolated test setup. No automatic cross-guest SSH control, VM snapshot, REA invocation inside Windows or guest credential validation is claimed.

## Scope and validation

This release introduces the `installer/re_lab.py` provisioning path, explicit CLI flags and focused contract tests for flag parsing, first-install credential persistence, existing-disk protection and Docker container arguments. Existing component pins (Agent 0.86.13, REA 6.4.0, Proxy 5.1.2) remain unchanged. Real Windows boot and login require an operator host with Docker Engine, KVM, sufficient RAM/storage and Windows licensing.
