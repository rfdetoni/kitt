# KITT ecosystem 0.15.42 — local hybrid semantic memory

## Released components
- Memory 0.10.0 at eee55669ef7400b2c1f31b6e658a28f018b77723: Rust/SQLite derived embeddings, schema 10, indexed model/dimension/LSH buckets, content-hash invalidation and scope/sensitivity/temporal filtering; query reranking combines FTS5 and cosine candidates using RRF.
- Agent CLI 0.87.19 at fed07a745c58ad8c286cba1230ebce9afe413170: optional loopback-only Ollama embeddings with lazy bounded single-thread indexing and lexical fallback.
- Assistant Runtime 0.3.27 at f5618fca85ac58d2708e97b0219f975ffb08e53b: compatible Agent SHA and Python lock/CI alignment.
- AI Workers 0.1.66 at 70f48abc58ae8b42133f7bd7d2635629cf7db93a: eval/evolution compatible Agent SHA and Python locks.

## Enable
```sh
ollama pull nomic-embed-text
export KITT_MEMORY_EMBED_MODEL=nomic-embed-text
# optionally: export KITT_MEMORY_EMBED_URL=http://127.0.0.1:11434
kitt
```

No model is automatically downloaded by KITT. Existing memories are not automatically bulk reindexed: newly remembered entries will be scheduled when the Agent process is active; a future bounded backfill job can cover legacy records. Query embeddings have a short deadline and degrade to lexical fallback if unavailable. Only loopback Ollama endpoints are permitted.

## Design tradeoffs
The vector index is an embedded LSH candidate index, not LanceDB/HNSW, and must be evaluated against exact recall and larger datasets before being treated as a general-purpose ANN replacement. SQLite remains the sole durable authority for memory, receipts, jobs, permissions and text search. Vectors can be discarded/recreated per model.

## Validate
- Memory: `cargo fmt --check`, `cargo clippy --workspace --all-targets --locked -- -D warnings`, `cargo test --workspace --locked`.
- Agent: PR Checks smoke and critical contracts.
- Consumers: CI build, lock and package tests.
- Root: `python -m unittest discover -s tests` and SHA validation against main refs.
