# KITT 0.16.0 — JSON model wire across the ecosystem

Coordinates Protocol 0.14.0, Agent CLI 0.88.0, Reverse Proxy 5.4.0, Assistant 0.1.45 / Runtime 0.4.0, and AI Workers / Evals / Evolution 0.1.77. Memory and Toolbox contracts need no changes.

[Release details](docs/RELEASE_0.16.0.md).

## KITT 0.15.56 — offline multilingual lexical resources

Pins Agent CLI **0.87.30**, Assistant Runtime **0.3.37** and AI Workers **0.1.76**, preserving current Reverse Proxy **5.3.17**. Supports explicit operator-prepared UniMorph PT/EN/ES corpora, multilingual WordNet suggestion datasets and optional build-time wordfreq, Snowball or spaCy metadata, with no automatic downloads and no runtime NLP dependency. Run `python -m installer --semantic-help` for opt-in guidance. [Release details](docs/RELEASE_0.15.56.md).

## KITT 0.15.54 — explicit local semantic installer guidance

Pins Agent CLI **0.87.29**, Assistant Runtime **0.3.36** and AI Workers **0.1.75** from validated main commits, while preserving Reverse Proxy **5.3.16** and all other pinned components from 0.15.53. The central source-free installer now offers `python -m installer --semantic-help` for safe opt-in Ollama E5 preparation guidance; it performs no download and starts no services. Agent standalone installers support explicit `--prepare-semantic-model` (Linux) / `-PrepareSemanticModel` (Windows). [Release notes](docs/RELEASE_0.15.54.md).

## KITT 0.15.53 — current-turn WebChat capture

Pins Reverse Proxy **5.3.16**, fixing fresh tool actions mistaken for prompt echoes and lost rendered line boundaries. The release manifest refreshes all seven component pins to their current mains, including Agent CLI **0.87.29**. [Release details](docs/RELEASE_0.15.53.md).

## KITT 0.15.51 — live agent planning/review feedback

Pins Agent CLI **0.87.27**, Assistant Runtime **0.3.34**, and AI Workers **0.1.73**. Planning/review now exposes the current stage, retry number and real elapsed provider-wait time in TUI, without claiming work is complete while the remote LLM is still responding. Retains the FINAL contract-review convergence fix from 0.87.26. Protocol, Memory, Toolbox and Reverse Proxy pins are unchanged. [Release notes](docs/RELEASE_0.15.51.md).

## KITT 0.15.50 — reviewed planning convergence fix

Pins Agent CLI **0.87.26**, Assistant Runtime **0.3.33** and AI Workers **0.1.72**. The Agent contract planner now preserves authored FINAL criteria, paths and dependencies through high-risk independent review, avoiding systematic REVIEW → REVISE loops caused by implicit union of all task criteria. Each task is still verified independently; global contract limits remain in force. Protocol, Memory, Toolbox and Reverse Proxy pins unchanged. [Release details](docs/RELEASE_0.15.50.md).

## KITT 0.15.49 — automatically routed LLMs per specialist

Pins Agent CLI **0.87.25** (each Code/Creative/Investigator/Critic/Tester worker selects its own registered TaskRouter profile: Ollama, direct providers or separate reverse proxies, with fixed/preferred/automatic routing and bounded failover), Assistant Runtime **0.3.32**, and AI Workers **0.1.71**. Memory, Protocol, Toolbox and Reverse Proxy pins remain unchanged. [Release notes](docs/RELEASE_0.15.49.md).

## KITT 0.15.47 — extensible multi-agent specialist teams

Pins Agent CLI **0.87.23** (trusted declarative personas, Code/Creative/Investigator/Critic/Tester, CLI/TUI Agent Manager, scoped peer messaging and governed model delegation), Assistant Runtime **0.3.31**, and AI Workers **0.1.70**. Existing Protocol, Memory, Toolbox and Reverse Proxy pins remain unchanged. Specialists share the existing ChildAgentManager, GoalScheduler, PolicyEngine, isolated child sessions and budgets. [Release notes](docs/RELEASE_0.15.47.md).

## KITT 0.15.46 — reproducible FTS5 and LSH retrieval microbenchmark

Adds a dependency-free, deterministic comparison of SQLite FTS5 vs lexical LIKE, and 8-bit multi-probe LSH candidate retrieval vs exact cosine top-10. It reports p50/p95 and Recall@10 and is smoke-tested by ecosystem-main. Measurements are synthetic/Python-only and do not replace Rust, Ollama, or WebChat end-to-end profiling. [Methodology](docs/RELEASE_0.15.46.md).

## KITT 0.15.43 — Memory 0.10.2 and revision-safe durable embedding backfill

Pins Agent CLI 0.87.20, Memory 0.10.2, native Assistant 0.1.44 / Runtime 0.3.28 and AI Workers 0.1.67. The Memory vector index now refuses outdated embeddings by exact content hash, and pending workspace embeddings remain discoverable from SQLite across restarts. Assistant Cargo.lock resolves the exact Memory git commit pinned in this release. Existing Protocol, Toolbox and Reverse Proxy commits remain unchanged. [Release notes](docs/RELEASE_0.15.43.md).

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

## KITT 0.15.36 — T00 ChatGPT Web composer submission fix

The full preset now pins reverse-proxy **5.3.11**, which recovers
multi-KiB T00 prompts modified by ChatGPT's rich editor before submission.
The writer verifies exact normalized contents after its single bounded
recovery and again before pressing Send; it never submits a corrupted draft.
See [release details](docs/RELEASE_0.15.36.md).
