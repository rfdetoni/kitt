# KITT 0.16.19 — Oracle SSH diagnostics and immutable dependency pins

## Component promotion

| Component | Version / revision | Scope |
| --- | --- | --- |
| Agent CLI | 0.88.15 / `037635b293bab033a375b8f180bd30072fd3de1f` | SSH error classifications, read-only handshake retry, Windows OEM bootstrap status, tests, runbook and early BrokenPipeError handling |
| Memory | 0.10.2 / `646a213672833c42f0e4eacf1faf048261e5a4c6` | CI-passing serde_json 1.0.154, sha2 0.11.1 and thiserror 2.0.21 dependency and Cargo.lock updates |
| Reverse Proxy | 5.4.10 / `9ea46443988fcf7fcb9beadd36d1ce41b2f21820` | CI-passing Playwright 1.64.1 dependency and package lock |

Protocol, Toolbox, Assistant and AI Workers retain the exact earlier immutable pins. This release changes the root VERSION/manifest only; it does **not** generate new installable Windows or Wine images.

## Windows laboratory operator acceptance

Run `kitt re lab status --json` and `kitt re lab verify --full` only after guest first-boot installation has completed. Expect categorized SSH failures instead of a bare exit 255. Verify C:\\KittOracle\\bootstrap.status and sshd from the local guest console when SSH is unavailable. `READY` requires a pinned-SSH `probe.info` response whose guest manifest matches the host pin. The differential pilot runs only after that handshake.

**CI limitation:** mock/unit smoke checks are not a real Dockur Windows/KVM end-to-end run; never claim Windows Oracle READY or guest attestation based on merged PR checks. No automatic destructive reset, credential rotation, host key bypass or replay of side-effecting probes.

## Verification

Agent CLI PRs [#117](https://github.com/rfdetoni/kitt-agent-cli/pull/117) and [#118](https://github.com/rfdetoni/kitt-agent-cli/pull/118), Memory PRs [#4](https://github.com/rfdetoni/kitt-memory/pull/4), [#15](https://github.com/rfdetoni/kitt-memory/pull/15) and [#16](https://github.com/rfdetoni/kitt-memory/pull/16), Reverse Proxy PR [#92](https://github.com/rfdetoni/kitt-reverse-proxy/pull/92). Each component merged only after available checks passed. Root integration CI must separately validate this immutable composition.
