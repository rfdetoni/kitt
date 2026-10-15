"""Deterministic, stdlib-only microbenchmark for SQLite FTS5 and 8-bit LSH.

Synthetic workload ONLY. Not a substitute for KITT Agent, Rust Memory,
Ollama or WebChat end-to-end benchmarks. p50/p95 include Python overhead.
"""
import argparse
import math
import random
import sqlite3
import statistics
import time

MASK = (1 << 64) - 1


def lsh_bucket(values):
    bits = 0
    for bit in range(8):
        score = 0.0
        for dim, value in enumerate(values):
            x = (((dim + 1) * 0x9E3779B97F4A7C15) & MASK) ^ (((bit + 1) * 0xBF58476D1CE4E5B9) & MASK)
            x ^= x >> 30
            x = (x * 0xBF58476D1CE4E5B9) & MASK
            x ^= x >> 27
            x = (x * 0x94D049BB133111EB) & MASK
            x ^= x >> 31
            score += value if x & 1 == 0 else -value
        if score >= 0:
            bits |= 1 << bit
    return bits


def norm(values):
    length = math.sqrt(sum(x * x for x in values))
    return tuple(x / length for x in values)


def percentile(values, fraction):
    ordered = sorted(values)
    return round(ordered[min(len(ordered) - 1, math.ceil(len(ordered) * fraction) - 1)] * 1000, 3)


def sql_bench(rows, count, randomizer):
    db = sqlite3.connect(":memory:")
    try:
        db.execute("CREATE TABLE chunks(rowid INTEGER PRIMARY KEY, text TEXT NOT NULL)")
        db.execute("CREATE VIRTUAL TABLE fts USING fts5(text)")
        tokens = [f"needle{i:04d}" for i in range(300)]
        data = [(" ".join(randomizer.sample(tokens, 5)),) for _ in range(rows)]
        db.executemany("INSERT INTO chunks(text) VALUES (?)", data)
        db.executemany("INSERT INTO fts(rowid,text) VALUES (?,?)", ((i + 1, row[0]) for i, row in enumerate(data)))
        times_fts, times_like = [], []
        for token in randomizer.choices(tokens, k=count):
            started = time.perf_counter()
            fts_hits = {r[0] for r in db.execute("SELECT rowid FROM fts WHERE fts MATCH ?", (token,))}
            times_fts.append(time.perf_counter() - started)
            started = time.perf_counter()
            like_hits = {r[0] for r in db.execute("SELECT rowid FROM chunks WHERE text LIKE ?", ("%" + token + "%",))}
            times_like.append(time.perf_counter() - started)
            assert fts_hits == like_hits, "FTS5/LIKE result mismatch"
        return {"fts_p50_ms": percentile(times_fts, .5), "fts_p95_ms": percentile(times_fts, .95),
                "like_p50_ms": percentile(times_like, .5), "like_p95_ms": percentile(times_like, .95)}
    finally:
        db.close()


def vector_bench(rows, dimensions, count, randomizer):
    vectors = [norm([randomizer.gauss(0, 1) for _ in range(dimensions)]) for _ in range(rows)]
    by_bucket = {}
    for i, vec in enumerate(vectors):
        by_bucket.setdefault(lsh_bucket(vec), []).append(i)
    recalls, exact_ms, lsh_ms, candidates_seen = [], [], [], []
    for _ in range(count):
        seed = vectors[randomizer.randrange(rows)]
        query = norm([x + randomizer.gauss(0, .12) for x in seed])
        def score(i):
            return sum(a * b for a, b in zip(query, vectors[i]))
        started = time.perf_counter()
        exact = sorted(range(rows), key=score, reverse=True)[:10]
        exact_ms.append(time.perf_counter() - started)
        started = time.perf_counter()
        center = lsh_bucket(query)
        chosen = [i for bucket in [center, *[center ^ (1 << b) for b in range(8)]]
                  for i in by_bucket.get(bucket, [])][:4096]
        approx = sorted(chosen, key=score, reverse=True)[:10]
        lsh_ms.append(time.perf_counter() - started)
        recalls.append(len(set(exact) & set(approx)) / 10)
        candidates_seen.append(len(chosen))
    return {"recall_at_10": round(statistics.mean(recalls), 3),
            "candidate_mean": round(statistics.mean(candidates_seen), 1),
            "exact_p50_ms": percentile(exact_ms, .5), "exact_p95_ms": percentile(exact_ms, .95),
            "lsh_p50_ms": percentile(lsh_ms, .5), "lsh_p95_ms": percentile(lsh_ms, .95)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=5000)
    parser.add_argument("--dimensions", type=int, default=32)
    parser.add_argument("--queries", type=int, default=20)
    parser.add_argument("--seed", type=int, default=4821)
    args = parser.parse_args()
    if args.rows < 100 or not 2 <= args.dimensions <= 2048 or args.queries < 1:
        parser.error("rows >= 100, dimensions 2..2048, queries >= 1 required")
    randomizer = random.Random(args.seed)
    started_cpu = time.process_time()
    sql = sql_bench(args.rows, args.queries, randomizer)
    vector = vector_bench(args.rows, args.dimensions, args.queries, randomizer)
    print({"sqlite_version": sqlite3.sqlite_version,
           "rows": args.rows, "dimensions": args.dimensions, "queries": args.queries,
           "fts5_vs_like": sql, "lsh_vs_exact": vector,
           "cpu_seconds": round(time.process_time() - started_cpu, 3)})
    print("Synthetic Python microbenchmark; results are not KITT end-to-end latency.")


if __name__ == "__main__":
    main()
