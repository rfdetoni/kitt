# K.I.T.T. Ecosystem

<p align="center">
  <strong>Local-first agent ecosystem for coding, automation, memory and resident AI.</strong><br>
  Agent CLI · native acceleration · persistent memory · assistant daemon · AI workers · authorized web gateway
</p>

<p align="center">
  <a href="https://github.com/rfdetoni/kitt/blob/main/LICENSE"><img alt="License MIT" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
  <img alt="Platforms" src="https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white">
  <img alt="Rust" src="https://img.shields.io/badge/Rust-native-000000?logo=rust&logoColor=white">
</p>

K.I.T.T. is a modular, local-first AI ecosystem centered on a high-performance autonomous coding agent. Flexible orchestration stays in Python and TypeScript; deterministic CPU/data-plane work can run in Rust; heavy AI/ML workloads are isolated into on-demand workers; browser-backed provider access remains inside a dedicated gateway.

This repository is the **distribution and composition point** for the ecosystem. It resolves compatible component revisions, installs the selected stack and validates that separately owned packages compose as one K.I.T.T. installation.

---

## What’s included

| Component | Responsibility | Primary technology |
| --- | --- | --- |
| [`kitt-agent-cli`](https://github.com/rfdetoni/kitt-agent-cli) | autonomous coding-agent control plane | Python + SQLite/FTS5 |
| [`kitt-reverse-proxy`](https://github.com/rfdetoni/kitt-reverse-proxy) | authorized web-chat/API gateway | TypeScript/Node.js + Playwright |
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
- **Run the browser/API gateway:** `kitt-reverse-proxy start chatgpt`
- **Agent container:** https://github.com/rfdetoni/kitt-agent-cli/pkgs/container/kitt-agent-cli
- **Reverse-proxy container:** https://github.com/rfdetoni/kitt-reverse-proxy/pkgs/container/kitt-reverse-proxy
- **Browser container:** https://github.com/rfdetoni/kitt-reverse-proxy/pkgs/container/kitt-reverse-proxy-browser
- **Inspect the resident service:** `kittctl service status`
- **Evolution runs:** `kitt evolve runs`
- **Security:** [SECURITY.md](SECURITY.md)
- **Pinned ecosystem revisions:** [`ecosystem.lock.json`](ecosystem.lock.json)

---

## Requirements & compatibility

Requirements are calculated from the selected module set rather than globally hard-coded. A normal complete Agent installation currently uses:

- Git;
- Python **3.12+**;
- Node.js **20+** and npm;
- Rust **1.85+** and Cargo.

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

The installer presents K.I.T.T. modules interactively. Explicit selections are marked `[x]`; transitively required technologies are marked `[+]`.

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

Heavy STT/ML dependencies remain opt-in because they are hardware- and workload-specific. Enable them with `--with-ai-workers`.

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

Package pages:

- https://github.com/rfdetoni/kitt-agent-cli/pkgs/container/kitt-agent-cli
- https://github.com/rfdetoni/kitt-reverse-proxy/pkgs/container/kitt-reverse-proxy
- https://github.com/rfdetoni/kitt-reverse-proxy/pkgs/container/kitt-reverse-proxy-browser
- https://github.com/rfdetoni/kitt-reverse-proxy/pkgs/container/kitt-reverse-proxy-standalone

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
KITT_AGENT_VERSION=v0.4.0
KITT_REVERSE_PROXY_VERSION=v3.1.0
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
--preset agent|assistant|web|full
--modules <id[,id...]>
--with-ai-workers
--force
--no-start-services
--portable
--ref <branch|tag|sha>
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
                  provider gateway
```

The ownership rule is intentional: components communicate through versioned contracts and separately packaged capabilities instead of duplicating implementation code.

---

## Installer & release integrity

`ecosystem.json` is the module catalog. `ecosystem.lock.json` pins every repository to an immutable commit SHA.

The installer is idempotent and source-locked by default. It refuses to overwrite local component changes unless `--force` is supplied. Python packages are composed from the locally checked-out locked revisions with `--no-deps` where appropriate so VCS dependency declarations cannot silently replace one component with another revision.

After installation, `<KITT_HOME>/installed-state.json` records requested modules, automatically resolved dependencies, exact repository SHAs, platform and launchers.

Re-running the installer updates to the reviewed snapshot recorded in the lockfile unless `--ref` is explicitly used for development/testing.

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
python scripts/validate_ecosystem_lock.py
python -m installer --modules agent-cli --dry-run --portable
```

The broader integration workflow validates Rust workspaces, the PyO3 wheel, Python namespace composition, Agent CLI, Assistant, Protocol, Memory, AI Workers and Reverse Proxy at frozen revisions.

Each component repository also owns its technology-specific unit tests and lint/build checks.

---

## Contributing

Changes should keep repository ownership boundaries clear, preserve local-first security defaults and avoid adding dependencies to the hot path without a measurable benefit. Cross-repository changes should update contracts and the ecosystem lock together when required.

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