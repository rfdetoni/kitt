# Ecosystem 0.13.26 — visible first-prompt bootstrap

## Symptom

After submitting the first prompt, the full-screen CLI could remain on the initial home screen with no visible progress even though the Agent was already connecting/starting the Assistant daemon, attaching the conversation and entering automatic-contract startup.

## Root cause

The visible route change from `home` to `session` lived only in the `TurnStarted` reducer. `TurnStarted` is emitted after `TurnEventBridge.start(...)` establishes the execution authority, so daemon/bootstrap latency was invisible.

## Agent CLI 0.84.7

- moves the UI to `session` before awaiting bridge startup;
- exposes the submitted prompt, `STARTING` status and core task immediately;
- marks that prompt as optimistic UI state only;
- reconciles the real `TurnStarted` event without duplicating the user message;
- keeps startup failures visible in the session as `ERROR` with a failed core task and persistent toast;
- leaves history persistence, daemon authority, durable Goals contracts and execution budgets unchanged.

The regression deliberately blocks `bridge.start(...)` and proves the session is already visible before the bridge returns.

## Consumer alignment

Assistant 0.1.29/runtime 0.2.42 locks Agent CLI 0.84.7 for daemon-owned execution. AI Workers 0.1.53 aligns Evals/Evolution immutable locks.

## Unchanged components

Reverse Proxy 4.9.16, Protocol 0.9.1, Memory 0.9.2 and Toolbox 0.4.2 are unchanged.
