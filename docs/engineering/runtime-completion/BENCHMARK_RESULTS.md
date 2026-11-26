# Benchmark Results

All metrics below were captured directly on this Linux x86_64 host during validation.

## 1. AI Worker Transport Echo Benchmark (`kitt-ai-workers`)

Command: `/tmp/.aiw-venv/bin/python -m kitt_workers.benchmark --jobs 256 --payload-bytes 4096`

| Metric | Measured Value |
|---|---|
| Jobs / Payload | 256 jobs × 4,096 bytes |
| Throughput | **4,743.86 jobs/s** (7,112.29 jobs/s warm CPU) |
| Latency p50 / p95 | **0.202 ms / 0.226 ms** |
| Peak Process RSS | 28,598,272 bytes (~27.3 MiB) |
| Python Peak Allocation | 51,949 bytes |

## 2. Reverse Proxy Core Benchmark (`kitt-reverse-proxy`)

Command: `npm run benchmark:core` (executed after final edit on PR #128)
- Suite completed cleanly alongside 351/351 passing TypeScript/unit tests.

## 3. Remote Runtime Local Compute, Compression & Snapshot Chunking (`kitt-assistant`)

Command: `/tmp/.assistant-venv/bin/python -m kitt.remote.benchmark --local-suite --samples 12 --warmup 2`

| Subsystem | Throughput / Result | p50 Latency | p95 Latency | p99 Latency |
|---|---|---|---|---|
| **CPU SHA-256 (4 MiB × 12)** | **1,413.36 MiB/s** | 2.830 ms | 2.966 ms | 2.966 ms |
| **RAM Copy (4 MiB × 12)** | **699.42 MiB/s** | 5.719 ms | 5.928 ms | 5.928 ms |
| **Zstd Level 3 Compress (512 KiB)** | **961.91 MiB/s** | 0.520 ms | 0.608 ms | 0.608 ms |
| **Zstd Level 3 Decompress** | **1,073.04 MiB/s** | 0.466 ms | 0.544 ms | 0.544 ms |

### Fixed 256 KiB vs FastCDC Chunking (4 KiB Prefix Shift on 2 MiB + 512 KiB Fixture)

| Strategy | Initial Export Time | Shifted Re-Export: Reused Chunks | Shifted Re-Export: Uploaded Chunks |
|---|---|---|---|
| **Fixed 256 KiB** | 17.36 ms | 2 | **8** |
| **Gear FastCDC** | 5,681.62 ms (pure Python loop) | 2 | **2** (**4× fewer uploads**) |

> Note: Pure-Python Gear CDC minimizes network uploads after byte insertions (`4×` reduction in shifted uploads) at higher CPU cost than fixed chunking; large-file operators can choose `chunking="fixed"` (default) when CPU-bound or `chunking="cdc"` when WAN-bandwidth-bound.
