# KITT Ecosystem 0.13.29

The supplied Gemini logs showed successful contract generation in approximately 13 seconds, followed by a second Agent turn stopping during prompt preparation. Replaying the exact objective and generated eight-item contract reproduced a required-tool-schema budget failure: the pre-mutation review inherited a 4,096-token coding output reserve on an 8,192-token profile.

| Component | Version | Change |
| --- | --- | --- |
| Agent CLI | 0.84.10 | Bound review output to 2,048 tokens, propagate per-request ceilings, count intent once, and log prompt-preparation failures |
| Assistant | 0.1.32 / runtime 0.2.45 | Align runtime lock and CI to the corrected Agent revision |
| AI Workers, Evals, Evolution | 0.1.56 | Align Agent locks |
| Reverse Proxy | 4.9.17 | Existing compatible transport |
| Toolbox / Memory / Protocol | 0.4.3 / 0.9.3 / 0.9.2 | Existing compatible native and wire contracts |

The original objective, validated items and required policy context remain intact. High-risk review still precedes mutation; read-only capabilities, cancellation and host verification continue to apply. Output ceilings are scoped to each request, so parallel turns do not modify a shared LLM profile. The full typed envelope retains USER_INTENT for provenance while input estimates count its user message once.

Diagnostics record whether prompt preparation succeeded and emit the exception type with turn/conversation identifiers on terminal failures. Request bodies and exception content are excluded from this new diagnostic.

## Validation

The new regression exercised real planning and review with an 8K profile and a deterministic provider response. It failed before the fix and now completes both calls while preserving the objective, all items and input-plus-output bounds. Client checks cover reduced output ceilings, configured limits, default calls and shared-profile immutability. Oversized requests still fail with a scoped terminal diagnostic.

Local checks passed: 266 Agent tests with one skipped, 33 Workers/Evals/Evolution tests, 11 focused Assistant tests, compilation, critical Ruff checks and Agent clean-room provenance verification. Release gates also exercise the compatible Assistant runtime/lifecycle, native composition and root installer. A fresh authenticated Gemini browser conversation was not run; the provided provider response was replayed locally.

Immutable component revisions are in ecosystem.release.json. Main installation resolves main once per run; the release channel uses the manifest revisions.
