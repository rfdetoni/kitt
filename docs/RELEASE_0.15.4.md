# K.I.T.T. Ecosystem 0.15.4 — VM-autonomous reverse-engineering laboratory

## Coordinated versions

- Agent CLI **0.86.6** (`8c5bfcd4d155035ffcaaecef1b56ad53b617e9fb`): Linux QEMU VM supervisor, operator-owned immutable guest image SHA, snapshot isolation, fixed SSH worker, Windows/Wine differential mission runner, optional Ghidra/Frida guest adapters, SQLite evidence querying.
- Assistant runtime **0.3.4**: runtime lock aligned to Agent 0.86.6, without native/protocol contract changes.
- Installer **0.15.4**: optional `--with-vm-lab` prerequisite verification; immutable release manifest pins compatible Agent and Assistant revisions.
- Protocol, Memory, Toolbox, AI Workers and Reverse Proxy remain at their previous compatible SHA pins.

## Autonomy and controls

`kitt vm doctor --profile <private-profile>` validates host prerequisites,
image hash and bounded VM profile. `kitt vm run --profile <private-profile>
--goal <objective>` runs an Agent durable contract inside a disposable
QEMU guest prepared by an operator, with `restrict=on` networking,
loopback-only SSH and optional explicit local model gateway forward.

Internal guest execution can use `--allow all` without giving the guest
access to host files, SSH agent, container socket, arbitrary Internet
egress, hypervisor configuration or the GitHub publication credential.

**Important**: this is an experimental, operator-provisioned Linux VM setup.
VM images, SSH host identities, and test binaries are not auto-generated.
Real QEMU + Windows + Wine + Ghidra/Frida E2E and host-side artifact
promotion are outstanding and MUST NOT be claimed verified by CI alone.

## Install and release verification

```sh
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh \
  | sh -s -- --preset full --channel release --with-vm-lab --yes
```

Prerequisites: Linux host, QEMU system x86_64, qemu-img and OpenSSH
client. The installer does not install privileged host packages.
Existing users can install without `--with-vm-lab`; it remains opt-in.

Run `kitt vm doctor` before any mission. See `docs/VM_AUTONOMY_INSTALL.md`.
