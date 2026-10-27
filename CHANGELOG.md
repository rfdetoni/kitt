# Changelog — K.I.T.T. Ecosystem

## 0.16.71 — release pin sync

- Update the release manifest for the latest Reverse Proxy commit.

## 0.16.70 — browser memory owned by Chrome

- Pin merged Reverse Proxy 5.4.28 (`b3caa28a1997a624e88db7422c69e94b02f3997b`) in the immutable release manifest.
- Remove browser RSS/PSS budgeting and memory-pressure session eviction: browser RAM is no longer sampled or managed by the proxy, allowing naturally growing ChatGPT Web conversations.
- Preserve page/session count limits, idle cleanup, in-flight and pending-tool protection, and consent-based browser setup.
- Reverse Proxy package and npm lock are synchronized; patched transitively resolved `qs@6.16.1` satisfies the newly published production dependency advisory without disabling the audit.
- All other ecosystem pins remain unchanged. The release still requires installer integration and immutable-pin CI before merge.


## 0.16.69 — model-budget checkpoint in Agent CLI 0.89.6

- Pin merged Agent CLI 0.89.6 (`69df41adee0c41354b0fd2768d658ff097c76bc8`) after green Docker, Podman, Windows package and regression CI.
- Preserve completed host tool receipts when a model-call/token/cost/duration budget is exhausted; return a recoverable `TurnBlocked` checkpoint without exceeding budgets or automatically replaying provider requests.
- Synchronize Agent CLI package/runtime/uv lock in its repository; update ecosystem immutable pin, version, installation docs and release notes.
- Preserve Reverse Proxy 5.4.27 and all other component pins. Chromium resource pressure and very large composer failures remain independently diagnosed, not disabled.


## 0.16.68 — Agent CLI 0.89.5: startup confiável e diagnósticos seguros

- Pin Agent CLI `0.89.5` (`7ab87087f321f2f13ef4207d6573ed12a303ae3b`) após merge e CI verde, com `pyproject.toml`, `uv.lock` e versão em código sincronizados.
- Antes da primeira requisição Chat, esperar de forma limitada e cancelável pelo Reverse Proxy local; invalidar descoberta de capacidades offline; não reproduzir solicitações já submetidas.
- O agente documenta que `flow.execute` é somente leitura e recomenda `process.run` governado em separado; logs das instâncias gerenciadas do proxy usam `metadata` como padrão.
- Documentar instalação completa com REA, AI Workers, Linux Docker RE, Ghidra/Frida, Dockur Windows 11 e imagens de VM.
- Preservar pins de Protocol, Memory, Toolbox, Assistant, AI Workers e Reverse Proxy; nenhuma alteração de dependência de terceiros foi necessária nesta atualização.


## 0.16.67 — verified task-root Autopilot isolation

- Pin Agent CLI 0.89.4 (`eaa4f198`) and Assistant runtime 0.4.46 (`727517fb`) at immutable main SHAs.
- Introduce isolated Git task worktrees for autonomous sandbox commands, verification and opt-in GitHub publication.
- Reject parent workspace mounts, tampered Git worktree metadata, absent durable state, and alternate host-write operations during active tasks; Docker and broker live tests included.
- Do not claim automatic local promotion: abandon retains task artifacts for audit, original checkout remains unchanged.
- Other protocol, proxy, toolbox and memory lock pins remain unchanged.


## 0.16.66 — Persistent Docker broker verified in real container integration

- Pin Agent CLI 0.89.3 (`1b17a65f`) and Assistant Runtime 0.4.45 (`44970484`), maintaining synchronized immutable SHA pins and Python dependency locks.
- Verify Docker broker worker reuse, cached HOME, readonly workspace, absent socket/control-plane files and worker reprovisioning through real Docker CI.
- Reject stale worker image/network/security config before reuse, and serialize commands per worker to avoid provisioning races.
- Keep GitHub publication operator opt-in and all other component SHA pins unchanged.


## 0.16.65 — Preauthorized verified GitHub Autopilot delivery

- Pin Agent CLI 0.89.2 (`105ebd7e`) with trusted `autopilot.publish` and Assistant runtime 0.4.44 (`30b21334`) with synchronized Python dependency and uv lock.
- Operator-controlled fixed repository/branch publication requires successful workspace validation, unchanged fingerprint and non-force GitHub branch update.
- Compose exposes only disabled-by-default publication parameters; credentials must be injected as Agent-only secrets outside the workspace.
- Retain other component pins and dependency locks; perform complete installer/lifecycle CI before merge.


