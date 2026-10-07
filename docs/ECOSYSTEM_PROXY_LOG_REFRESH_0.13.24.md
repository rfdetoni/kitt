# K.I.T.T. Ecosystem 0.13.24 — managed Reverse Proxy log-directory refresh

## Snapshot

| Component | Version / role | Revision |
| --- | --- | --- |
| Agent CLI | 0.84.3 | `87d3954adbeb37a21eae367cd30e3499c3fdb162` |
| Assistant | 0.1.26 | `299f3b903fd17d69b5a013c095cfb3f71534b98b` |
| Assistant runtime | 0.2.39 | included in Assistant revision |
| AI Workers / Evals / Evolution | 0.1.49 | `8e8fec72ce814109726338d9004cf39da8f32f2a` |
| Reverse Proxy | 4.9.16 | `cc03515b90afcc995699969e86cc22539d8b7dc7` |
| Protocol | 0.9.1 | unchanged |
| Memory | 0.9.2 | unchanged |
| Toolbox | 0.4.2 | unchanged |

## Root cause

Agent CLI 0.84.2 correctly forwarded `log_level`, `log_content`, `log_file` and owner metadata when starting a managed Reverse Proxy. Reverse Proxy 4.9.16 also correctly derives a dedicated `reverse-proxy-<instance>.log` next to the Agent log.

The remaining failure was process lifetime across upgrades. The resident control plane can outlive the installed package. A 4.9.15 control plane reports the same schema-v1 health endpoint and accepts `service.start`, but its request decoder does not know the newer managed logging fields. It therefore ignores them and falls back to `~/.kitt-reverse-proxy/logs`.

## Correction

Agent CLI 0.84.3 refreshes the resident control plane once per Agent process before the first managed start/restart:

1. stop the resident control plane;
2. wait until its health endpoint disappears;
3. ensure a new control plane from the currently installed `kitt-reverse-proxy` executable;
4. start the managed service with the Agent logging/owner settings.

The Agent parses the returned `logFile` and requires its parent directory to equal the directory of `KITT_LOG_FILE`. A missing or mismatched path stops the just-created service and fails explicitly.

Managed restart is stop + start with current Agent logging, so instances created by older control-plane versions migrate to the correct log directory.

## Expected behavior

With:

`kitt --log-level 2 --log-file ~/.kitt/logs/agent-cli.log`

a Reverse Proxy started from KITT writes to a dedicated file such as:

`~/.kitt/logs/reverse-proxy-chatgpt-3001.log`

The Agent and Proxy intentionally do not write to the same file.

## Validation

Agent CLI 0.84.3 passed PR Checks and Docker, including release-critical, Agent ownership, Windows package smoke, Docker runtime smoke and Podman runtime smoke. Regression coverage verifies stale-control refresh, returned log-path validation and restart with current logging.

Assistant 0.1.26/runtime 0.2.39 passed Python runtime, Rust core, HUD and Linux/macOS/Windows lifecycle CI against the exact Agent revision. AI Workers 0.1.49 passed its critical CI after lock alignment.

The root ecosystem integration is the final immutable composition gate.
