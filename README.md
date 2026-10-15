## KITT 0.15.43 — Memory 0.10.2 and revision-safe durable embedding backfill

Pins Agent CLI 0.87.20, Memory 0.10.2, native Assistant 0.1.44 / Runtime 0.3.28 and AI Workers 0.1.67. The Memory vector index now refuses outdated embeddings by exact content hash, and pending workspace embeddings remain discoverable from SQLite across restarts. Assistant Cargo.lock resolves the exact Memory git commit pinned in this release. Existing Protocol, Toolbox and Reverse Proxy commits remain unchanged. [Release notes](docs/RELEASE_0.15.43.md).

## KITT 0.15.42 — opt-in native hybrid memory retrieval

Pins Memory **0.10.0** (SQLite schema 10, indexed multi-probe LSH cosine candidates and FTS5/RRF), Agent CLI **0.87.19** (Ollama local lazy embeddings with bounded indexing/fallback), Assistant Runtime **0.3.27**, and AI Workers **0.1.66**. No new networked vector database or Protocol/KAP/2 change. Enable only with an installed local embedding model via `KITT_MEMORY_EMBED_MODEL`; SQLite remains the authoritative durable store. See [release notes](docs/RELEASE_0.15.42.md).

## KITT 0.15.41 — indexed search efficiency and consumer lock synchronization

Release pins Agent CLI **0.87.18** (SQLite FTS5 rowid deletions, qualified symbol indexes and reduced unchanged-file reads), Reverse Proxy **5.3.12** (de-duplicated DOM contract samples and efficient CDP event buffering), Assistant Runtime **0.3.26**, and AI Workers **0.1.65**. Unchanged Protocol, Memory and Toolbox commits remain pinned to the previous validated revisions. See [release notes](docs/RELEASE_0.15.41.md).

## KITT 0.15.40 — visible Goal planning and execution progress

Pins Agent CLI **0.87.16**, which sends host-owned planning, review,
revision/retry and execution states through daemon IPC into the Agent TUI.
Long WebChat planning loops now show their current phase and attempt instead
of appearing idle; reviewer rejection still blocks execution as designed.
No Protocol, Reverse Proxy or permission-policy changes.
See [release notes](docs/RELEASE_0.15.40.md).

## KITT 0.15.39 — lazy RE lab lifecycle and in-Agent setup

Release pins Agent CLI **0.87.15**. Windows/Linux reverse-engineering guest
profiles are created by the existing wizard, enrolled explicitly, and started
only when the operator uses a lab mission or the `/re` UI. Only
mission-started guests are stopped after the run; existing guests are
preserved. RE toolbox can be launched directly from the Agent CLI TUI.
See [release details](docs/RELEASE_0.15.39.md) and the
[Agent RE guide](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/RE_LAZY_ENVIRONMENTS.md).

## KITT 0.15.38 — KAP/2 K2 T host dispatch

Pins Agent CLI **0.87.13** plus updated Assistant and AI Workers
runtime locks, completing the tool-first Goals repair. Model K2 T
operations now reach canonical KAP/2 decoding before host policy and
execution. See [release notes](docs/RELEASE_0.15.38.md).

## KITT 0.15.37 — restore host-tool execution in durable Goals

The root pins Agent CLI **0.87.12** with a KAP/2 tool-first completion
contract, Assistant Runtime **0.3.24** and AI Workers **0.1.63**.
This fixes T00 loops returning `INCOMPLETE` without a single host tool
operation. See [release 0.15.37](docs/RELEASE_0.15.37.md).

## KITT 0.15.36 — T00 ChatGPT Web composer submission fix

The full preset now pins reverse-proxy **5.3.11**, which recovers
multi-KiB T00 prompts modified by ChatGPT's rich editor before submission.
The writer verifies exact normalized contents after its single bounded
recovery and again before pressing Send; it never submits a corrupted draft.
See [release details](docs/RELEASE_0.15.36.md).

## KITT 0.15.35 — DOM freshness capture for KAP/2

This release pins reverse-proxy **5.3.10** with an opt-in,
bounded post-submit DOM mutation capture fallback for ChatGPT/Gemini
KAP/2 frames. Prompts containing embedded KAP examples are not
accepted as fresh replies. No Agent CLI/Protocol grammar change.
See [release notes](docs/RELEASE_0.15.35.md).

## KITT 0.15.34 — compact KAP/2 final accepted end to end

The root pins reverse-proxy **5.3.9**, resolving the disagreement between
the proxy's generated KAP/2 decoder and canonical Protocol **0.13.3**.
A captured `K2 F @json: {...}\nK2/END` is now recognized by the proxy
contract validator and raw transport selector, with no duplicate parser
heuristics. The host still checks that a durable plan includes the mandatory
`FINAL` item, so incomplete plans cannot execute. See
[release 0.15.34](docs/RELEASE_0.15.34.md).

## KITT 0.15.33 — WebChat KAP/2 DOM recovery

Root pins Reverse Proxy 5.3.8, which detects one-line `K2 F @json`
replies, bounds the DOM fallback, and handles only deterministic Markdown
presentation escapes without relaxing canonical host validation.
See [release notes](docs/RELEASE_0.15.33.md).

# KITT 0.15.32 — lossless KAP/2 planning replies

The root manifest now pins Protocol 0.13.3, Agent CLI 0.87.11,
Reverse Proxy 5.3.7, Assistant Runtime 0.3.23 and AI Workers 0.1.62.
The planner uses explicit single-line `K2 F @json: {...} K2/END`
structured finals to survive WebChat whitespace flattening while host
schema validation and permissions remain strict. See
[release details](docs/RELEASE_0.15.32.md) and
[KAP/2 hard limits](docs/KAP2_LIMITS_0.15.32.md).

# KITT 0.15.31 — Safe Python via KAP/2

The full release snapshot pins Agent CLI **0.87.10** with the
`sandbox.python` host operation, Assistant Runtime **0.3.22**, and
AI Workers **0.1.61** with synchronized Python `uv.lock` references.
The executor reuses the existing `python_compute` restricted AST interpreter,
rather than allowing unrestricted Python. KAP/2 grammar and Protocol 0.13.2
remain unchanged. See [release 0.15.31](docs/RELEASE_0.15.31.md).

# Ecosystem 0.15.30 — KAP/2 DOM capture after transcript virtualization

The release installer pins Reverse Proxy **5.3.6** and validates its npm package/lock versions before building. The fix locates a fresh browser-rendered KAP envelope after the submitted prompt even if old chat DOM is virtualized; collapsed malformed frames are forwarded solely to the Agent repair flow. No changes to the other component pins. See [release 0.15.30](docs/RELEASE_0.15.30.md).

undefined