# K.I.T.T. Ecosystem

<p align="center">
  <strong>Local-first agent ecosystem for coding, automation, memory and resident AI.</strong><br>
  Agent CLI · native acceleration · persistent memory · assistant daemon · AI workers · authorized web gateway
</p>

<p align="center">
  <a href="https://github.com/rfdetoni/kitt/blob/main/LICENSE"><img alt="License MIT" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
  <img alt="Platforms" src="https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.14%2B-3776AB?logo=python&logoColor=white">
  <img alt="Rust" src="https://img.shields.io/badge/Rust-native-000000?logo=rust&logoColor=white">
</p>

K.I.T.T. is a modular, local-first AI ecosystem centered on a high-performance autonomous coding agent. Flexible orchestration stays in Python and TypeScript; deterministic CPU/data-plane work can run in Rust; heavy AI/ML workloads are isolated into on-demand workers; browser-backed provider access remains inside a dedicated gateway.

This repository is the **distribution and composition point** for the ecosystem. `edge` tracks component `main` branches; `release` installs the immutable snapshot in `ecosystem.release.json`.

---

## Ecosystem 0.13.7 — final local agentic acceptance hardening

This snapshot composes Agent CLI **0.83.13** at `5757bb21808c`. The Agent now has executed acceptance evidence for original AuthoritySnapshot enforcement on managed-process control, real Git worktree isolation/integration/discard, compaction retention of critical execution diagnostics, deterministic no-progress/reread detection, explicit approval for opaque interpreter wrappers even under `allow-all`, privacy-safe `kitt learn`, and no automatic A/B promotion.

PR validation also exercises real **Docker and Podman** provision/pause/resume/replacement persistence. Protocol **0.9.0**, Memory **0.9.1**, Reverse Proxy **4.9.4**, Toolbox **0.4.0**, Assistant **0.1.18** / Runtime **0.2.32**, and AI Workers **0.1.42** remain unchanged because this slice adds no cross-repository schema or contract change.

## Ecosystem 0.13.6 — conversation concurrency and recovery acceptance

This snapshot composes Agent CLI **0.83.12** with consumers validated against the same Agent SHA. Active turns in one conversation are serialized at admission, while distinct conversations remain parallel. Deterministic acceptance checks now cover FIFO resource contention without deadlock, selective rollback, exact workspace snapshot/artifact recovery and bounded large-artifact query/page retrieval.

Protocol **0.9.0**, Memory **0.9.1**, Reverse Proxy **4.9.4** and Toolbox **0.4.0** keep their existing runtime release pins; this slice introduces no Protocol v2 or new coordination authority.

## Ecosystem 0.13.5 — runtime integrity and cross-platform evidence

This snapshot composes Agent CLI **0.83.11**, Protocol **0.9.0**, Memory **0.9.1**, Reverse Proxy **4.9.4**, Toolbox **0.4.0**, Assistant **0.1.18** / Runtime **0.2.32**, and AI Workers **0.1.42**.

The Agent hardens artifact GC against shared-blob reference races, renews long-running mutation leases, and recovers prompt capacity after blocked cancellations while bounding total live producer threads. Memory now has real `kitt-memoryd` process restart/reclaim evidence for leased jobs. Protocol adds generated/adversarial decoder coverage without changing wire v1. Because those Protocol/Memory changes are test/workflow-only, the immutable release manifest intentionally keeps their published runtime tag SHAs (`v0.9.0` / `v0.9.1`) instead of pretending the evidence commits are new package releases.

Ecosystem CI keeps the full Ubuntu installation/release gates and adds minimal portable Agent installation smokes on **Windows** and **macOS**, verifying platform-specific installer state, launchers and Agent startup without duplicating the heavy native suite.

## Ecosystem 0.13.4 — final consumer lock reconciliation

This release keeps the same Protocol 0.9/wire-v1 architecture and updates the composed Assistant and AI Workers SHAs after final cross-repository lock reconciliation. Assistant now validates against Agent CLI **0.83.9**, resolves Memory **0.9.1**, and aligns the native HUD with Protocol **0.9.0**; AI Workers locks resolve Agent CLI **0.83.9** and Protocol **0.9.0**.

Protocol v2 remains deliberately unnecessary: the structural Agent ↔ Reverse Proxy boundary is already canonical, Protocol/Proxy context schemas are identical, and no shared wire break is required. The Reverse Proxy `agent-contract v2` remains a provider/WebChat response contract, not KITT Protocol v2.

Release integration now also exercises a non-portable Assistant release smoke so the current manifest cannot silently pin Memory/Protocol SHAs that disagree with the Assistant Cargo/npm locks.
## Ecosystem 0.13.3 — integrated P1/P2 snapshot

This release composes the post-wave validated heads: Agent CLI **0.83.9**, Reverse Proxy **4.9.4**, Protocol **0.9.0** (wire v1), Memory **0.9.1**, Toolbox **0.4.0**, Assistant **0.1.18** / Runtime **0.2.32**, and AI Workers **0.1.42**.

