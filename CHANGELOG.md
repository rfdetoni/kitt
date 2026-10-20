# Changelog — K.I.T.T. Ecosystem

## 0.16.28 — contract-aware planning diagnostics

Pins Agent CLI 0.88.24 (`58ffe92`, PR #130) and Assistant Runtime 0.4.18 (PR #57). Agent planning now provides the exact plan.submit wire format; invalid proposals and premature verification receive actionable errors. Host sandbox failures state the Bubblewrap/user-namespace requirement instead of suggesting repeated approvals. Scope, capabilities, VM identity and mandatory host isolation remain unchanged. Existing Protocol, Memory, Toolbox, AI Workers and Reverse Proxy pins are preserved. [Notes](docs/RELEASE_0.16.28.md).

## 0.16.27 — Agent CLI allow-all e Assistant Runtime sincronizados

Promove Agent CLI 0.88.23 (`fa1ab23`, PR #129) e KITT Assistant Runtime 0.4.17 (`f332320`, PR #56), com atalho `A` que persiste autonomia para todo o workspace, `w` para permissão restrita a uma ferramenta e tratamento explícito de erro na mudança de perfil. Manifesto release utiliza SHAs imutáveis de ambas as branches `main`; Protocol, Memory, Toolbox, AI Workers e Reverse Proxy permanecem nos pins anteriores. Permissões de workspace, capacidades e requisitos de isolamento do host continuam aplicáveis. [Notas](docs/RELEASE_0.16.27.md).

## 0.16.26 — release metadata and immutable CLI / Assistant pins

Pins the validated Agent CLI 0.88.21 release source (`0484f2e`, PR #127) and Assistant 0.1.60 / Runtime 0.4.15 (`6b019b3`, PR #54). Aligns source fallback with Python package metadata, fixes the automatic release gate, and reconciles Assistant uv.lock/CI pin with the exact CLI source revision. Behavior of the autonomy and remembered approval fixes from 0.16.25 remains unchanged. All unrelated component pins are preserved. [Notes](docs/RELEASE_0.16.26.md).


## 0.16.25 — daemon autonomy reconciliation and durable approvals

Pins Agent CLI 0.88.21 (`306f312`, PR #126) and Assistant 0.1.59 / runtime 0.4.14 (`c2157a8`, PR #53). The TUI no longer resets daemon autonomy to a stale local preset at attach; it reads the daemon-authoritative effective profile. Persisted approval lists retain the authenticated principal identity required by workspace/session remembered approval rules. The Assistant build and Python lock pin Agent CLI 0.88.21. Reverse Proxy 5.4.14 and unrelated pins unchanged. [Notes](docs/RELEASE_0.16.25.md).


## 0.16.24 — approval hotkeys, bounded artifact and tool-catalog recovery

Pins Agent CLI 0.88.20 (`4a45488`, PR #125) and Reverse Proxy 5.4.14 (`9dc9e78`, PR #98). Fixes A/S/D keyboard navigation for autonomy and eager approval shortcuts, prevents recursive artifact retention, avoids replaying identical policy-denied actions, and bounds `request_tools` recovery to one attempt without inventing host tools. Component CI/Docker passed; pins and installer integration are verified by the ecosystem CI. Other components retain their 0.16.23 SHAs. [Notes](docs/RELEASE_0.16.24.md).


## 0.16.23 — native tools, sequential execution and explicit host actions

Pins Agent CLI 0.88.19 (`dc625e5`, PR #124) and Reverse Proxy 5.4.13 (`82c4c59`, PRs #96/#97). Restores native provider tool forwarding when the client sets `parallel_tool_calls=false`, keeps a single host action per loop, rejects prose-inferred tools, and uses existing bounded `repo.batch_read` for independent reads. Validated component CI/Docker; no authenticated WebChat speedup is claimed. Other ecosystem pins unchanged. [Notes](docs/RELEASE_0.16.23.md).


## 0.16.22 — validated agent/proxy contract and tool-loop performance

Pins Agent CLI 0.88.18 (`e768fdf`, PR #122) and Reverse Proxy 5.4.11 (`0d3b986`, inclui PR #94 e ajustes posteriores de contêiner). The Agent exposes its existing bounded batch-read operation in the exact model schema, extracts host-tool policy from the tool loop and avoids repeating generic guidance on every receipt; the proxy rejects empty final responses and unsafe broad contract repairs while separating validation from session orchestration. Component locks and release docs are synchronized. Protocol, Memory, Toolbox, Assistant and AI Workers retain their previous tested pins; no authenticated Gemini Web speedup is claimed. [Notas](docs/RELEASE_0.16.22.md).


## 0.16.21 — agent capability-first discovery and RE source staging

Pins Agent CLI 0.88.17 (`c5abeff`): host capability snapshot for agent-loop, consistent JSON tool envelope, context retrieval free from plan scaffolding, deterministic single-file planning, bounded discovery checkpoints and operator-only Wine-Staging source staging in the networkless RE shared workspace. uv.lock, regression tests and runbooks updated in Agent; all other immutable ecosystem pins unchanged. [Notas](docs/RELEASE_0.16.21.md).


## 0.16.20 — fixed isolated Wine pilot HOME

Promotes Agent CLI 0.88.16 (`38b0bf4`) to fix the isolated Windows-versus-Wine pilot failing because non-root Wine refused root-owned `HOME=/tmp`. The ephemeral container now initializes a private Wine HOME inside tmpfs, validates Windows receipts first and reports bounded nonzero Wine exit codes without exposing stderr. Preserves the existing Protocol, Memory, Assistant, Reverse Proxy, Toolbox and Workers immutable pins. [Notas](docs/RELEASE_0.16.20.md).


## 0.16.19 — Windows Oracle SSH diagnostics and dependency lock pins

Pins Agent CLI 0.88.15 (`037635b`): actionable SSH error classification, bounded read-only probe.info transport retry and OEM provisioning evidence; still no automatic probe.run replay or guest disk reset. Promotes CI-validated Memory serde_json/sha2/thiserror updates (`646a213`), compatible Assistant Cargo.lock (`6ef2201`), and Reverse Proxy Playwright patch (`9ea4644`). Protocol, Toolbox and AI Workers retain existing immutable pins. [Notas](docs/RELEASE_0.16.19.md).


## 0.16.18 — RE Linux guest WineHQ Staging

Pins Agent 0.88.13, signed Wine-Staging guest image 0.86.11, Assistant 0.1.58/Runtime 0.4.13 and Workers 0.1.83. Adds `kitt re lab upgrade-linux --approve` with rollback and /workspace/Windows preservation. [Notas](docs/RELEASE_0.16.18.md).

## 0.16.17 — UI composer recovery and RE guests MCP

Pins Reverse Proxy 5.4.10, Agent CLI 0.88.12, Assistant 0.1.57 / Runtime 0.4.12 and AI Workers 0.1.82. Repairs a one-character mutation in ChatGPT tool continuations and adds optional read-only guest status/Oracle readiness MCP. [Notas](docs/RELEASE_0.16.17.md).

## 0.16.16 — Centralized changelogs and synchronized immutable pins

Promotes Protocol 0.14.2, Agent CLI 0.88.11, Assistant 0.1.56 / Runtime 0.4.11, AI Workers 0.1.81, and documentation-only revisions of Reverse Proxy, Memory and Toolbox. Moves README release history to CHANGELOG.md and fixes immutable release hygiene. [Notas completas](docs/RELEASE_0.16.16.md).

Histórico de versões migrado integralmente do README. As notas detalhadas de cada versão permanecem em `docs/RELEASE_*.md`.

# KITT 0.16.15 — signed offline Clean-Room RE pipeline

Pins Agent 0.88.10, Protocol 0.14.1, Assistant 0.1.55/Runtime 0.4.10 and Workers 0.1.80. Adds local model image build and gated independent execution, without claiming Windows/Wine new-code conformance. [Release notes](docs/RELEASE_0.16.15.md).

# KITT 0.16.14 — guarded Clean-Room RE

Pins Agent 0.88.9, Protocol 0.14.1, Assistant 0.1.54/Runtime 0.4.9 and Workers 0.1.79. Strict black-box API contracts, private handoff seals, mandatory independent Ed25519 review signature and a SHA-pinned networkless offline implementer path are available; independent Windows/Wine end-to-end certification is still required. [Release notes](docs/RELEASE_0.16.14.md).

## KITT 0.16.13 — DeepSeek paused response and contract resilience

Pins Reverse Proxy 5.4.9 and DeepSeek plugin 1.2.1 to recognize the screenshot-observed `Servidor está temporariamente indisponível` / `Parado` / `Continuar` state, supporting deeply nested footer controls without clicking unrelated authorization UI or replaying prompts. Hardens JSON contract repairs with bounded context, serializer-only instructions and early exit on unchanged invalid responses. [Release notes](docs/RELEASE_0.16.13.md).

## KITT 0.16.12 — DeepSeek paused generation continuation

Pins Reverse Proxy 5.4.8 (after upstream CI/merge) to resume one confirmed assistant-only DeepSeek `Continue` button without replaying the prompt, and avoids delivering partial JSON. Unrelated login/consent/approval dialogs remain human-only. [Release note](docs/RELEASE_0.16.12.md).

## KITT 0.16.11 — DeepSeek 1.1.0 and ChatGPT Web capture recovery

Pins Reverse Proxy 5.4.7: DeepSeek final-answer-only DOM selectors, non-replayable ChatGPT `ui_capture_unverified` recovery via explicit `continue`, and deterministic two-sentence public summary normalization. Preserves the previous Agent CLI 0.88.8 / Assistant 0.1.53 pins. [Release details](docs/RELEASE_0.16.11.md).

## KITT 0.16.10 — Agent-owned Linux RE + Dockur Windows autosetup

With `--preset full --with-re-lab --yes --accept-windows-license`, the root installer delegates to Agent CLI 0.88.8 (`kitt re lab setup`). The official Dockur image is pinned by digest; OEM configures OpenSSH and SHA-pinned probes. Wine runs the fixed differential pilot in a separate restricted container. `kitt re lab recreate` requires a recent scope-bound confirmation token. **Live Windows/KVM E2E is unverified.** [Guide](docs/RELEASE_0.16.10.md).

# KITT 0.16.9 — reuse existing Docker RE Linux and Dockur Windows environments

Pins **Agent CLI 0.88.5**, **Assistant 0.1.50** / **Python Runtime 0.4.5**. Docker is automatically preferred over Podman when both engines are operational; an explicitly requested engine is never silently replaced. The Agent recognizes the installer-owned Linux RE toolbox (`kitt-re-full`) and Dockur Windows (`kitt-re-win11`), checks container ownership and isolation before read-only inventory or operator lifecycle actions, and avoids requiring another ISO for the existing Docker lab. Windows remains non-oracle without authenticated guest probes. Other ecosystem SHA pins remain unchanged.

[Release details](docs/RELEASE_0.16.9.md).

# KITT 0.16.8 — durable approvals, scoped parallelism and synchronized dependencies

Pins Agent CLI **0.88.4**, Assistant **0.1.49** / Python Runtime **0.4.4**. Approval requests persist before display and cannot reopen after a decision; pending actions resume the exact host-approved tool and retain mutation preconditions. Goal parallel batches prioritize the scheduler's current task and prevent overlapping path scopes. The Agent, Assistant and release manifest are coordinated by immutable commit SHAs. Protocol 0.14.0, Memory 0.10.2, Toolbox 0.4.3, AI Workers 0.1.78 remain unchanged. Reverse Proxy **5.4.5** fixes response extraction after uniquely rendered prompts while retaining fail-closed behavior for ambiguous WebChat output.

[Release details](docs/RELEASE_0.16.8.md).

# KITT 0.16.7 — complete autonomous and approved process flow

Pins Agent CLI 0.88.3 and Assistant 0.1.48 / Runtime 0.4.3. User-selected allow-all now applies to inline Python/Node processes. Manual approvals persist the exact effective tool and payload, pass the waiting Goal's approval fence, and resume its contract once after evidence persistence. Plain fallback uses the same contract approval owner.

[Release details](docs/RELEASE_0.16.7.md).

# KITT 0.16.6 — approvals resume without reopening the permission modal

Pins Agent CLI 0.88.2 and Assistant 0.1.47 / Runtime 0.4.2. Saving a remembered allow rule no longer invalidates the explicitly approved waiting action. Revocations and other authority changes still block execution. Terminal execution failures are acknowledged separately from approval decisions, so the TUI closes the request and displays its error instead of asking again.

[Release details](docs/RELEASE_0.16.6.md).

# KITT 0.16.5 — bounded planning and local JSON result normalization

Pins Agent CLI 0.88.1, Reverse Proxy 5.4.4, Assistant 0.1.46 / Runtime 0.4.1 and Workers / Evals / Evolution 0.1.78. Updated runtime and consumer locks resolve the same Agent commit. Protocol 0.14.0 remains JSON Agent v5; Memory and Toolbox pins are unchanged.

[Release details](docs/RELEASE_0.16.5.md).

# KITT 0.16.4 — assistant patch decoding and terminal response recovery

Pins Reverse Proxy 5.4.3 for ordered assistant patch batches, complete escape presentation and recovery of a complete response after SSE EOF followed by a connection failure. Thoughts, metadata copies, partial and ambiguous responses remain excluded. [Release details](docs/RELEASE_0.16.4.md).

# KITT 0.16.3 — rendered prompt exclusion and generation sequencing

Pins Reverse Proxy 5.4.2: rejects JSON examples from the prompt despite rendering whitespace changes, waits for DOM generation to finish, and captures the next turn baseline after the previous answer completes. Busy waits preserve drafts and support cancellation. [Release details](docs/RELEASE_0.16.3.md).

# KITT 0.16.2 — JSON response capture and faithful repair

Pins Reverse Proxy 5.4.1: complete JSON reaches host validation before Agent schema checks, and bounded repair may wrap an unchanged structured result as `final_response`. Tool execution still requires the full contract and host authorization. Includes bounded opt-in capture diagnostics. [Release details](docs/RELEASE_0.16.2.md).

# KITT 0.16.1 — validated JSON ecosystem composition

Retains the JSON Agent contract v5 migration from [0.16.0](RELEASE_0.16.0.md), with final Agent, Assistant and Workers commit pins. Agent's static CI checks now pass, the release companion uses the JSON-compatible Assistant runtime, Assistant CI checks out the matching Agent revision, and third-party Rust registry versions/checksums remain unchanged.

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
