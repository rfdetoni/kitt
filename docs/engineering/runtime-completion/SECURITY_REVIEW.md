# Security & Performance Review

## 1. Security Vulnerabilities Remediated

| Severity | Category | Location | Finding & Fix Applied |
|---|---|---|---|
| **High** | HTTP Request Smuggling | `kitt-assistant/apps/kittd/src/settings_web.rs`, `kitt/remote/server.py` | Duplicate `Host`/`Content-Length`/`Origin`/`X-Kitt-CSRF` headers previously overwrote earlier values; `Transfer-Encoding` was ignored. Now rejected fail-closed (`400 Bad Request`). |
| **High** | Cross-Site Request Forgery | `kitt-reverse-proxy/src/control-plane/server.ts`, `apps/kitt-rune/web/serve.mjs` | Control-plane mutations lacked strict Origin + custom action header verification. Enforced `isLoopbackHostHeader`, `isTrustedBrowserOrigin`, and `X-Kitt-Rune-Action: 1`. |
| **High** | Privilege Escalation | `kitt-agent-cli/kitt/runtime/core_runtime.py` | `_op_process_start` now rejects `is_path_scoped` and restricts `sandbox_profile` to `{"read-only", "workspace-write"}`; reserved key prefixes protected in `_is_operator_state_key`. |
| **Medium** | Socket & SSRF Hardening | `kitt-agent-cli/kitt/security/autopilot_broker.py`, `conversation_runtime.py` | Added `SO_PEERCRED` peer UID check + `0o600` socket mode; constrained remote `token_env` to `KITT_REMOTE_RUNTIME_TOKEN*` and applied `NetworkPolicy.validate_url`. |
| **Medium** | Zip-Bomb / Zstd Framing | `kitt-assistant/kitt/remote/cas_store.py`, `runtime_worker.py` | Enforced `DecompressionParameter.window_log_max=20`, bounded `max_length`, EOF checks, and trailing-frame rejection on Zstd streams. |
| **Low** | Null-Byte / Regex Bugs | `kitt-agent-cli/kitt/runtime/core_runtime.py`, `execution_sandbox.py`, `vm_supervisor.py` | Fixed literal string `"\\x00"` -> real NUL `"\x00"` in preflight checks and fixed `\w` regex escape. |

## 2. Preserved Security Invariants

- `computer.run` retains mandatory one-time `ASK` human approval; UI layers have no grant-bypass API.
- Worker bearer tokens, GitHub PATs (`KITT_GITHUB_MOUNT_TOKEN`), and AWS credentials (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`) remain strictly host-side and are stripped from Rune native/WebGPU projections.
- Crash recovery (`PersistentWakeScheduler.start`) resets interrupted `RUNNING` rows to pending state cleanly on daemon restart.

## 3. Performance & Bounded I/O Improvements

- `kitt-toolbox` (`edit.rs`, `search.rs`, `output.rs`): bounded file reads (`4 MiB + 1` cap) and O(n) single-pass byte scanning in `compress_generic`.
- `kitt-assistant` `settings_web.rs`: reuses shared pooled `reqwest::blocking::Client` rather than reallocating TLS/client state per poll.
- `kitt-rune/web/serve.mjs`: streams static assets (`createReadStream`) and suspends background polling when browser tab is hidden or offline.
- `kitt-assistant` `runtime_pool.py`: parallelized worker probing across up to 8 threads via `ThreadPoolExecutor` + 30s circuit breaker.
