# KITT 0.16.50 — Git metadata planning and Gemini no-action recovery

## Incidents

The 2026-10-22 `mbs-wine` automatic contract failed with `Automatic contract planning failed: Protected workspace path component: .git`. The plan validator passed model-authored validation scopes to the protected workspace filesystem. The planner caught `ValueError` for retries, but the policy raised `PermissionError` before the bounded revision could run.

An independent Gemini Web interaction returned `{}` instead of the required agent action envelope. The Reverse Proxy submitted a speculative repair, observed a static partially streamed answer, and remained occupied until the request was cancelled.

## Fixes and boundaries

- **Agent CLI 0.88.50** turns forbidden model-generated scopes into actionable structural errors for a bounded plan revision; prompts forbid protected metadata in validation paths. `.git` access, traversal, and command authorization remain denied by the original filesystem and execution policies.
- **Reverse Proxy 5.4.22** stops on an empty JSON action with HTTP 409 `agent_contract_empty_action`, recoverable `continue`, and **no host tool execution**. Non-empty malformed actions retain existing validation/recovery.
- **Agent CLI 0.88.50** additionally rejects public Git checkout bundled in a network-enabled `bash -c` without opening an unnecessary generic-network approval modal. It responds with actionable guidance to issue `repo.create_directory`, direct `git init`, and a separate direct public Git `git clone` per repository. Arbitrary network shells still require approval.
- **Assistant Runtime 0.4.39** synchronizes its Agent dependency range, `uv.lock` Git commit and two CI checkouts.
- **Ecosystem 0.16.50** pins the exact merged component commits for reproducible release installation. The remaining protocol, memory, toolbox and AI workers pins stay immutable.

## Evidence and limits

Agent CLI critical, Docker, Windows and Podman checks passed; Reverse Proxy CI and Docker passed. Assistant CI passed; ecosystem CI must pass before integrating the release manifest. The authenticated Gemini Web browser, actual Wine clone, KITT VM, and Windows Oracle are not exercised by those hosted checks.

Transport cancellation after a user-triggered `cancel_turn` is expected behavior, not evidence that Git failed. A Git remote URL accidentally ending in `%60` should be corrected to `.git` in the input; the KITT runtime must not silently rewrite arbitrary remote URLs.