Protocol v2 was deliberately not introduced: the Protocol-generated context schema and the Proxy copy are aligned, request metadata fields remain compatible, and the Agent/Proxy structural-contract work required no shared wire break. The Proxy's `agent-contract v2` is its WebChat response contract and is not KITT Protocol v2.

The `release` channel pins the exact validated SHAs in `ecosystem.release.json`; `edge` continues to resolve component `main` branches. Existing integration gates prove immutable release installation, schema parity, and fail-closed lock mismatch behavior.

## Ecosystem 0.13.1 — Agent 0.83.7 release snapshot

The distribution now has two explicit channels: `edge` follows component `main` branches, while `release` installs only the SHAs in `ecosystem.release.json`. Release composition fails closed when the Assistant Cargo/npm locks do not match the Protocol/Memory pins, and Python sibling packages are installed from the root-selected checkouts instead of silently resolving K.I.T.T. dependencies from a newer `main`.

The validated snapshot pins Agent CLI `c5802cbcd638` (v0.83.7), Reverse Proxy `90e8b7b91293`, Assistant `978c5c9a66fb`, Protocol `f1c17df15c64`, Memory `ad0e99b62ff5`, Toolbox `3d81ad110354` and AI Workers `9336a4e21b3c`.

## Ecosystem 0.12.0 — bounded gateway lifecycle

This distribution composes Agent CLI **0.83.3**, Protocol **0.8.0**, Reverse Proxy **4.9.1**, Memory **0.8.1**, Toolbox **0.3.0**, Assistant Runtime **0.2.30** (native/HUD **0.1.16**) and AI Workers **0.1.42** from `main`.

The gateway shares the Agent wallet across bounded repairs, enforces processing locality, commits context acknowledgements after successful responses, and preserves uncertain request identity. Streaming, cancellation, daemon shutdown, file cursors and IPC resources have explicit bounds. Contracts remain owned by Protocol; consumers reuse Agent policy.

See [docs/GATEWAY_RELEASE_0.12.0.md](docs/GATEWAY_RELEASE_0.12.0.md) for findings, validation, source revisions and remaining limitations.

## Ecosystem 0.11.0 — host-owned planning and scoped verification

The 0.11.0 distribution composes Agent CLI **0.82.0**, Protocol **0.7.0**, Reverse Proxy **4.8.0**, Memory **0.7.0**, Toolbox **0.2.9**, Assistant **0.1.15** / Runtime **0.2.27** and AI Workers **0.1.40** from their current `main` branches.

The Agent adds optional bounded task DAGs, dependency readiness, host-assigned task IDs, structured child reports and registered verification checks within the existing EventLedger, ToolRegistry and global turn budget. Child admission is serialized, leaf workers cannot delegate, cancelled children cannot be resurrected by late results, and POSIX workers supervise parent loss. Rollback protects newer concurrent edits and human approval waits pause active duration accounting.

Protocol owns the shared planning/evidence shapes and hierarchical request metadata. The Proxy requires typed host evidence for agent-loop completion and ignores stdout success markers. Memory, Assistant, Toolbox and Workers keep their existing ownership and versions. The installer continues to resolve `main` into per-run SHAs rather than freezing this document's release snapshot.

See [docs/AGENTIC_RELEASE_0.11.0.md](docs/AGENTIC_RELEASE_0.11.0.md) for source SHAs, checks, compatibility, deliberate deferrals and the 30 provider E2E gates that remain pending.

---

## What’s included

