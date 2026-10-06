# K.I.T.T. Ecosystem 0.13.17

## Scope

This release composes Agent CLI **0.83.17** at `8d3d047b77c1a361a507ab8063c70539b234bfb1`. Assistant advances to pin-only commit `d9540e0dfdf86fc26266bea78e59b97f1eb8eb4c` and AI Workers to pin-only commit `6d9deabe1bcecb6ffb471cba4a31cde0dcd2d68b`, aligning their Python locks to the exact Agent revision. Protocol, Reverse Proxy, Memory and Toolbox pins remain those from ecosystem 0.13.16; no companion runtime contract changed.

## Changes

- Optional built-in `kitt-rea` integration registers only an already-installed local `rea mcp` executable through the Agent's existing governed MCP boundary.
- KITT does not download REA, Ghidra, Hopper or other reverse-engineering dependencies implicitly.
- Evidence v2 enriches the existing Agent evidence record with kind, authority, confidence, coverage, limitations, producer metadata and a deterministic provenance digest.
- Agent state schema 11 adds one additive `metadata_json` column to `evidence_records`; migrations from schema 10 preserve existing evidence identity.
- The existing task-plan coordinator projects verification obligations and residual unknowns from host-owned execution facts into the trusted output contract. It does not introduce another scheduler, event ledger or completion authority.

## Compatibility

The feature is Agent-owned. REA is an optional MCP capability, not an ecosystem dependency. Shared request/response schemas and the Agent ↔ Reverse Proxy transport remain unchanged, so Protocol **0.9.1** and Reverse Proxy **4.9.12** remain pinned.

Release installation continues to resolve immutable component SHAs from `ecosystem.release.json`.

## Validation

Agent CLI PR #69 passed:

- release-critical regression contracts;
- clean-room provenance guard;
- static critical checks;
- Agent ownership-boundary validation;
- real Docker runtime smoke;
- real Podman runtime smoke;
- Windows package/compile/help smoke;
- Docker image workflow.

Assistant PR #23 then passed Rust/core, Python runtime, HUD web and Windows/macOS/Linux lifecycle jobs while installing the aligned Agent dependency. AI Workers PR #18 passed worker protocol/STT boundaries, Evolution security/promotion, evaluation smoke, static checks and the installed dependency graph.

Focused Agent regressions cover schema 10 → 11 migration, Evidence v2 round-trip, protection against weaker evidence downgrading stronger evidence, verification-obligation closure, and plugin-owned stdio MCP registration.

## Limits

Authenticated or vendor-specific REA providers were not exercised by the KITT CI. Enabling `kitt-rea` requires a separately installed compatible `rea` executable; REA remains responsible for its own provider/tool semantics. Evidence authority identifies provenance and does not by itself prove behavior outside the observed coverage.
