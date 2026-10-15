# KITT 0.15.44 — performance and safe memory

## Pinned component revisions

- Agent CLI 0.87.22: `7a010b2dfba3e3356b7b49aeb32186b69605df7f`.
- Reverse Proxy 5.3.13: `f6d7687d57c014cf4924ae8a44c744386ac30d5f`.
- Assistant native 0.1.44 / Python Runtime 0.3.30: `3cb7cb61e15f041c309653a08cd2f4a0f21a1a77`.
- AI Workers 0.1.69: `e3f1879204be23e6e0e473c1d764ee9ca1cb495e`.
- Memory 0.10.2 remains pinned to `e236c18323f2e8cdb839d02710eaf7514a060c8e`; Protocol 0.13.3 and Toolbox retain prior pins.

## Changes

- Full repository reconciliation: shorter SQLite transactions, parser/file I/O outside database RLock and guarded concurrent file metadata.
- Targeted graph refresh, cache invalidation and indexed FTS routing for ordinary lexical queries; native Rust retains diagnostic and missing-index search.
- Reused, idle-cleaned WebChat DOM mutation observer with unchanged freshness, security and completion rules.
- Revision-safe asynchronous vector upserts and SQL-derived retry/backfill of missing workspace embeddings across Agent restarts.
- Native Assistant Cargo.lock and Python consumer uv.lock references match immutable release pins.
- KAP/2 code parity remains enforced by Proxy CI against authoritative Protocol; no duplicate parser added.

## Checks

Release requires Agent CLI, Proxy, Memory, Assistant and Workers CI plus root `ecosystem-integration` (main and `--channel release` smoke). Performance benchmarks must be run on representative repositories before claiming measured gains.