| Component | Responsibility | Primary technology |
| --- | --- | --- |
| [`kitt-agent-cli`](https://github.com/rfdetoni/kitt-agent-cli) | autonomous coding-agent control plane | Python + SQLite/FTS5 |
| [`kitt-reverse-proxy`](https://github.com/rfdetoni/kitt-reverse-proxy) | authorized web-chat/API gateway with versioned provider plugins | TypeScript/Node.js + Playwright |
| [`kitt-assistant`](https://github.com/rfdetoni/kitt-assistant) | resident assistant, daemon and Control Center | Rust + web + Python runtime |
| [`kitt-protocol`](https://github.com/rfdetoni/kitt-protocol) | cross-component contracts and SDKs | Rust + Python + TypeScript |
| [`kitt-memory`](https://github.com/rfdetoni/kitt-memory) | shared persistent memory engine | Rust + SQLite WAL |
| [`kitt-toolbox`](https://github.com/rfdetoni/kitt-toolbox) | native code/system data plane and Python accelerator | Rust + PyO3 |
| [`kitt-ai-workers`](https://github.com/rfdetoni/kitt-ai-workers) | Evolution/Evals and optional heavy AI/ML workers | Python |

The Python distributions compose through the shared `kitt.*` namespace instead of vendoring the same implementation into multiple repositories.

---

## Quick links

- **Install the complete Agent stack:** use the installer below.
- **Run the coding agent:** `kitt`
- **Manage the browser/API gateway:** open `Ctrl+P -> KITT Reverse Proxy` in Agent CLI or use `kitt-reverse-proxy service list --json`
- **Develop WebChat providers:** use the versioned `kitt-reverse-proxy/plugin-sdk` contract.
- **GHCR packages:** https://github.com/rfdetoni?tab=packages
- **Inspect the resident service:** `kittctl service status`
- **Evolution runs:** `kitt evolve runs`
- **Security:** [SECURITY.md](SECURITY.md)
- **Architecture and bounded contexts:** [docs/ECOSYSTEM_ARCHITECTURE.md](docs/ECOSYSTEM_ARCHITECTURE.md)

---

## Requirements & compatibility

Requirements are calculated from the selected module set rather than globally hard-coded. A normal complete Agent installation currently uses:

- Git;
- Python **3.14+**;
- Node.js **24+** and npm;
- Rust **1.90+** and Cargo.

The shell/PowerShell bootstrap can start with Python **3.10+** only to launch the installer. The selected runtime is then checked against the catalog and a complete Agent installation requires Python **3.14+**. CI exercises the complete stack at its declared floors (Python 3.14, Node 24 and Rust 1.90) rather than relying on newer toolchains.

Windows, Linux and macOS are first-class targets. Other POSIX systems use the generic POSIX adapter when the selected upstream toolchains support the OS.

`--portable` is an explicit degraded mode that skips native builds where a portable fallback exists. It is not the default for a complete installation.

---

## Installation

### Linux / macOS / POSIX

```bash
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | sh
```

### Windows PowerShell

```powershell
irm https://raw.githubusercontent.com/rfdetoni/kitt/main/install.ps1 | iex
```

The installer presents K.I.T.T. modules interactively. Explicit selections are marked `[x]`; transitively required technologies are marked `[+]`. Protocol and Memory are internal composition dependencies, so they remain visible but cannot be selected as misleading standalone installs.


Before an install or update replaces any runtime artifact, the ecosystem installer now quiesces registered K.I.T.T. services and narrowly matched resident processes (daemon, Assistant, Reverse Proxy and Agent Gateway). This prevents an old Python/Node process from retaining pre-update modules in memory while the on-disk installation already points at a newer component revision. Interactive Agent clients are not targeted by the fallback process matcher.

### Complete Agent guarantee

Selecting **KITT Agent CLI** resolves the full technology stack that the Agent integrates with:

```text
KITT Agent CLI
  + KITT Protocol
  + KITT Memory
  + KITT Toolbox
  + KITT Assistant
  + KITT AI Workers (base + Evolution/Evals)
  + KITT Reverse Proxy
```

The catalog resolver and CI enforce this relationship so the Agent is not silently installed as an incomplete subset simply because capabilities are owned by separate repositories.

### Human approval continuity

The main-tracking Agent stack keeps tool/command approval prompts active until the user decides. `kitt-agent-cli 0.82.0` persists `PENDING` approvals without a wall-clock timeout, revalidates authority snapshots before resume and scopes remembered permissions by workspace/executable identity. `kitt-assistant-runtime 0.2.27` transports the same saved-permission identity in daemon mode, while `kitt-reverse-proxy 4.8.0` keeps recoverable model-response sessions available for Continue/Retry. Grant TTLs remain short-lived and single-use after approval.

Heavy STT/ML dependencies remain opt-in because they are hardware- and workload-specific. Enable them with `--with-ai-workers`.



### Integrated Reverse Proxy control center

The current Agent stack tracks the latest compatible `main` revisions, including Agent CLI 0.82.0 and Reverse Proxy 4.8.0 at the time of this update. From the full-screen TUI, open **KITT Reverse Proxy** through `Ctrl+P` or `/reverse-proxy`. The modal is painted immediately, then loads its control-plane snapshot, and can start a provider-plugin service directly from **Novo serviço**. Use it to:

- run multiple reverse-proxy instances at once;
- use named browser profiles and provider plugins;
- start from a provider plugin or a custom WebChat URL;
- stop/restart individual proxy instances;
- bind independent instances to Context, Principal/Code and Validation roles;
- operate the main configuration menus with keyboard or mouse, including visible hover feedback on Reverse Proxy actions;
- scroll retained modal content without wheel events leaking to the transcript;
- render modal text without raw ANSI/CSI escape artifacts.

A supported dual-provider topology is:

```text
Context        -> Gemini Web  -> gemini-context -> local endpoint A
Principal/Code -> ChatGPT Web -> chatgpt-code   -> local endpoint B
```

The TUI automatically consumes the reverse-proxy machine-readable control plane; it does not inspect OS process tables or hard-code the provider plugin list. Mouse interaction uses Agent-owned local-cell hit regions inspired by OpenTUI interaction principles while retaining the existing Python/prompt_toolkit renderer.


---

## Docker

Docker is an optional execution path, not a requirement for K.I.T.T. The root `compose.yaml` isolates the hot-path Agent control plane, reverse proxy and browser into separate containers while keeping native installation available for the complete resident/native stack.

The default topology is:

```text
Agent CLI ──HTTP──> Reverse Proxy ──CDP──> Chromium sidecar
    │                    │                    │
/workspace          localhost:3000      persistent profile
                                         + optional noVNC
```

The browser runs **headless by default**. CDP port `9222` stays private to the Compose network; only the proxy API and optional noVNC UI are published on host loopback.

### Published images

Component release workflows publish the Docker images to GitHub Container Registry:

```text
ghcr.io/rfdetoni/kitt-agent-cli
ghcr.io/rfdetoni/kitt-reverse-proxy
ghcr.io/rfdetoni/kitt-reverse-proxy-browser
ghcr.io/rfdetoni/kitt-reverse-proxy-standalone
```

GHCR packages index: https://github.com/rfdetoni?tab=packages

GitHub creates each direct package page after that image is pushed for the first time, so the README links to the stable packages index rather than to package-specific pages that may not exist before the first release.

Stable releases publish `vMAJOR.MINOR.PATCH`, `MAJOR.MINOR.PATCH`, `MAJOR.MINOR`, `MAJOR` and `latest` aliases. `latest` follows the newest stable component release. For reproducible environments, pin `KITT_AGENT_VERSION` and `KITT_REVERSE_PROXY_VERSION` to complete release tags; the browser sidecar intentionally uses the same version as the reverse proxy.

### Start the Docker stack

```bash
cp .env.docker.example .env
# Replace KITT_PROXY_API_KEY with a strong local secret, for example:
openssl rand -hex 32

docker compose up -d browser reverse-proxy
docker compose run --rm agent
```

The Compose services contain both `image:` and `build:` definitions. Docker Compose therefore prefers the GHCR release image and falls back to building the corresponding repository source if that image is not available yet. A separate `docker compose build` is not required for normal startup.

To pre-fetch already-published images explicitly:

```bash
docker compose --profile agent pull browser reverse-proxy agent
```

Inside the Agent container, the OpenAI-compatible reverse-proxy endpoint is `http://reverse-proxy:3000/v1`. Use the same API key configured as `KITT_PROXY_API_KEY` in `.env`.

The Agent service mounts `KITT_WORKSPACE` at `/workspace` and persists its state in a named volume. The container deliberately does not mount the Docker socket, host root filesystem or run privileged. Project-specific toolchains are also not injected automatically; derive a project image or prefer native K.I.T.T. when the Agent must execute SDKs not present in the base image.

Host services such as Ollama or LM Studio can be reached through `host.docker.internal`; the Compose file adds the Linux `host-gateway` mapping to the Agent container.

### Pin component releases

The Agent and reverse proxy evolve independently, so their release versions do not need to match. For example:

```env
KITT_AGENT_VERSION=vMAJOR.MINOR.PATCH
KITT_REVERSE_PROXY_VERSION=vMAJOR.MINOR.PATCH
```

You can also override the image repository through `KITT_AGENT_IMAGE`, `KITT_REVERSE_PROXY_IMAGE` and `KITT_BROWSER_IMAGE`, for example when mirroring GHCR into a private registry.

### Build unreleased source

`compose.dev.yaml` keeps development image names separate from release images while reusing the source build definitions:

```bash
docker compose -f compose.yaml -f compose.dev.yaml --profile agent build
docker compose -f compose.yaml -f compose.dev.yaml up -d browser reverse-proxy
docker compose -f compose.yaml -f compose.dev.yaml run --rm agent
```

`KITT_AGENT_REF` and `KITT_REVERSE_PROXY_REF` select the branch, tag or commit used for those source builds.

### Manual browser authentication

When a provider needs login, CAPTCHA or another manual browser step, temporarily enable headed mode:

```bash
KITT_BROWSER_MODE=headed docker compose up -d browser reverse-proxy
```

Open:

```text
http://127.0.0.1:6080/vnc.html?autoconnect=1&resize=remote
```

Complete authentication manually, return `KITT_BROWSER_MODE` to `headless`, and recreate the browser container:

```bash
docker compose up -d --force-recreate browser
```

The browser profile is stored in `kitt-browser-profile`, so authenticated state survives normal container replacement. Treat that volume as credential material. `docker compose down` keeps it; `docker compose down -v` deletes it together with the Agent state volume.

The native installer remains the canonical path when you need the complete Assistant/Memory/Toolbox/AI-Workers composition and native acceleration in one local installation.

---

## Non-interactive & advanced installation

Install the default complete Agent stack without prompts:

```bash
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | KITT_NON_INTERACTIVE=1 sh
```

PowerShell:

```powershell
$env:KITT_NON_INTERACTIVE='1'; irm https://raw.githubusercontent.com/rfdetoni/kitt/main/install.ps1 | iex
```

Enable verbose repository/build output:

```bash
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | KITT_VERBOSE=1 sh
```

Resolve the dependency graph without changing the machine:

```bash
python -m installer --modules agent-cli --dry-run
```

Useful options:

```text
--preset agent|agent-proxy-minimal|assistant|web|full
--modules <id[,id...]>
--channel edge|release
--with-ai-workers
--force
--no-start-services
--portable
--ref main|<branch|tag|sha>
--verbose
--uninstall
```

---

## Running K.I.T.T.

After installation:

```bash
kitt
kitt --root /path/to/project
kitt models
kitt doctor
kitt-reverse-proxy start chatgpt
kittctl service status
```

Self-evolution remains staged and explicit:

```bash
kitt evolve runs
kitt evolve skill <skill-name>
kitt evolve promote <run-id>
```

Evolution candidates never replace live skills automatically; promotion happens only after evaluation and adversarial review.

---

## Architecture

```text
                         ┌─────────────────────┐
                         │   K.I.T.T. Agent    │
                         │  Python control     │
                         │      plane          │
                         └─────────┬───────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
  KITT Protocol             KITT Toolbox             KITT Memory
  shared contracts          native data plane        persistent memory
          │                        │                        │
          └──────────────┬─────────┴──────────┬─────────────┘
                         │                    │
                         ▼                    ▼
                  KITT Assistant       KITT AI Workers
                  resident runtime     isolated heavy work
                         │
                         ▼
                  Reverse Proxy
                  provider gateway + plugins
```

The ownership rule is intentional: components communicate through versioned contracts and separately packaged capabilities instead of duplicating implementation code.

---

## Installer & release integrity

`ecosystem.json` defines the module graph. `ecosystem.release.json` pins the immutable release SHAs.

- `--channel edge` (default) resolves component `main` branches.
- `--channel release` resolves manifest SHAs and requires matching component lockfiles.
- `--ref <branch|tag|sha>` is an edge-only diagnostic override.
- `installed-state.json` records channel and resolved revisions.

---

## Security & privacy

K.I.T.T. is designed around explicit trust boundaries:

- local services prefer loopback/private interfaces;
- credentials stay outside model-visible context;
- tool execution is governed by capabilities and approvals;
- secret/private memory has egress restrictions;
- browser sessions are isolated in the reverse proxy;
- CAPTCHA and provider security controls are never bypassed;
- process output, protocol frames and resource usage are bounded where practical.

See the root [SECURITY.md](SECURITY.md) plus component-specific security documentation.

---

## Development

Validate installer and ecosystem invariants:

```bash
python -m unittest discover -s tests -v
python scripts/validate_ecosystem_main.py
python scripts/validate_architecture.py
python -m installer --modules agent-cli --dry-run --portable
```

The broader integration workflow resolves the current component `main` branches once per CI run, validates Rust workspaces, the PyO3 wheel, Python namespace composition, Agent CLI, Assistant, Protocol, Memory, AI Workers and Reverse Proxy, and performs a clean non-portable Linux installation through the real installer. It runs `pip check`, exercises installed launchers and verifies source cleanup and recorded provenance.

Each component repository also owns its technology-specific unit tests and lint/build checks.

---

## Contributing

Changes should keep repository ownership boundaries clear, preserve local-first security defaults and avoid adding dependencies to the hot path without a measurable benefit. Cross-repository changes should keep shared contracts and sibling `main` branches compatible because the installer composes them directly.

---

## Project principles

1. **Local-first by default.** Remote providers are integrations, not the center of the architecture.
2. **Fast hot path.** Keep orchestration lightweight and move deterministic heavy work to native components when it materially helps.
3. **Explicit authority.** Agents act through capability, approval and workspace boundaries.
4. **Composable components.** Share contracts and namespaces instead of vendoring copies.
5. **Bounded resources.** Queues, frames, outputs and telemetry should have explicit limits.
6. **Reviewable evolution.** Self-improvement is measured and promoted, never silently self-deployed.

---

## License

MIT. See [LICENSE](LICENSE).

### Snapshot 0.9.17 — consistency and lifecycle hardening

The promoted ecosystem pairs **KITT Memory 0.2.1**, **Protocol 0.2.1**, **Assistant 0.1.6 / runtime 0.2.18**, **Agent CLI 0.74.6**, **AI Workers 0.1.24**, **Toolbox 0.2.9** and **Reverse Proxy 4.4.1**.

This snapshot hardens reverse-proxy process ownership against PID reuse, serializes its multi-process control plane, verifies service readiness before publication and bounds session shutdown. The Agent release image is also aligned to Python 3.14 and uses the refreshed Docker build actions. Agent memory now has deterministic local structured authority with shared-memory mirroring/merged recall, project clearing covers structured/shared records, Markdown fallback is locked/atomic, and default files no longer fabricate user preferences. Approval denial is durable-first, daemon protocol versioning is unified, HUD fan-out no longer performs socket I/O under its subscriber mutex, and standalone Assistant CI is immutable. Python packages now require the single supported/validated interpreter, Python 3.14+, while the Assistant's Node prerequisite matches its validated Node 22+ floor.


### Snapshot 0.9.18 — semantic context, UI and experience learning

The promoted ecosystem pairs **KITT Memory 0.3.0**, **Protocol 0.3.0**, **Assistant 0.1.7 / runtime 0.2.19**, **Agent CLI 0.75.1**, **AI Workers 0.1.25**, **Toolbox 0.2.9** and **Reverse Proxy 4.4.1**.

This snapshot adds a hierarchical shared-memory context layer with progressive summaries, provenance, durable ChangeSets, recall traces and extensible memory schemas without changing the local-authority contract. The Agent adds structured long-session WorkingState, rehydratable externalized tool outputs, a declarative Surface runtime projected through TUI/Web renderers, and a host-owned Backend IR with validation, impact planning and deterministic Python/TypeScript/Rust contract generation. AI Workers adds evidence-backed experience generalization and long-horizon memory evaluation; the Assistant exposes capability-aware Surface rendering and a narrow semantic-action path rather than a generic browser-to-runtime execution endpoint.

The design is a clean-room KITT implementation: specialized stores keep their own authority, semantic contracts remain declarative, repository mutation stays behind SafeRuntime policy/approval boundaries, and the new memory/experience features do not make vector search or a centralized context service mandatory.


Snapshot 0.9.18 uses the final validation SHAs for Agent/Workers: Agent `c24487c9727e10706f1d51fe933578207a2c6db1` and AI Workers `ee6b749f91874815a179e8e7ff583d7fcbb3e879`. Runtime versions remain Agent 0.75.1 and AI Workers 0.1.25.


### Automatic prerequisite bootstrap

Non-interactive installs now bootstrap a missing/incompatible Rust toolchain automatically when native K.I.T.T. modules require it. The installer downloads the official platform-specific `rustup-init` binary over HTTPS, installs the stable minimal toolchain in the current user's Cargo home, prepends that Cargo bin directory for the active install process, revalidates the required Rust version, and then continues.

This behavior is enabled by `KITT_NON_INTERACTIVE=1` / `--yes`. To require prerequisites to be preinstalled instead, pass `--no-auto-prerequisites` or set `KITT_NO_AUTO_PREREQUISITES=1`.

The installer still fails closed if the platform/architecture cannot be mapped to an official rustup target or the installed stable toolchain does not satisfy the highest Rust requirement in the selected module graph.


### Linux native audio fallback

The installer no longer requires `pkg-config`/ALSA development headers just to install the complete agent stack. On Linux it probes `pkg-config --exists alsa` before the Assistant Cargo build. When the native audio toolchain is absent, it builds KITT Assistant with `--no-default-features`: resident microphone/wake-word capture is omitted, while the daemon, Control Center, HUD, memory, model routing, explicit transcription APIs and the rest of the ecosystem remain installed.

If ALSA development support is present, the normal default-feature build is used and resident voice capture remains enabled.


### Snapshot 0.9.20 — zero-prep native install fallback

The locked ecosystem now promotes Assistant **0.1.8** at `dc36ff35f66e3934f7e7bf2182e1bb0d62330b26`, Agent CLI 0.75.1 validation snapshot `aee552caf0ef4fd7bd44b12a85e15e7df1febed4`, and AI Workers 0.1.25 snapshot `21978ab2e4968861e2be1387323d9c6e9bce07f4`.

Non-interactive installation bootstraps missing Rust through official rustup. On Linux, resident Assistant microphone/wake-word capture is compiled only when the ALSA development toolchain is already available; otherwise the installer automatically selects the non-audio Assistant build. This keeps the complete coding-agent, daemon, Control Center, memory, HUD, reverse proxy and explicit transcription interfaces installable without requiring a system package-manager preparation step.


### Minimal Agent + Reverse Proxy install

For a coding-agent installation without Assistant, Memory daemon, AI Workers or native Toolbox, use the explicit minimal preset:

```bash
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | sh -s -- --preset agent-proxy-minimal --minimal --yes
```

`--minimal` changes dependency resolution from `requires + companions` to strict `requires` only. With this preset the resolved KITT modules are exactly:

```text
kitt-protocol
kitt-memory
kitt-agent-cli
kitt-reverse-proxy
```

The Agent CLI requires kitt-memory and uses its standalone kitt-memoryd as the sole durable memory authority. kitt-memoryd is installed with the preset and auto-started by the Agent when first needed. The Agent CLI keeps its safe Python fallback when the optional native Toolbox is not installed. The Reverse Proxy remains an independent Node service. Assistant, shared-memory daemon, AI Workers and resident voice components are not installed.


### Component update channels

The command above uses the default `edge` channel and follows component `main` branches. Add `--channel release` to install the immutable component SHAs in `ecosystem.release.json`. Use `--ref <branch|tag|sha>` only for an edge diagnostic/bisect.

### Memory authority update

The minimal Agent/Proxy installation now includes `kitt-memory` by design. Agent CLI 0.76+ no longer owns a second memory database: `kitt-memoryd` stores semantic memories, provenance, lifecycle state and dream commits. Assistant remains optional and is not required to host memory.


### Snapshot 0.9.21 — single memory authority

The promoted ecosystem aligns **Protocol 0.4.0**, **Memory 0.4.0**, **Agent CLI 0.76.0**, **Assistant 0.1.9 / runtime 0.2.20**, **AI Workers 0.1.26**, **Toolbox 0.2.9** and **Reverse Proxy 4.4.1**.

Agent CLI now delegates durable semantic memory, provenance, lifecycle state and Dreaming commits to standalone `kitt-memoryd`. Local Agent memory/vector/concept/correction tables were removed by schema migration v7. The minimal `agent-proxy-minimal --minimal` installation includes Protocol + Memory + Agent CLI + Reverse Proxy only; Assistant, Toolbox and AI Workers remain optional.


### Snapshot 0.9.22 — evidence-first agentic reliability

The promoted ecosystem aligns **Protocol 0.4.0**, **Memory 0.4.0**, **Agent CLI 0.77.0**, **Assistant 0.1.10 / runtime 0.2.21**, **AI Workers 0.1.28**, **Toolbox 0.2.9** and **Reverse Proxy 4.5.0**.

Application-sized mutation requests now enter an evidence-first agentic loop: the complete user goal remains authoritative, but the first execution action is a bounded repository inspection before optional architecture planning or mutation. Subsequent work advances through small action/observation milestones and preserves the adaptive symbol/diff editing path for existing files.

Official streaming providers distinguish explicit output-limit truncation from successful completion and the Agent recovers by regenerating a smaller complete action instead of concatenating partial JSON, diffs or source code. WebChat uses activity-aware response liveness with a bounded absolute ceiling, while managed reverse-proxy browser startup keeps the 330-second readiness budget. The retained TUI also includes bidirectional manual transcript scrolling and continuous visible K.I.T.T. scanner animation.

### Snapshot 0.9.23 — autonomous interaction and action transparency

The promoted ecosystem aligns **Protocol 0.4.0**, **Memory 0.4.0**, **Agent CLI 0.78.0**, **Assistant 0.1.12 / runtime 0.2.22**, **AI Workers 0.1.30**, **Toolbox 0.2.9** and **Reverse Proxy 4.6.1**.

Autonomy semantics are now explicit end to end: `allow-all` remains authoritative for ordinary model-initiated commands even when a strong OS sandbox is unavailable, while dangerous argv, network elevation and control-plane mutation retain their dedicated fail-closed/approval boundaries. Permission overlays consume pointer input across the whole modal and expose clicks only on visible approval actions, eliminating modal-body fallthrough.

The agent-contract `reasoning_summary` is no longer discarded when a model response becomes a native tool call. Reverse Proxy preserves the bounded public summary, Agent CLI carries it through the tool bridge, and the TUI renders it as the primary description of what the model is doing and why, with the concrete tool/command retained as technical detail. This is user-visible progress metadata, not chain-of-thought.

The immutable lock uses Agent `4e3eb53437cccfcd7254a338b8051e54e41ae1be`, Reverse Proxy `f5dd7787554d2c599df8277830124db6e7ffeb41`, Assistant `58ebdbaf6bc2c9135d645cd782d639e226e24d03` and AI Workers `9d073716163491a0716e44c341a6d6674bbba931`.



### Snapshot 0.9.25 — governed Figma integration

The promoted ecosystem aligns **Protocol 0.4.0**, **Memory 0.4.0**, **Agent CLI 0.78.1**, **Assistant 0.1.12 / runtime 0.2.22**, **AI Workers 0.1.31**, **Toolbox 0.2.9** and **Reverse Proxy 4.6.1**.

Agent CLI 0.78.1 adds the opt-in `kitt-figma` integration through the official Figma MCP boundary. The plugin registers only plugin-owned runtime MCP adapters, preserves user-owned MCP configuration, and keeps Figma operations inside the normal KITT ToolRegistry/policy/approval path. AI Workers 0.1.31 updates Evolution/Evals immutable Agent provenance to the same promoted Agent revision.

The immutable lock pins Agent `fbc64cdd90d476773f1af081f864572a4cc72b7b` and AI Workers `c01d1ff13f202f39b6a109d95bac914ede4b8688`; all other component revisions remain unchanged from the preceding validated snapshot.


### Installer cleanup

The distribution CLI has one installation pipeline: `SourceFreeEcosystemInstaller`. `EcosystemInstaller` now contains only shared prerequisites, rollback, state, smoke-test and launcher utilities; the obsolete source-retaining build/install implementation was removed.


### Snapshot 0.9.26 — authority and dead-code hardening

The promoted ecosystem aligns **Protocol 0.4.0**, **Memory 0.5.0**, **Agent CLI 0.78.3**, **Assistant 0.1.13 / runtime 0.2.23**, **AI Workers 0.1.33**, **Toolbox 0.2.9** and **Reverse Proxy 4.6.2**.

This snapshot removes redundant Agent-local memory authority, unused Python/TypeScript/Rust symbols and obsolete installer paths while preserving explicit compatibility exports that are part of the public surface. Agent state now creates only the current history schema and rejects obsolete local revisions instead of retaining migration code for removed authorities. KITT Memory remains the sole durable semantic-memory authority; Assistant consumes Memory 0.5.0 without recreating Agent memory ownership.

CI is stricter across the composition: Agent and Workers reject critical unused Python symbols, Reverse Proxy TypeScript rejects unused locals/parameters, Rust components keep clippy warnings as errors, and Protocol continues cross-SDK parity checks. The root promotion workflow now resolves `push` builds from the immutable `ecosystem.lock.json` instead of skipping the resolver, so a main-branch promotion validates the exact revisions it can release.

The immutable lock pins Agent `89a63da16368a59eac5eee185373bfbf89f516b1`, Memory `defa05c7712c726a4accc3626757b270d190387b`, AI Workers `f0d9a28601b202a4f516622245406f4e042b18d5`, Assistant `b4237627c57980c8c9cd0c4656ccd021b09a9765` and Reverse Proxy `7fd858bbf5c4fda8dd1cdbb290a3ce29fc857d72`.


### Snapshot 0.9.27 — staged prompt execution

The promoted ecosystem aligns **Protocol 0.4.0**, **Memory 0.5.0**, **Agent CLI 0.78.7**, **Assistant 0.1.14 / runtime 0.2.24**, **AI Workers 0.1.34**, **Toolbox 0.2.9** and **Reverse Proxy 4.6.5**.

This snapshot fixes the browser-backed superprompt regression. Agent CLI carries its deterministic discovery phase as structured turn data and deduplicates equivalent semantic/raw task text. Reverse Proxy sends the complete tool/workspace bootstrap once per stable context fingerprint, then sends compact delta turns while the named WebChat session retains previously supplied context.

Contract repairs no longer replay the original task/workspace payload. Valid tool actions may omit nullable fields, common tool-call aliases are normalized locally, and each turn chooses one host action then waits for its observation before choosing the next action. Broad implementation work therefore follows staged discovery -> mutation -> validation instead of attempting a project-sized tool bundle in one model response.

The immutable lock pins Agent `7d56faec43fa6f5c0e4b1f63c0c18e269a0eb9d8`, Reverse Proxy `581083b839d285428f28d40f7c9c85b771bfb23b`, Assistant `2101bac97a876611b6c696c2efba7c7f68711f35` and AI Workers `12cd5489fbc0c73097eed4b0c120b6f8791f1939`.


### Snapshot 0.9.27 — compact staged WebChat execution

The promoted WebChat execution path aligns **Agent CLI 0.78.5**, **Reverse Proxy 4.6.5** and **AI Workers 0.1.35**.

The Agent no longer forwards its generated execution persona or textual Tool Contract across the reverse-proxy boundary after tools have been represented structurally. Reverse Proxy bounds retained trusted orchestration to 4 KiB and drives mutation turns through the deterministic phases `discovery -> mutation -> validation`, requesting one host action per round trip.

This prevents the earlier superprompt amplification where the same task, workspace and tool instructions could appear in the Agent prompt, contract bootstrap and repair context at once. Contract repairs remain compact and do not resend the workspace bootstrap.


### Snapshot 0.9.28 — structural reverse-proxy tool transport

The promoted stack aligns **Agent CLI 0.78.7**, **Reverse Proxy 4.6.5**, **AI Workers 0.1.37** and Assistant runtime 0.2.24.

Agent tool schemas now travel as structured execution data instead of being rediscovered from the textual Tool Contract. Prompt compaction may therefore remove duplicated tool instructions without causing `TOOLS_AVAILABLE: []`. Internal provider retries also preserve the same structural schema, preventing a retry from silently downgrading an execution turn to an empty tool surface. The exact per-turn `kitt_runtime.operation` allowlist remains enforced by the Agent host and its policy/approval boundary.


### Snapshot 0.9.29 — recoverable cancellation and model-response flow

The promoted minimal Agent/Proxy stack aligns **Protocol 0.4.0**, **Memory 0.5.0**, **Agent CLI 0.78.9**, **AI Workers 0.1.38** and **Reverse Proxy 4.6.6**.

Agent CLI 0.78.9 fixes the Ctrl+C cancellation race where an already-running local worker could keep the single-worker executor occupied and leave the next prompt queued indefinitely. Cancelled consumers are generation-scoped so stale cleanup cannot clear the replacement turn. Reverse Proxy 4.6.6 preserves browser sessions for recoverable invalid model responses and exposes Continue/Retry metadata. The root installer now follows `main`, so the documented `agent-proxy-minimal --minimal -y` command upgrades existing installations to the current Agent and Reverse Proxy revisions.


### Snapshot 0.9.30 — main-first ecosystem installation

The main-first stack aligns **Agent CLI 0.78.10**, **Assistant 0.1.15 / runtime 0.2.25**, **AI Workers 0.1.39** and **Reverse Proxy 4.6.6**, with Protocol, Memory and Toolbox also resolved from their current `main` branches.

The root installer no longer persists a cross-repository `ecosystem.lock.json`. Every selected K.I.T.T. module resolves from `main` by default, while the exact fetched SHAs are recorded only as installation provenance. `--ref <branch|tag|sha>` remains available as an explicit override. CI resolves moving refs once per run for consistency without turning them into a long-lived ecosystem lock.
