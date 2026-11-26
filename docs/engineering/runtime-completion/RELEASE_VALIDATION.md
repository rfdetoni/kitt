# Release Validation (`v0.16.76`)

## 1. Root Cause of Prior Release Failure (`45810579540`)

Prior PR #124 modified `ecosystem.release.json`, `installer/cli.py`, and `installer/vm_lab.py` while keeping `VERSION` at `0.16.75` (tag `v0.16.75` already existed on `fcc8052`), causing `Automatic Release` to fail closed.

## 2. Synchronized Ecosystem Manifest (`0.16.76`)

`VERSION` (`0.16.76`) and `ecosystem.release.json` pin all 7 component repositories to exact merged `main` commits verified by `scripts/validate_ecosystem_main.py --release` and `scripts/validate_ecosystem_main.py --check-main-heads`:

- `protocol`: `2cb05bb03e54eb2dc5f81bf151edcbd207ff194e`
- `memory`: `fae5aee3a3ef889babe612bdd842c3c4c3611c85`
- `toolbox`: `b8f42753ca64f5f79d5653aae5e4dffb03aecd5f`
- `assistant`: `f6fa0650f30f5ec730992d16630a2fa9e6e06fef`
- `agent-cli`: `8dd1827763cf3a9f8aff373b6e9fd8d77ee146b4`
- `ai-workers`: `2e96b47f411be6797fc736778c2516b95da0175c`
- `reverse-proxy`: `8b0ee8873dd12d5c749a751ffe6a054f91fc9d6f`

## 3. Release Artifacts & Attestation (`.github/workflows/release.yml`)

Each release tag (`v0.16.76`) packages and publishes:
- `ecosystem.release.json`
- `kitt-installer-v0.16.76-linux.tar.gz`
- `kitt-installer-v0.16.76-macos.tar.gz`
- `kitt-installer-v0.16.76-windows.zip`
- `SHA256SUMS.txt` (verified in CI via `sha256sum -c SHA256SUMS.txt`)
- GitHub Artifact Attestation (`actions/attest@1e69f48acb82d1966a394da916b4c1698aa569d6`)
