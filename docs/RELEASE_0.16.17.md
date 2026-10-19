# KITT 0.16.17 — ChatGPT rich editor integrity + RE guest MCP

Pins Reverse Proxy **5.4.10**, Agent CLI **0.88.12**, Assistant **0.1.57** / Runtime **0.4.12**, and AI Workers/Evals/Evolution **0.1.82**. Protocol 0.14.2, Memory 0.10.2, Toolbox 0.4.3 remain unchanged.

## Correções

- The ChatGPT UI composer may mutate short tool-result prompts (observed 1695 expected chars vs 1696 rendered), aborting an agent task after a successful `kitt_runtime` read. Reverse Proxy now attempts one bounded DOM correction for *all* prompt lengths, verifies the stable result and refuses to submit if still altered. No unsafe keyboard replay or duplicate submission.
- Added focused regression tests for corrected one-character drift, persistent drift and delayed editor reversion. Synthetic CI does not prove all live UI variants.
- Agent CLI provides an **opt-in, operator-only, read-only** RE guest MCP stdio adapter for Linux/Windows status and pinned Windows Oracle `probe.info` readiness. There is no model-controlled Docker, shell, source editing, arbitrary probes, or direct guest-to-guest traffic. Never expose the bridge to a Clean-Room implementation agent. See [RE_GUEST_MCP](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/RE_GUEST_MCP.md).
- All consumer revisions and Python/Rust/npm locks are pinned by exact Git SHAs in `ecosystem.release.json`.

## Validation limits

The repo CI checks test synthetic composer and RE guest boundary cases. The live authenticated ChatGPT-Web browser and actual Windows/Wine guest differential tests are environment-dependent and not claimed by this release. The operator must explicitly enable and authorize MCP; it is disabled by default.
