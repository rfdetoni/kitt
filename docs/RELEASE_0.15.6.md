# KITT ecosystem 0.15.6 — Docker/Podman QEMU VM guests and prebuilt Linux RE images

## Coordinated modules

- KITT Agent CLI **0.86.8**: optional `kitt vm create --backend docker|podman`, QEMU in containers with noVNC, operator ISO/QCOW2, bounded host-loopback viewer and read-only guest ISO mount.
- KITT Assistant runtime **0.3.6**: compatible Agent lower bound and source SHA/uv.lock; no daemon/protocol updates.
- KITT root **0.15.6**: installer preflight `--with-vm-containers`, `--vm-container-runtime`, optional `--vm-pull-images`, release pins and documentation.
- Protocol, memory, reverse-proxy, toolbox, AI workers unchanged and pinned to previously compatible commits.

## Prebuilt Linux reverse-engineering images

- `base`: Debian 13, GDB, LLDB, gcc/clang, binutils, Java, Python and build tooling.
- `wine`: plus Wine64 and MinGW.
- `full`: plus Frida 17.23.3, Frida Tools 14.11.0 and Ghidra 12.1.4 fetched with an SHA-256 checksum verified from the upstream release.
- Separate QEMU/noVNC runner image builds VM from user-provided ISO/QCOW2. The toolbox is **not** a VM and should not execute unknown malware directly.

The GitHub Actions image workflow builds/tests these packages and attempts GHCR publication on main. Availability of GHCR packages must be verified after the workflow completes; `kitt vm container build` always provides a local alternative.

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh \
  | sh -s -- --preset full --channel release --with-vm-containers \
     --vm-container-runtime podman --yes
```

`--vm-pull-images` enables explicit image pulls. It does not silently grant elevated privileges, install Docker/Podman itself or fetch Windows ISO.

## Gates

CI exercises parser, host capabilities/ports, copied disks, Docker/Podman command contracts, QEMU entrypoint shell syntax, builds QEMU/noVNC and full RE toolchain. Live Windows/Linux QEMU guest boot with KVM, rootless Podman and artifact export remain separate environmental validation gates.

See [Docker/Podman guide](VM_CONTAINERS_DOCKER_PODMAN.md), [complete VM guide](GUIA_COMPLETO_VMS_KITT.md) and the Agent repository's technical documentation.