## 0.16.64 — persistent Compose Autopilot and recoverable validation

- Pin Agent CLI 0.89.1 (`0ddae447`) and Assistant 0.4.43 (`296206af`) with trusted persistent broker, automatic mount discovery, task checkpoints/CAS rollback, strong verification gates and root-only network predelegation.
- Start `sandbox-broker` only with the Compose Agent profile, keeping Docker socket out of the Agent and worker containers; add readiness checks and dev overlay.
- Keep all other immutable component SHA pins/locks unchanged.
- Reconcile historical PRs by audit: superseded release branches are not blindly merged, nor are incompatible dependency PRs with red CI.


## Next — Unix broker in Compose agent profile

- Add sandbox-broker sidecar for the Agent Compose profile with a private Unix socket and persistent isolated Docker workers.
- Keep the Docker daemon socket exclusively in the broker, not the Agent or guest workers; disable bridge egress unless operator opts in.
- Reuse the existing workspace mount; guard broker readiness via healthcheck before starting Agent.
- Final Agent CLI version/immutable pin will be updated after verified merge.


## 0.16.63 — autonomous Docker toolchain selection hardening

- Pin merged Agent CLI 0.88.97 (`2a21ca81`), preferring trusted Docker toolchains over missing host binaries for autonomous development even where Bubblewrap works.
- Incorporate prior Agent CLI 0.88.96 Docker smoke validation, Gradle/JDK25 selection and avoidance of misrouting Git/inspection commands.
- Keep all other component SHA pins, platform installers and dependency locks unchanged; validate release installer contracts.


## 0.16.62 — Autonomous Docker Java/Node/Rust toolchain support

- Pin merged Agent CLI 0.88.95 (`46a37db1`) after passing Python regression, build, Docker, Podman and Windows CI checks.
- Autonomous Docker sandbox now selects fixed official Java 25/Maven, Node 24 and Rust worker images and provisions them on demand through trusted host Docker commands.
- Keep other component pins and dependency locks unchanged. Containerized Compose Agent still requires a host-authorized executor for arbitrary project commands.


## 0.16.61 — autonomous Git commands and strict network flags

- Pin Agent CLI v0.88.94 (`f07ca85a`) after green CI, adding Git metadata write support for autonomous Bubblewrap shell execution within an owned workspace.
- Fix network authority input validation to require exact booleans, denying numeric coercion before sandbox selection.
- Keep the other ecosystem SHA pins, installer source resolution, Docker fallback image policy and dependency locks unchanged.


## 0.16.60 — Autonomy sandbox worker preparation

- Pin Agent CLI 0.88.93 (`1f627845`), adding strongly isolated `sandbox.run` and Docker fallback when Bubblewrap is unavailable.
- On native Linux installs, verify or pull the sandbox Docker image without exposing the Docker socket to agent commands; report preparation failures explicitly.
- Document capability requirements, immutable Agent commit pin and the current Compose limitation; other component versions remain unchanged.


## 0.16.59 — Explicit Python verification check resolution

- Pin Agent CLI v0.88.92 (`3a45f25f`), fixing full-mode verification for explicitly required `python.targeted-tests` without bypassing host contracts or approvals.
- Keep Reverse Proxy v5.4.27 and all other component pins unchanged. Adds regression coverage for available and missing targeted Python tests.


## 0.16.58 — UI click timeout confirmation and duplicate-send protection

- Update immutable Reverse Proxy pin to v5.4.27 (6d3a1910). A timed-out Playwright send click now checks UI evidence before failure and never automatically retries an ambiguous submission.
- Keep Agent CLI v0.88.91 and every other component revision unchanged; validate release installation in CI.


## 0.16.57 — ACP v1 session replay and permission isolation

- Pin Agent CLI 0.88.91 to merged main. `session/load` replays ordered conversation text through session/update before its empty response, and `session/cancel` affects only the addressed session's permission requests.
- Fix redundant pip Git cloning of already checked-out internal KITT dependencies during main installation; resolve third-party requirements once and install internal packages locally with --no-deps. Add offline installer regression.
- Preserve all other component SHAs; run release installer, gateway and Assistant lock gates.


## 0.16.56 — ACP permissions, concurrency-safe reviews and live browser diagnostics

