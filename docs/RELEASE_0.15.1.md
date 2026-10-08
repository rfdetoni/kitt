# KITT ecosystem 0.15.1 — Assistant immutable dependency pins

## Symptom

```text
K.I.T.T. install failed: Assistant Cargo.lock does not match release pins: kitt-protocol
```

This blocked `install.sh --preset full --channel release --yes`.

## Cause

The 0.15.0 manifest pinned Protocol 0.11.0 at `ed096ba68368c8b449c1baf715e0000871ec9fb9`, but Assistant 0.1.33 still pinned the previous Protocol 0.10.0 commit in **both** Rust Cargo locks, the HUD npm lock, and its Python runtime `uv.lock`. Assistant runtime also required `kitt-agent-cli>=0.85.0,<0.86` while the release selected Agent CLI 0.86.0. The installer intentionally fails closed on mismatched source revisions.

## Resolution

- Upgrade Assistant to 0.1.34 and companion runtime to 0.3.1.
- Align root/HUD Cargo locks and HUD package-lock with Protocol 0.11.0 and its immutable source SHA.
- Align Python uv.lock and runtime requirement with Agent CLI 0.86.0 and Protocol 0.11.0.
- Pin the exact merged Assistant revision in the root release manifest.
- Keep the root release-pin validators enabled; do not resolve this by removing the check.

## Acceptance

Release-checkout dependency graph and lock files must match the manifest. Verify Rust `--locked` compilation, HUD `npm ci`/build, Python `pip check` and critical tests, root ecosystem policy, and the release-channel Assistant installation smoke. End-to-end `--preset full --channel release` is the definitive acceptance gate. Checks may validate correct wiring but do not prove a local Linux installation until the full installer runs successfully.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | sh -s -- --preset full --channel release --yes
```
