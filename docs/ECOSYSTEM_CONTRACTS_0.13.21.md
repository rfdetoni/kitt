# K.I.T.T. Ecosystem 0.13.21 — durable task-contract execution

## Snapshot

| Component | Version / role | Revision |
| --- | --- | --- |
| Agent CLI | 0.84.0 | `b2f627b09643289f31dcb181904722da69395689` |
| Assistant | 0.1.23 | `23855eb2da5b6a068b04e2f33fd24ba9817aadb1` |
| Assistant runtime | 0.2.36 | included in Assistant revision |
| AI Workers / Evals / Evolution | 0.1.46 | `83f23f873c8ab977fafc9f5cad3f514f3f92cb05` |
| Protocol | 0.9.1 | unchanged |
| Memory | 0.9.2 | unchanged |
| Toolbox | 0.4.2 | unchanged |
| Reverse Proxy | 4.9.15 | unchanged |

## Architecture

Agent CLI 0.84.0 adds an optional durable task contract without creating a second runner, scheduler, memory engine or permission authority.

The existing GoalScheduler remains the lifecycle owner. A bounded model-produced plan is schema-validated by the host, persisted as ordered contract items, and executed one item at a time through GoalStepExecutor and the canonical TurnProcessor/tool path.

The scheduler only commits an item as DONE while it still owns the goal lease and the executor returns qualified `ITEM_DONE` evidence containing:

- successful completion verification;
- independent validation verdict `OK`;
- non-empty validation evidence.

A plain model/executor `SUCCEEDED` status cannot advance a contract item.

## Verification and isolation

Contract check ids must resolve to the host-owned verification registry; unknown ids are rejected during planning. Paths remain workspace-relative and the final integrated path set is bounded rather than silently truncated.

Planner and independent validator turns use `no_history=True`. Agent 0.84.0 makes this an actual isolation boundary for conversation history, working-set state, memory/harness context and provider/Reverse Proxy session identity. Validation remains read-only and cannot increase capabilities.

The final independent validation receives the authoritative original user request so planner omissions cannot be accepted merely because model-generated criteria omitted them.

## Compatibility

No shared KITT Protocol schema, Memory API or Reverse Proxy wire contract changed. Therefore those components intentionally retain their existing releases.

Assistant had a real compatibility requirement: runtime 0.2.35 declared Agent `<0.84`. Runtime 0.2.36 expands the supported range to `<0.85` and locks Agent 0.84.0.

AI Workers Evolution/Evals also locked the previous Agent revision; 0.1.46 aligns both locks.

## Validation evidence

Before ecosystem promotion:

- Agent CLI PR checks passed release-critical regressions, clean-room, static ownership checks, Windows package smoke, Docker runtime smoke and Podman runtime smoke.
- Assistant PR/push CI passed Rust core checks, Python runtime suite, HUD build, and lifecycle validation on Linux, macOS and Windows.
- AI Workers CI passed on the aligned 0.1.46 revision.

The root ecosystem CI remains the final immutable-composition gate for the SHAs above.
