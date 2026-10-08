# KITT Ecosystem 0.13.29 — WebChat owns token limits

The supplied Gemini logs showed successful contract generation in approximately 13 seconds, followed by a second Agent turn stopping before another provider request. Replaying the objective and generated eight-item contract reproduced a required-tool-schema budget failure caused by treating a local 8K profile placeholder as WebChat capacity.

| Component | Version | Change |
| --- | --- | --- |
| Agent CLI | 0.84.10 | Delegate reverse-proxy token limits, preserve prompts/tool observations, count intent once and log prompt failures |
| Reverse Proxy | 4.9.18 | Keep token estimates as telemetry; ignore legacy token quotas |
| Assistant | 0.1.32 / runtime 0.2.45 | Align runtime/CI and display WebChat context ownership |
| AI Workers, Evals, Evolution | 0.1.56 | Align Agent locks |
| Toolbox / Memory / Protocol | 0.4.3 / 0.9.3 / 0.9.2 | Existing compatible native and wire contracts |

Reverse-proxy turns have no local input/output token reserve or model-window ceiling. Per-turn, child and durable-goal token quotas do not enforce limits for this provider. max_tokens and max_prompt_tokens are not sent by Agent. Local profile placeholders do not truncate follow-up messages or tool observations, and they do not trigger automatic history compaction. WebChat controls its context and output behavior.

Token accounting remains available for observability. The UI displays WebChat ownership rather than a fabricated local capacity percentage. The typed envelope retains USER_INTENT provenance while input estimates count the user message once. Native/API providers retain their existing token budgets.

Attempts, model/tool calls, duration, costs, queue/session capacity, subagent counts, cancellation, approvals, byte limits, schema validation and workspace path bounds remain enforced. Context retrieval stays selective. High-risk review still precedes mutation, and required instructions and schemas remain intact.

Diagnostics record prompt-preparation success/failure and the exception type with turn/conversation scope. This new diagnostic excludes request bodies and exception content.

## Validation

269 Agent tests passed with one skipped; all 206 Proxy tests, TypeScript checks and production build passed. Regressions cover requests larger than local profile windows, one-token quotas, complete planning/review inputs, untruncated tool observations, parent/child/goal accounting, preserved operational limits, native token enforcement and WebChat UI rendering. Proxy lifecycle tests exceed the former million-token ceiling and ignore a legacy one-token allowance while retaining deadlines and attempt bounds.

Local checks also passed: 33 Workers/Evals/Evolution tests, 11 focused Assistant tests, 58 installer tests, compilation, critical Ruff checks, JavaScript syntax and Agent clean-room provenance verification. Release gates validate the compatible runtime/lifecycle, native composition and clean main/release installations. An authenticated fresh Gemini conversation was not run; the supplied provider response was replayed locally.

Immutable component revisions are in ecosystem.release.json. Main installation resolves main once per run; the release channel uses the manifest revisions.
