# K.I.T.T. Ecosystem 0.13.22 — focused contract-step verification

## Snapshot

| Component | Version / role | Revision |
| --- | --- | --- |
| Agent CLI | 0.84.1 | `37945bf0b868cb0dab00984c7e7ebc31d317966a` |
| Assistant | 0.1.24 | `9b836eeeb7d10f292e3e70da6b866b0361702024` |
| Assistant runtime | 0.2.37 | included in Assistant revision |
| AI Workers / Evals / Evolution | 0.1.47 | `09a00bddc7f0b024ab68683091be7a5ff0a0fbfc` |
| Protocol | 0.9.1 | unchanged |
| Memory | 0.9.2 | unchanged |
| Toolbox | 0.4.2 | unchanged |
| Reverse Proxy | 4.9.15 | unchanged |

## Structural correction

Agent CLI 0.84.1 keeps the durable Plan → Execute → Validate → Retry lifecycle introduced in 0.84.0, but removes the oversized `GoalStepExecutor` responsibility discovered during the final Pragmatic Dev review.

`GoalStepExecutor` now owns turn execution and event collection. Mutation-path discovery and bounded workspace snapshots live in `review_snapshot.py`; reviewer egress, budget and provider accounting live in `review_runtime.py`; deterministic verification, adversarial review, independent contract validation and completion-state persistence are composed by `step_verifier.py`.

The executor's main call path was reduced from roughly 346 lines to roughly 105 lines without introducing another scheduler, runner, memory owner or policy authority.

## Contract invariants retained

- GoalScheduler remains the lifecycle and lease/fencing authority.
- Contract items advance only with qualified `ITEM_DONE` evidence.
- Host-owned verification and independent validation remain fail-closed.
- The final validation still checks the authoritative original user request.
- Model-produced plans cannot grant capabilities or inject arbitrary command argv.
- Planner/validator no-history provider isolation remains unchanged.

## Compatibility

No shared Protocol schema, Memory API or Reverse Proxy wire contract changed. Those releases intentionally remain pinned.

Assistant and AI Workers changed only because they keep immutable Agent consumer locks. Their CIs passed with Agent 0.84.1 before this snapshot was composed.

## Validation

Agent CLI 0.84.1 passed PR Checks and Docker, including release-critical regressions, clean-room/static ownership checks, Windows package smoke, Docker runtime smoke and Podman runtime smoke.

Assistant 0.1.24/runtime 0.2.37 passed its Python runtime, Rust core, HUD and Linux/macOS/Windows lifecycle jobs. AI Workers 0.1.47 passed its critical dependency/evaluation gate.

The root ecosystem CI is the final immutable-composition validation for the SHAs above.
