# KITT ecosystem compatibility contract

The laboratory baseline uses **KITT Protocol v1** as the only cross-process wire contract.

## Rules

- No legacy flat `command` JSON messages.
- Every authenticated daemon request is `{ "token": "...", "envelope": { ... } }`.
- Every response/event is a versioned envelope.
- Request envelopes have no `correlation_id`.
- Responses use `correlation_id = request.id`.
- Unknown envelope fields, versions and kinds fail closed.
- NDJSON is the framing format: one frame per line.
- The canonical maximum daemon frame is 1 MiB.
- AI workers use the same envelope semantics with a tighter 256 KiB line limit.
- Authentication tokens are transport metadata, never payload fields.
- `kitt-memory` has no IPC/network dependency.
- `kitt-toolbox` remains protocol-agnostic unless a concrete process boundary requires otherwise.
- Cross-repository dependencies must not rely on sibling directory layout.

## Laboratory dependency policy

During active laboratory development, cross-repository dependencies may track `main` while lockfiles pin resolved commits. Before a public release, replace those branch dependencies with signed tags or published packages/crates.

## Release ordering

1. `kitt-protocol`
2. `kitt-memory`
3. `kitt-ai-workers`
4. `kitt-assistant`
5. `kitt-agent-cli`
6. `kitt-toolbox` validation
7. `kitt` ecosystem integration gate
