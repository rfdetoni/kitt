# K.I.T.T. Ecosystem 0.13.23 — automatic durable loops and managed proxy ownership

## Snapshot

| Component | Version / role | Revision |
| --- | --- | --- |
| Agent CLI | 0.84.2 | c9bbe79bf2393179a58b616a90552906b422311a |
| Assistant | 0.1.25 | 19e6088052ace2813d02e2e394fec2aac851f229 |
| Assistant runtime | 0.2.38 | included in Assistant revision |
| AI Workers / Evals / Evolution | 0.1.48 | 8208a44c1703e3212c5458668aa6baed10939be6 |
| Reverse Proxy | 4.9.16 | cc03515b90afcc995699969e86cc22539d8b7dc7 |
| Protocol | 0.9.1 | unchanged |
| Memory | 0.9.2 | unchanged |
| Toolbox | 0.4.2 | unchanged |

## Automatic contract execution

Persisted user turns in mode=auto now enter the Agent CLI durable contract automatically instead of requiring --contract or /contract.

The outer user turn plans and persists the ordered contract. GoalScheduler remains the only scheduler and executes the current item through GoalStepExecutor. A failed validation reiterates the same item; the goal only reaches SUCCEEDED after every item, including final validation against the authoritative original request, is DONE.

Planner turns and Goal-owned execution turns call TurnProcessor directly, so the contract does not recursively decompose its own items. Explicit ask, plan and no-history turns also remain direct.

## Authoritative daemon path

Assistant runtime 0.2.38 routes daemon-owned mode=auto turns through the same wrapper. This closes the previous gap where the local Agent supported contracts but the normal TUI path delegated to the resident daemon, which sent the original prompt directly to TurnProcessor.

Goal-owned approvals are detected by their pending-action security context. Approval executes exactly the approved inner action and resumes the same contract item without resetting attempts. TUI IPC approval does not acquire the outer turn lock and therefore cannot deadlock against the contract observer.

Cancellation tracks the active inner Goal turn, cancels that TurnProcessor execution, clears pending approval where applicable and transactionally moves the contract to CANCELLED.

## Managed Reverse Proxy logging

When Agent CLI starts a Reverse Proxy through its managed control client, it forwards the Agent log level and log-content policy plus the configured Agent log path as a directory anchor.

The control plane derives a separate reverse-proxy-<instance>.log file in that directory. Agent and Proxy therefore do not append concurrently to one file.

Managed restart preserves these logging settings.

## Managed Reverse Proxy ownership

Agent-started services include the Agent PID. Reverse Proxy resolves and persists the process fingerprint and supplies PID plus fingerprint to the spawned proxy process.

The managed proxy periodically checks that the exact owner process still exists. Normal TUI shutdown explicitly stops only instances created by that Agent client; abnormal Agent termination is covered by the PID/fingerprint watchdog in the Proxy process.

Standalone/manual Reverse Proxy services receive no owner identity and remain independent.

The shared Browser Host remains profile-owned rather than bound to a single Agent, avoiding accidental teardown when multiple managed services share it.

## Compatibility decisions

No KITT Protocol or Memory wire schema changed. Those components intentionally remain at their current revisions.

AI Workers changed only because Evals/Evolution keep immutable Agent source locks. Assistant changed because it owns the authoritative resident daemon execution path and also keeps an immutable Agent lock.

## Validation before ecosystem composition

Agent CLI 0.84.2 passed PR Checks and Docker after tests covering automatic contract creation, approval resume, cancellation-related lifecycle behavior, inherited Proxy logging and Agent-owned Proxy cleanup.

Reverse Proxy 4.9.16 passed CI and Docker with managed launch arguments covering logging and owner identity.

Assistant 0.1.25/runtime 0.2.38 passed Python runtime tests, Rust core, HUD, and lifecycle validation on Linux, macOS and Windows against the exact Agent CLI 0.84.2 revision. The daemon tests include automatic contract routing and prevention of Goal-approval lock deadlock.

AI Workers 0.1.48 passed its critical CI after Agent-lock alignment.

The root ecosystem integration remains the final immutable composition gate for this snapshot.
