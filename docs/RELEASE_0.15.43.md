# KITT 0.15.43 — release lock and memory integrity

## Immutable component pins

- Memory 0.10.2: `e236c18323f2e8cdb839d02710eaf7514a060c8e`.
- Agent CLI 0.87.20: `bae99751b082523bc3d44bc26f249f085a25fc3a`.
- Assistant native 0.1.44 / Python runtime 0.3.28: `129b7ff460026ced774f4afc0486fe99220c9316`.
- AI Workers 0.1.67: `249690e3d935d435d83a861f30e10df65afe7cda`.
- Protocol, Toolbox and Reverse Proxy: unchanged previous release pins.

## Behavior

- Fix previous release installer failure: Assistant native Cargo.lock now resolves the pinned Rust Memory packages.
- For vector upserts, require the original persisted content hash; concurrent updates cannot attach embeddings for stale content.
- Bounded workspace-only, secret-excluding backfill derived from missing persisted embeddings, retried upon subsequent semantic searches; no background vector server.
- All consumer uv.lock metadata and CI checkouts resolve the same immutable Agent CLI commit.

## Validation

Requires root `ecosystem-integration` installation smoke and successful Memory/Assistant/Agent/Workers CI. Retrieval quality benchmarks and additional indexing/proxy performance work are independent tasks and are not claimed by this release.