- Agent CLI 0.88.90: workspace-scoped ACP session load and consent flow, durable CAS review changes with per-path authorization, CLI review tools, parameterized recipes with checks/hooks, and reproducible review latency/memory measurement.
- Reverse Proxy 5.4.26: live origin-scoped Playwright console/network failure observations, bounded redaction, patched transitive body-parser/fast-uri and verified npm audit.
- Pin immutable merged-main revisions; leave all other ecosystem components unchanged. Verify end-to-end release installation, contracts and locks in CI.


## 0.16.55 — ACP IDE bridge and reviewable KITT workflows

- Pin Agent CLI 0.88.89 to merged main commit c513114cfbb1f24e4738b10c7ce915f13c0762fb, including an ACP v1 stdio endpoint, guarded review/apply/rewind and editable TOML recipes controlled by existing write permissions.
- Add bounded browser diagnostic summaries. Keep unchanged Protocol, Memory, Toolbox, Assistant, AI Workers and Reverse Proxy SHA pins, avoiding unnecessary companion rebuilds.
- Validate immutable release resolution, installer portability, end-to-end installation and assistant lock smoke in root CI. No third-party dependency additions.


## 0.16.54 — synchronized Agent MCP/recipe runtime and Reverse Proxy release pins

- Update immutable release pins to the verified Agent CLI and latest Reverse Proxy main revisions; keep all unchanged component SHAs pinned exactly.
- Release installers continue to resolve the full manifest atomically. No new protocol, native engine, or dependency changes.


## 0.16.53 — authenticated FreeLLMAPI model discovery

Pins Agent CLI 0.88.53 and Assistant Runtime 0.4.42 to immutable main commits. FreeLLMAPI now appears in the shared catalog and model picker; discovery sends the gateway credential and the models CLI respects the workspace endpoint. Locks and CI pins are synchronized. See [release notes](docs/RELEASE_0.16.53.md).

## 0.16.52 — FreeLLMAPI autonomous CLI execution

Pins Agent CLI 0.88.52 and Assistant Runtime 0.4.41 to immutable main commits. Fixes read-only plan JSON being inferred as a file write, adds native OpenAI-compatible tool round trips and visible CLI planning progress, preserves outer contract verification for native API goals, and bounds gateway retries. Saved authentication and supported output limits are reused without adding execution privileges. Assistant dependency, uv lock and CI pins are synchronized. Free provider capacity and actual Wine/Windows Oracle validation remain runtime requirements. See [release notes](docs/RELEASE_0.16.52.md).

## 0.16.51 — prevent repeated Gemini empty-action retries

Agent CLI 0.88.51 now confines `agent_contract_empty_action` recovery to another **configured, trusted** provider if one exists and no partial output was emitted. Otherwise the goal item is marked BLOCKED_ENV instead of rapidly resubmitting the identical task, preventing needless WebChat calls. It also clarifies root-relative file paths after inspecting nested project folders. Assistant Python Runtime 0.4.40 synchronizes its min Agent dependency, `uv.lock`, and both CI SHA pins. Reverse Proxy 5.4.22 retains the fail-closed empty-action validator; UI/Gemini generation quality and tap fallback latency are independent and not claimed fixed. All release components remain pinned to immutable merged-main SHAs; no new execution privileges or dependencies were introduced. [Release notes](docs/RELEASE_0.16.51.md).

## 0.16.50 — protected Git planning recovery and empty Gemini action guard

Pins merged Agent CLI 0.88.50 and Reverse Proxy 5.4.22 to correct three distinct failure modes reported on 2026-10-22. An automatic contract containing model-generated `.git` validation paths now requests a corrected plan instead of aborting with `Protected workspace path component: .git`; Git metadata remains inaccessible to workspace file tools. An empty Gemini action `{}` now fails immediately as a recoverable no-action response, avoiding a speculative browser repair that previously stalled for minutes. Assistant Python Runtime 0.4.39 updates its minimum Agent CLI dependency, lock and immutable CI checkout pins. An additional fix stops shell-wrapped public Git clone requests from triggering generic network approval modals and provides instructions for separate direct Git calls. No new dependency or sandbox permissions were introduced. [Release notes](docs/RELEASE_0.16.50.md).

## 0.16.49 — allow bounded child sessions under high Chromium startup RSS

The Wine-MBS logs of 2026-10-21 exposed `session_limit_exceeded` when the primary ChatGPT Web conversation was busy and its diagnostic child could not open a named session. Chromium already exceeded the configured 768 MiB memory cap at startup, while session/page-count quotas were otherwise available. This release pins Reverse Proxy 5.4.21: where the fixed startup RSS itself is over budget, one additional named child may be admitted within the original 512 MiB startup headroom. The third named session, excessive growth, hard page/count limits and busy-session eviction remain blocked. Agent CLI 0.88.48 and Assistant 0.4.37 retain the already-merged Git -C inspection fix; no changes to Agent or Assistant pins. [Release notes](docs/RELEASE_0.16.49.md).

