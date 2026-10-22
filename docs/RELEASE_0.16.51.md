# KITT 0.16.51 — Gemini Web no-action recovery

## Observed incident

During the 2026-10-22 `mbs-wine` run, the host successfully performed `process.run(argv=['ls','-la','mbs-wine'])`. The subsequent Gemini Web completion returned `{}` and Reverse Proxy 5.4.22 rejected it with recoverable `agent_contract_empty_action`. Further automatic contract retries submitted the same objective repeatedly (five no-action failures total); one response took about 110 seconds because the tap did not match and the browser used DOM capture. The model also selected bare `.gitignore` relative to the parent workspace root instead of `mbs-wine/.gitignore`.

## Changes

- **Agent CLI 0.88.51:** allow the existing FailoverLLMClient to try a *configured and trusted* alternate provider only after a confirmed empty-action error with no emitted partial output. It never replays a tool call or broadens an endpoint allowlist.
- When no alternate provider succeeds, contract GoalStepExecutor marks the item BLOCKED_ENV for explicit continuation rather than requeueing the same broken task rapidly. Host receipts and earlier workspace changes remain intact.
- Clarify the model-visible root-relative path contract; prefer `repo.list` for structured directory discovery.
- **Assistant Runtime 0.4.40:** synchronize its minimum agent version, immutable Git SHA in Python `uv.lock` and two CI checkouts.
- **Reverse Proxy 5.4.22:** remains unchanged, rejecting `{}` without speculative model repair.

## Validation and limits

Agent PR #143 passed critical tests and Windows/Docker/Podman smoke. Assistant PR #66 passed Python, core, HUD and Ubuntu/macOS/Windows lifecycle checks. Ecosystem CI must validate end-to-end main/release installation and the exact merged SHAs before publication.

This release is a containment and safe failover improvement, not a claim that Gemini Web will stop producing empty completions. UI tap correlation and the `mbs-wine` clone/Windows Oracle workflow still require a real authenticated host reproduction.
