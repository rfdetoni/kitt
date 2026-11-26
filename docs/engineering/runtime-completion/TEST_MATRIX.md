# Verification & Test Matrix

| Repository | Check / Suite | Scope | Result |
|---|---|---|---|
| `kitt-protocol` | `cargo fmt --check`, `cargo clippy --locked -- -D warnings`, `cargo test --locked` | Rust runtime & KAP/2 contracts | **15 passed** |
| `kitt-protocol` | `export_agent_contract.py --check`, `export_context_schema.py --check`, `check_contract_parity.py`, Python `unittest` | Cross-language parity & schemas | **51 + 1 passed** |
| `kitt-protocol` | `npm run typecheck && npm test` + KAP/2 5000-case fuzz | TypeScript SDK & framing | **PASS** (0 errors) |
| `kitt-memory` | `cargo fmt --check`, `cargo clippy --locked`, `cargo test --workspace --locked` | Core & SQLite memory | **50 passed (11 suites)** |
| `kitt-toolbox` | `cargo fmt --all --check`, `cargo clippy --locked`, `cargo test --workspace --locked` | Bounded edit/search/output | **23 passed** |
| `kitt-reverse-proxy` | `npm run verify`, `npm run benchmark:core` | VM gateway scoping, CSRF, TS | **351/351 passed** |
| `kitt-agent-cli` | `ruff check`, `compileall`, `verify_cleanroom.py`, `pytest` (`test_runtime_completion_p0_p1.py`, `test_remote_artifact_cache.py`) | Debian VM, Zstd, security, RPC | **PASS** (CI 3/3 ok: critical, docker, podman) |
| `kitt-ai-workers` | `unittest` (`test_protocol`, `test_stt_server`, `kitt-evolution`, `kitt-evals`), `uv lock --check` (x3), `ruff`, `kitt_workers.benchmark` | STT ROCm/XPU/IPv6, evals, evo | **35 passed** (22+10+3; CI critical ok) |
| `kitt-assistant` (Rust/Node) | `cargo test --workspace --locked`, `cargo clippy --locked`, `kitt-rune` `--lib`, `wasm32-unknown-unknown` check, `serve.test.mjs`, `control_center_r3.test.mjs` | Control plane, HTTP smuggling, Rune | **44 + 5 Rust passed; 1 + 12 Node passed; wasm32 0 errors** |
| `kitt-assistant` (Python/HW) | `pytest` clean venv, `uv lock --check`, `ruff`, live `discover_drm('amd')`, `--local-suite` benchmark | GPU leases, CAS/CDC, S3 SigV4 | **80 passed + 2 subtests; 2 real AMD GPUs detected** |
| `kitt` (Installer) | `validate_ecosystem_main.py` (`--release`, `--check-main-heads`), `validate_architecture.py`, `unittest`, `ruff`, `--capabilities`, `--dry-run` | Release pins, rollback, uninstall | **92 passed** (`0.252s`); all 7 live `main` SHAs matched |
