# Ecosystem 0.13.27 — live durable-contract progress

## Evidence

The observed request reached Gemini Web, produced a valid automatic execution contract, and completed the planning turn successfully. The first durable contract item then began inside the Goal scheduler, but its inner TurnProcessor events were consumed by the scheduler instead of being forwarded to the outer user-facing turn. The TUI therefore appeared idle between contract-level checkpoints even while inner work was active.

## Agent CLI 0.84.8

- forwards a bounded set of safe inner Goal progress events through the existing outer automatic-contract stream;
- keeps nested terminal events, approvals and metrics private to the owning scheduler path;
- emits visible thinking state while the initial contract is being planned;
- flushes final queued progress before terminal contract completion;
- bounds interactive kitt-memory recall to four seconds;
- treats temporary kitt-memoryd unavailability as empty contextual enrichment rather than a failed coding turn;
- records separate `memory_context` and `prompt_build` latency phases before `tool_loop.start`.

The Goal scheduler remains the only durable execution authority. No second orchestrator or state machine was added.

## Consumer alignment

- Assistant 0.1.30 / runtime 0.2.43 locks Agent CLI 0.84.8 for daemon-owned execution.
- AI Workers 0.1.54 aligns Evals/Evolution immutable Agent locks.

## Unchanged components

Reverse Proxy 4.9.16, Protocol 0.9.1, Memory 0.9.2 and Toolbox 0.4.2 are unchanged.
