# KITT 0.15.46 — retrieval benchmark and evidence

Run `python benchmarks/retrieval_sqlite_lsh.py --rows 5000 --dimensions 32 --queries 20 --seed 4821`.
The default harness uses SQLite FTS5 with equivalent one-token LIKE queries, and the Memory 0.10.2 8-bit fixed-hyperplane LSH candidate rule (center plus eight single-bit neighbors, max 4096 candidates). It compares approximate cosine top-10 against exact top-10.

Observed on the ChatGPT execution container (SQLite 3.46.1, synthetic random corpus, two repetitions): FTS5 p50 0.029–0.032ms vs LIKE p50 0.709–0.790ms. Exact cosine p50 8.18–10.12ms vs LSH p50 0.57–0.73ms; LSH Recall@10 **0.235**. These are Python microbenchmarks, **not Rust/Memory/Agent end-to-end figures**. This synthetic low recall warrants testing real Ollama embeddings and representative corpora before promoting LSH as an all-purpose replacement or selecting an ANN dependency.

No component pin or runtime logic changed relative to KITT 0.15.45. Root 0.15.46 adds CI smoke coverage of the harness; no new dependency.
