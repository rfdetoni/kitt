# KITT 0.15.7 — VM isolation and lifecycle corrections

## Coordinated versions

- Agent CLI **0.86.9**: authenticated noVNC, immutable QEMU image identity, runtime readiness, preserved logs, offline snapshots and host-controlled lab broker.
- Assistant runtime **0.3.7**: dependency and lock alignment; no changed daemon/protocol contracts.
- KITT root **0.15.7**: installer optional GHCR pull errors no longer falsely report the already-completed KITT install as failed.

## Resolved

- A strong random web viewer password now protects HTTP and WebSocket ingress, including other containers on the bridge. Use `kitt vm container credentials --profile ...` to obtain the password deliberately.
- VM startup verifies the service is live; concurrent starts are blocked and stopped-container logs remain available.
- The QEMU image is stored by immutable ID in the VM profile. Old 0.86.8 profiles must be backed up and recreated.
- Baselines can be created/restored offline with copied UEFI/TPM state and disk SHA-256 checks, using explicit restore confirmation.
- `kitt vm lab run` reuses pinned forced-command SSH probes for cross-guest differential testing, without general VM network or arbitrary remote shell.
- `--probe-port` enables opt-in localhost-forwarded SSH only; without it, guests remain without NICs. The user must provision authorized SSH guest accounts and host keys separately.
- Interactive `kitt vm create` asks for a backend and rejects Linux tool flags that are not applied to QEMU guest images.

## Validation

CI validates Python contracts, Windows package smoke, Docker/Podman and container builds. Live KVM guest boots, Podman rootless networking and full Windows/Wine/Frida cross-VM mission are host-dependent checks not simulated by static tests.