## 0.16.48 — nested, read-only Git inspection in autonomous MBS workflow

Agent CLI 0.88.48 fixes `git -C mbs-wine status --short --branch` being hard-denied despite autonomy, preserving the existing read-only subcommand and workspace path checks. Assistant Python Runtime 0.4.37 pins the merged Agent revision; Reverse Proxy stays 5.4.20. The earlier public Git HTTPS checkout change from 0.16.47 remains intact. The 2026-10-21 MBS logs also show an independent memory-pressure refusal of a child Reverse Proxy session: this release does not increase the RSS limit or claim to eliminate model latency. [Release notes](docs/RELEASE_0.16.48.md).

## 0.16.47 — correct autonomous public Git clone approvals

Pins Agent CLI 0.88.47 and Assistant Python Runtime 0.4.36. In a root workspace autonomous turn with strong network sandbox, public Git source checkout via GitHub or GitLab can execute without the redundant `network.access` approval loop. General egress, other network commands, guest/path-scoped principals, and absent strong sandbox continue to require explicit authority. Reverse Proxy 5.4.20 remains unchanged. Regression covers the 2026-10-21 Wine/Wine-Staging submodule flow and blocked variants. Missing Ollama local models and slow downloads remain environment conditions. [Release notes](docs/RELEASE_0.16.47.md).

## 0.16.46 — recovery from SQLite repository index lock during KITT startup

Pins Agent CLI 0.88.46 with a bounded SQLite busy wait and safe per-process, non-persistent repository-index fallback when the daemon holds a writer transaction on the same workspace. Disk index/WAL are preserved, searches continue in-memory for the secondary instance, and permanent DB errors still propagate. Pins Assistant Python runtime 0.4.35 for the same immutable Agent revision; Reverse Proxy 5.4.20 is unchanged. Includes regression with a real concurrent SQLite writer. [Release notes](docs/RELEASE_0.16.46.md).

## 0.16.45 — safe agent-session continuity under Chromium memory pressure

Pins Reverse Proxy 5.4.20 to preserve recently active named sessions across host-tool execution gaps and to recheck RSS pressure after recycling stale sessions. The five-minute grace applies to background pressure sweeps; on-demand admission can still recycle idle isolated planning sessions before the executor's conversation. The configured session timeout, busy-session protection and resource admission limits remain intact. Retains Agent CLI 0.88.43, Assistant Runtime 0.4.33 and other immutable pins. CI and end-to-end release-channel installation remain required. [Notes](docs/RELEASE_0.16.45.md).

## 0.16.44 — guarded Begin Patch compatibility for Wine-MBS agents

Pins Agent CLI 0.88.43 and Assistant Runtime 0.4.33, keeping their immutable Python dependency and CI checkouts aligned. The Agent now accepts bounded `*** Begin Patch` updates through its existing content-anchored, path-constrained patch engine rather than rejecting the model's `*** Update File` hunk as a parse failure. Invalid, ambiguous, unanchored or out-of-workspace edits remain rejected. Preserves Reverse Proxy 5.4.18 and all other immutable component pins. The distinct `ui_capture_unverified` transport fault requires explicit safe continuation. [Notes](docs/RELEASE_0.16.44.md).

## 0.16.43 — bounded auto-continuation for durable Goals

Pins Agent CLI 0.88.42 and Assistant Runtime 0.4.32 (Python lock and CI checkout aligned to that Agent revision). A host-owned tool-budget checkpoint now requeues the same contract item without consuming a failed attempt; overall Goal turn, time, token and cost caps still apply, and unsupported CHECKPOINT reasons fail closed. Preserves Reverse Proxy 5.4.18 and all remaining immutable component SHAs from 0.16.42. See [release notes](docs/RELEASE_0.16.43.md).

## 0.16.42 — safer Agent CLI patches and Reverse Proxy memory admission

Pins Agent CLI 0.88.41 and Reverse Proxy 5.4.18. Agent patch parsing no longer treats version strings in later SEARCH/REPLACE blocks as new file targets; batch reads surface failed IDs without hiding successful siblings, and bounded default tool budgets accommodate larger implementation turns. Reverse Proxy only admits a first named Chromium session under bounded memory-growth headroom instead of unlimited baseline-pressure exceptions. Regression suites and component CI remain authoritative; this does not certify Windows guest Oracle behavior or eliminate Chromium's resident baseline.

