# Ecosystem 0.15.0 — KAP/1 WebChat model contract

**Components:** Protocol 0.11.0, Reverse Proxy 5.1.0, Agent CLI 0.86.0.

## Changed
- Model-visible Agent contract v4 emits one bounded KAP/1 textual action, replacing model-generated JSON envelopes.
- Typed scalar and multiline `TEXT` fields preserve code, quotes, backslashes and indentation without extra JSON escaping.
- Plans, architect handoffs and review results use typed structured `content` fields. The proxy generates JSON/OpenAI tool calls after validation; JSON remains a trusted host-side representation.
- 64 KiB maximum WebChat action payload; oversized changes must be split into smaller operations.
- Ambiguous responses, duplicate fields and repaired actions that drift from the original intent are rejected, not executed.
- The Agent still owns approvals, tool authorization, workspace boundaries, verification evidence, budget policies and execution lifecycle.
- Integration and regression tests cover round trips, type checking, protocol parity and bounded repair behavior.

## Upgrade and compatibility
Update the entire ecosystem together, ideally through the root installer and release SHA manifest. Contract v3 is not compatible with v4; there is intentionally no model-output fallback to the previous JSON envelope. Restart the Agent and Reverse Proxy after upgrade so sessions no longer hold the old contract.

## Validation
The modules must pass their required CI gates (Protocol Rust/SDK parity, Proxy typecheck/contracts/browser packaging, Agent release-critical contracts plus packaging). Do not promote this root release until all component checks are green and `ecosystem.release.json` pins the exact merged commit SHAs.

## Limitations
KAP/1 is an output-grammar and validation change. Its token reduction and error-rate improvement have **not** been quantified by an equivalent-model, equivalent-task benchmark; treat these as design goals, not measured results. User-visible backpressure, model refusal behavior and provider-specific variations still require real WebChat end-to-end testing.
