# Hardware & OS Validation Report

## 1. Local Linux Host Capabilities

Probed directly via `/home/toni/otherProjects/kitt/kitt-assistant/packages/kitt-assistant-runtime/kitt/remote/runtime_worker.py` and `kitt/installer/platforms.py`:

- **OS / Architecture**: Linux x86_64
- **Python**: `3.14.4`
- **Rust**: `rustc 1.97.1` / `cargo 1.97.1` (+ `wasm32-unknown-unknown` target installed)
- **KVM**: `/dev/kvm` present
- **AMD GPUs (`discover_drm("amd")`) — LIVE HARDWARE VERIFIED**:
  - `AMD-0000:01:00.0`: render node `/dev/dri/renderD128`, VRAM `2,147,483,648` B total / `2,146,091,008` B free
  - `AMD-0000:05:00.0`: render node `/dev/dri/renderD129`, VRAM `2,147,483,648` B total / `531,374,080` B free

## 2. Blocked / Unavailable Hardware & Infrastructure (Honestly Declared)

| Component / Capability | Reason Unavailable Locally | Mitigation & Verification Performed |
|---|---|---|
| **NVIDIA Physical GPU (`nvidia-smi` / CUDA)** | No NVIDIA GPU or driver installed on local host | Validated discovery parser, Podman CDI, Docker `--gpus`, atomic lease rollback, and quantitative VRAM selection via mocked `nvidia-smi` + Docker/Podman CLI tests (`test_runtime_worker.py`, `test_gpu_cas_migration.py`). |
| **Intel XPU / Level Zero GPU** | No physical Intel GPU on host | Tested DRM `0x8086` discovery, `ZE_AFFINITY_MASK`, and unknown `None` VRAM policy via sysfs fixtures. |
| **QEMU Debian Minimal Real Boot** | `qemu-system-x86_64` not installed on host | Verified download redirect allowlist, GPG + SHA-512 verification helpers, cloud-init & non-root SSH hardening, Python `>=3.14` tuple check, and installer integration via unit/integration tests (`test_real_debian_qemu.py`). |
| **Local Docker / Podman Daemons** | Local Docker socket inactive; `podman` missing locally | Executed real Docker and Podman container runtime smoke jobs inside `kitt-agent-cli` GitHub Actions PR #224 (`docker runtime smoke` & `podman runtime smoke` both passed). |
| **Windows / macOS LAN Server (`192.168.100.51`)** | Unreachable from current network (`No route to host`) | Multi-OS build/lifecycle verified on official `ubuntu-latest`, `windows-latest`, and `macos-latest` GitHub Actions runners (`kitt-assistant` & `kitt`). |