## 0.16.41 — stable Goal tool-graph context and aligned release gates

Pins Agent CLI 0.88.40 (`78d7eaa`) and Assistant Runtime 0.4.31 (`2f39401`), retaining Reverse Proxy 5.4.17 (`e3fd97e`). Source code and locks now agree on the same Agent version, restoring the critical package metadata test. Read-only tool graphs and program receipts persist across Goals attempts, repository-wide evidence is invalidated after writes and semantic memory queries focus on the original objective. Existing C/Wine verification diagnostics, bounded parallel specialists and safe WebChat continuation remain intact. Protocol, Memory, Toolbox and AI Workers preserve their previous immutable SHAs. [Notes](docs/RELEASE_0.16.41.md).


## 0.16.40 — complete host-verification diagnostic handoff

Pins Agent CLI 0.88.39 (`f915302`) and Assistant Runtime 0.4.30 (`6c18d0d`) with Reverse Proxy 5.4.17 unchanged. Native C/C++ source builds that have no configured Makefile now explicitly report a bounded `UNAVAILABLE` diagnostic through the outer Goal, instead of generic failure messages. The release retains read-only tool graph guidance, persistent evidence, empty-memory status, parallel planning independence and explicit manual continuation for WebChat captures without verified provenance. Python/npm locks, immutable CI pins and root manifest are synchronized. Protocol, Memory, Toolbox and AI Workers remain unchanged. [Notes](docs/RELEASE_0.16.40.md).


## 0.16.39 — safe continuation across Agent/Proxy v5

Pins Agent CLI 0.88.38 (`0d28f07`), Assistant Runtime 0.4.29 (`b6d5347`) and Reverse Proxy 5.4.17 (`e3fd97e`). Completed WebChat UI turns that cannot be attributed to their request are recoverable by explicit operator continuation only and are never replayed automatically by the Goal scheduler. Includes read-only flow/program and code navigation guidance, preserved Goal receipts, empty-memory diagnostics, non-artificial parallel task dependencies and fail-closed Makefile-backed native C/C++ compilation checks. Locks and CI checkout pins match component SHAs; Protocol, Memory, Toolbox and AI Workers are unchanged. [Notes](docs/RELEASE_0.16.39.md).


## 0.16.38 — read-only tool orchestration, native verification and WebChat continuation

Pins Agent CLI 0.88.37 (`2a8aaad`), Assistant Runtime 0.4.28 (`9110d6e`) and Reverse Proxy 5.4.17 (`e3fd97e`). Agent prompts can leverage existing read-only flow/program operations, context handles, memory and structured symbol tools; Goal evidence survives read-only graph calls and planning favors independent scopes for existing parallel specialists. C/C++ source edits require a configured Makefile-backed build, otherwise validation blocks rather than asserting unsupported success. Reverse-Proxy returns safe explicit-continue signals and correlated capture diagnostics for completed unattributed WebChat replies, without implicit prompt replay. Python/npm locks and Agent/Assistant CI pins align with component main SHAs. Protocol, Memory, Toolbox and AI Workers remain unchanged. [Notes](docs/RELEASE_0.16.38.md).


## 0.16.37 — Bubblewrap resolver symlink mount fix

Pins Agent CLI 0.88.36 (`d76ef6a`) and Assistant Runtime 0.4.27 (`297a5bf`), retaining Reverse Proxy 5.4.16. The Agent runtime now avoids bind-mounting onto the systemd-resolved `/etc/resolv.conf` symlink while the Bubblewrap namespace masks `/run`; it selectively restores only canonical resolver targets for network-enabled profiles. Python locks and CI source pins are synchronized. Protocol, Memory, Toolbox, AI Workers and Reverse Proxy remain on their exact previous revisions. [Notes](docs/RELEASE_0.16.37.md).


## 0.16.36 — automatic secure Bubblewrap selection

Pins Agent CLI 0.88.35 (`89d30ef`) and Assistant Runtime 0.4.26 (`99e0611`) with Reverse Proxy 5.4.16 unchanged. The host enumerates all system and PATH Bubblewrap candidates, skips outdated or nonfunctional versions, reports AppArmor uid_map denials accurately and refreshes status after environment repairs. The Python runtime lock and Assistant CI pins are aligned. No AppArmor configuration or host capability is modified automatically; Protocol, Memory, Toolbox and AI Workers retain their prior immutable source revisions. [Notes](docs/RELEASE_0.16.36.md).


