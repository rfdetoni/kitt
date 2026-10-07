# Ecosystem 0.13.25 — durable loop completion ownership

## Failure reproduced

The automatic durable contract was being created and its first item was executing. The stall occurred after workspace mutations: the inner GOAL-owned turn had no TaskPlan, but the generic TaskPlan host-completion gate still required per-turn mutation verification. That recovery path asked the model for registered verification, which led to `plan.verify` even though no TaskPlan existed. Repeated fallback validation then consumed the turn tool budget before the outer contract verifier could own completion.

## Agent CLI 0.84.6

- GOAL-owned turns with no nested TaskPlan defer completion to the existing `GoalStepVerifier`.
- Real TaskPlans retain the generic host-completion gate.
- Contract-item prompts explicitly prohibit creating/verifying a second TaskPlan for the current Goals item.
- Tool-call budgets are unchanged; duplicate verification is removed instead of raising limits.
- 0.84.4 hardening remains included: task+FINAL minimum contracts, risk-gated pre-mutation plan review, item-scoped resolvable blockers, semantic LSP runtime wiring and provider cache observation telemetry.

## Assistant 0.1.28 / runtime 0.2.41

Assistant locks daemon-owned execution to Agent CLI 0.84.6. The previous immutable daemon startup-identity fix remains: an old resident daemon cannot appear compatible merely because package metadata was replaced on disk.

## AI Workers 0.1.52

Evals and Evolution immutable Agent locks move to 0.84.6. Worker behavior is unchanged.

## Unchanged contracts

Reverse Proxy 4.9.16, Protocol 0.9.1, Memory 0.9.2 and Toolbox 0.4.2 remain unchanged. The correction changes local execution ownership only and requires no transport, schema or memory migration.
