# Ecosystem 0.13.14

This immutable release composes the fixes from the Agent CLI and companion-module review. `ecosystem.release.json` is the authority for full component SHAs. `edge` continues to follow component `main`; wire version stays 1 and SQLite stays at schema v9.

| Component | Version | Result |
| --- | --- | --- |
| Agent CLI | 0.83.16 | Contained fallback reads, bounded regex execution, complete path reservations, guarded directory recovery and cursor-based daemon reconnection |
| Protocol | 0.9.1 | Public Python, Rust and TypeScript decoders reject duplicate keys, malformed UTF-8, non-finite numbers and lone surrogates |
| Memory | 0.9.2 | One bounded, validated and transactional receipt batch per selection |
| Toolbox | 0.4.2 | Filter before cloning, bounded top-k selection, deterministic source-offset ties and external-edit refresh |
| Assistant | 0.1.19 / runtime 0.2.33 | Authoritative connection health, explicit EOF failure and immediate resync stop before cursor advancement |
| AI Workers | 0.1.43 | Actual graph ablation and optional lexical reranking before selection, with latency/token diagnostics |
| Reverse Proxy | 4.9.10 | Trusted correlated raw response can rescue a DOM timeout; dependency audit fix |

## Reviewed boundaries

| Boundary | Correction and acceptance evidence |
| --- | --- |
| Python native fallback | Uses RepositoryScanner and no-follow WorkspaceFileSystem reads; regressions cover ignored and external symlink paths |
| Regex search | Disposable subprocess with a 3-second execution deadline, kill/reap and worker-side path validation; pathological regex regression |
| Move/rename coordination | Reserves source and destination for aliases and runtime tools; real destination contention regression; releases leases on resource acquisition failure |
| Mutation recovery | Captures file and directory changes before dispatch; verifies descendants and rejects rollback after changed contents; engineering-wrapper directory rollback/conflict regressions |
| Durable run state | Reads latest state with descending SQL LIMIT 1; recovery regression exceeds 10,000 events |
| Public wire decoding | Shared invalid corpus runs through all three public SDKs; version lexemes and required payload also validated |
| Provider bytes | SSE rejects invalid UTF-8; raw-CDP timeout recovery requires a previously trusted explicit extraction mode, full-prompt match, successful completion and strict contract validation |
| Memory latency and receipts | Context budget 8 seconds, receipt telemetry 1 second; outage fails the turn recoverably; batch validates all items before one SQLite transaction |
| Daemon reconnection | Resumes from delivered cursor, deduplicates replay and bounds attachment buffering; EOF/resync stops delivery without resubmitting mutations |
| Symbol search | Selects bounded candidates before cloning; same-line repeated JavaScript declarations reproduce and prevent a source-order cutoff regression |
| Retrieval evaluation | Graph disabled/enabled and lexical reranking change the actual stages before selection; indexed dependency-neighbor fixture and distinct-output tests |
| Composition | Version metadata, Cargo/npm/uv locks and Assistant CI checkout refs align with the immutable component revisions |

## Validation and limits

Python validation uses 3.14. The Agent full suite passed with 222 tests, one skip and 12 subtests before the final lease regression; the release-critical gate including that regression passed with 210 tests and 12 subtests. Proxy verification passed 178 tests, type checks and build, with zero reported npm audit vulnerabilities. Public Protocol validation passed Python, TypeScript, Rust and schema parity checks. Memory and Toolbox passed locked Rust tests, formatting and Clippy with warnings denied; Toolbox includes 17 tests after the reproduced tie regression. Workers and Assistant non-socket Python tests passed together (56 tests). Assistant CI exercises the real daemon lifecycle on supported operating systems; local Unix socket creation was denied by the execution environment.

Root installer/catalog tests passed locally (58 tests and seven subtests), together with architecture checks, immutable-manifest validation, installer Bash syntax and Protocol/Proxy schema parity. The root integration workflow checks clean installation from `main`, immutable release installation, matching Protocol/Proxy schemas, consumer locks and portable startup. Component CI and immutable revisions are available through the repositories linked in the release manifest.

Directory snapshots refuse links and special files and are bounded to 1,000 entries / 32 MiB. Rollback checks for conflicting content; it does not provide a filesystem transaction against unrelated external writers. The regex execution deadline excludes bounded repository discovery. Daemon attachment buffers at most 2,048 live events. EOF can leave a request outcome unknown, so reconnect never silently resubmits mutations.

Raw network recovery does not bypass cancellation, manual intervention, untrusted profiles, tap failures or ambiguous competing payloads. Authenticated live WebChat providers were not exercised. The six-case retrieval fixture measures synthetic recall and stage behavior: structural retrieval scores 5/6, graph retrieval 6/6, and lexical reranking 5/6 at recall@5. These results do not establish production model quality; reranking is not promoted by default.

Proxy 4.9.10 updates transitive `proxy-addr` to 2.0.8 while preserving both audit gates. See [the upstream advisory](https://github.com/advisories/GHSA-jqcg-44mw-7w3h) for affected configurations.