## 0.16.35 — preserve Goal read evidence and validate written paths

Pins Agent CLI 0.88.34 (`66e8b49`) and Assistant Runtime 0.4.25 (`399ac70`), retaining Reverse Proxy 5.4.16. The Goal loop persists bounded previous host read receipts and now captures canonical `repo.write_file` paths (including Markdown reports) for post-turn verification. Python locks and CI pins updated; unrelated Protocol, Memory, Toolbox and AI Workers stay at their existing exact main SHAs. [Notes](docs/RELEASE_0.16.35.md).


## 0.16.34 — durable Goal host evidence across retries

Pins Agent CLI 0.88.33 (`dc1333b`) and Assistant Runtime 0.4.24 (`a90b554`), with Reverse Proxy 5.4.16 unchanged (`d992cbe`). The Goal executor persists bounded read/list/search evidence into its existing session state; subsequent turns reuse prior receipts instead of starting discovery from scratch. Successful file mutations invalidate stale entries; successful members of partially failed batches are preserved. Agent/Assistant Python locks and immutable CI checkout pins align with this release. Protocol, Memory, Toolbox and AI Workers remain pinned to the same versions. [Notes](docs/RELEASE_0.16.34.md).


## 0.16.33 — Agent 0.88.32 no-progress loop and host-blocker fixes

Pins Agent CLI 0.88.32 (`f399bf6`), Assistant Runtime 0.4.23 (`fa6fad5`) and Reverse Proxy 5.4.16 (`d992cbe`). Repeated successful read-only batches now trigger bounded stagnation detection; repeated host denials and unavailable sandbox errors propagate as POLICY and ENVIRONMENT blockers respectively, never successful completion. Python uv.lock, Assistant source pins, release manifesto and notes are synchronized. Unchanged modules retain their existing immutable SHAs. [Notes](docs/RELEASE_0.16.33.md).


## 0.16.32 — explicit host sandbox preflight

Pins Agent CLI 0.88.31 (`fbb6029`) and Assistant Runtime 0.4.22 (`a1f7f68`), retaining Reverse Proxy 5.4.16 (`d992cbe`). Hosts without functional Bubblewrap >=0.12 now expose the blocker before the Agent attempts process.run; authorized repo mutations remain available, while unsafe unsandboxed fallback remains forbidden. The Python lock, Assistant CI immutable pins and root release manifest are aligned. [Notes](docs/RELEASE_0.16.32.md).


## 0.16.31 — verify Agent model identity before WebChat dispatch

Pins Reverse Proxy 5.4.16 (`d992cbe`) which rejects mismatched Agent Contract model IDs before browser submission, preventing a configured Gemini model from silently executing on a ChatGPT instance. Keeps Agent CLI 0.88.30 and Assistant Runtime 0.4.21 at their verified source pins. Protocol, Memory, Toolbox and AI Workers are unchanged. [Notes](docs/RELEASE_0.16.31.md).


## 0.16.30 — host reliability, context budgets, typed decision shadow and proxy sessions

Pins Agent CLI 0.88.30 (`dd63d72`), Reverse Proxy 5.4.15 (`23d86ef`) and Assistant Runtime 0.4.21 (`1901398`). Aligns Python/npm manifests, locks and Assistant CI source pins; the release manifest preserves exact current-main SHAs for Protocol, Memory, Toolbox and AI Workers. Improves resumable host checkpoints, scoped read batches, polyglot AGENTS.md inclusion, autonomous policy consistency, immutable child-model egress constraints and double-invalidation of browser session generations. Adds an opt-in System One decision benchmark; production routing and safety authorization remain unchanged until measured. [Notes](docs/RELEASE_0.16.30.md).


## 0.16.29 — Agent host-loop recovery and safe Reverse Proxy timeout handling

Pins Agent CLI 0.88.27 (`67bc827`) and Assistant Runtime 0.4.19 (`e1f5694`). Repeated host commands are blocked after an unavailable Bubblewrap sandbox; alternating failed commands and unchanged read results are recognized as stalled progress; ambiguous reverse-proxy WebChat request timeouts are not automatically replayed. Python runtime lock and both Assistant CI Agent source pins are aligned. Protocol, Memory, Toolbox, AI Workers and Reverse Proxy remain at their previous exact main SHAs; there is no new Wire/API protocol or Rust daemon behavior. [Notes](docs/RELEASE_0.16.29.md).


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
