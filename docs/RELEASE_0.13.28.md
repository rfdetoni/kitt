# KITT Ecosystem 0.13.28

This release fixes the eleven findings from the Agent CLI, Reverse Proxy and dependency review. It preserves transport Envelope v1 and existing memory schemas.

| Component | Version | Change |
| --- | --- | --- |
| Agent CLI | 0.84.9 | Planning cancellation, durable selected inputs, Node check/build verification, scoped native reads and shared argument cap |
| Reverse Proxy | 4.9.17 | Session admission reservations, browser cancellation and producer argument cap |
| Assistant | 0.1.31 / runtime 0.2.44 | Immediate turn/thinking events, cancellation event ordering and aligned locks |
| Toolbox | 0.4.3 | Contained reads, current symbol offsets, bounded indexing and explicit invalidation |
| Memory | 0.9.3 | Return pooled SQLite connections in receipt lookup and concept expansion |
| Protocol | 0.9.2 | Export MAX_TOOL_ARGUMENT_BYTES in Rust, Python and TypeScript; verify SDK parity |
| AI Workers, Evals, Evolution | 0.1.55 | Local-only Whisper fallback and aligned Agent/Protocol locks |

## Operational behavior

Cancellation stops contract admission and closes the dedicated automation tab to interrupt browser waits. A browser side effect already submitted before cancellation cannot be undone. Provider session tabs remain separate from automation tabs.

Selected files and attachment references are persisted with the Goal, so scheduler execution and validation use the same inputs after resume. Counts and workspace-relative paths are checked before admission; existing payload limits still apply when loading content.

The native index refreshes at most once per second between external edits. KITT edits invalidate it immediately. Individual source reads are capped at 4 MiB; scans use file, entry, byte, symbol and elapsed-time budgets. A partial scan reports truncation instead of silently representing a complete index. Direct symbol reads reparse current content to avoid stale offsets.

Tool arguments are capped at 65,536 UTF-8 bytes of their serialized JSON, including escaping. Producers and consumers reject larger calls before tool execution. Large edits must be split into smaller calls.

When STT local_files_only is enabled, openai-whisper requires an existing explicit checkpoint or cache checkpoint. Missing models fail before the download-capable loader runs. CPU retries retain local-only settings.

## Validation

Local checks passed: Agent 264 tests (one skipped), Proxy 205 tests plus TypeScript build, Workers/Evals/Evolution 33 tests, focused daemon lifecycle/cancellation tests, Protocol cross-SDK parity and fixtures, and the native Rust workspace suites. Rust formatting and Clippy passed; the Toolbox wheel was built and exercised in Python 3.14. The installer unit suite and architecture/catalog checks passed.

Socket-based daemon tests require CI because this local environment rejects socket creation. GitHub Actions validates the published component candidates, including platform lifecycle checks. Live provider accounts and real STT model inference were not exercised. The immutable release component revisions are in ecosystem.release.json; main installation continues to resolve main once per installation.
