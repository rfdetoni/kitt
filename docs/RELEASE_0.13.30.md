# KITT Ecosystem 0.13.30 — Nested JSON contract recovery

New supplied logs confirm that Agent 0.84.10 submits both planning and high-risk plan review to Gemini without local token rejection. Review fails because Gemini emits KITT_PLAN_REVIEW JSON inside an outer content string without escaping its quotes; both upstream repairs repeat the serialization defect.

Reverse Proxy 4.9.19 recovers that response locally using the existing mandatory contract field shape. Alternatives that swallow required fields are excluded, and exactly one matching interpretation is required. The original verdict content is preserved. Multiple matching parses, ambiguous optional tool arguments, duplicate properties and incomplete payloads remain rejected. Generic JSON recovery keeps its conservative behavior and existing byte, depth, work and branch limits.

Action and loop status require string values; array coercion is rejected. Model instructions explicitly require escaping nested string quotes and backslashes. Agent 0.84.10, Assistant 0.1.32/runtime 0.2.45, Workers/Evals/Evolution 0.1.56, Protocol 0.9.2, Memory 0.9.3 and Toolbox 0.4.3 remain compatible and unchanged. No wire contract or consumer lock changes are needed. WebChat continues to own token limits.

## Validation

208 Proxy tests, TypeScript checks and production build passed. The HTTP regression returns the exact nested verdict in one attempt, while a competing interpretation of tool arguments still yields a recoverable failure with no tool dispatch. Existing canonical-contract checks now also reject array-valued action and status. All three failed responses from the supplied log were replayed and recovered locally. A fresh authenticated Gemini session was not run locally.

The release manifest pins the new Proxy revision alongside the existing compatible ecosystem revisions. Root installer and architecture checks plus clean-install CI validate the composition.
