# K.I.T.T. Ecosystem

K.I.T.T. is a local-first agent ecosystem centered on a high-performance Agent CLI and an authorized browser reverse proxy.

## Core architecture

| Component | Role | Primary technology |
| --- | --- | --- |
| `kitt-agent-cli` | autonomous coding-agent control plane | Python + SQLite/FTS5 |
| `kitt-reverse-proxy` | web-chat/API gateway and reasoning/session bridge | TypeScript/Node.js + Playwright |
| `kitt-assistant` | local daemon/control center and resident runtime | Rust + web frontend |
| `kitt-protocol` | cross-component contracts/SDKs | Rust + Python/TypeScript SDKs |
| `kitt-memory` | shared local memory service | Rust |
| `kitt-toolbox` | shared native code-intelligence/system data plane and Python accelerator | Rust + PyO3 |
| `kitt-ai-workers` | lightweight Evolution/Evals packages plus optional heavy STT/ML workers | Python |

The architecture deliberately keeps flexible orchestration in Python/TypeScript and moves CPU/data-plane work to Rust rather than rewriting I/O-bound control planes for marginal gains. Python components share the `kitt.*` namespace so independently packaged capabilities can compose without duplicating compatibility layers.

The Agent CLI owns coding-agent orchestration, policy, goals, history, routing and the portable Python fallback. Native search/symbol/edit/output acceleration is owned by `kitt-toolbox` and exposed through the `kitt_native` PyO3 wheel. Offline staged skill evolution and evaluation tooling are packaged independently under `kitt-ai-workers`; they depend on the Agent contracts but are not part of its hot path.

## Install or update everything

Running the installer again performs an idempotent upgrade to the requested ref. It refuses to overwrite local component changes unless `--force`/`-Force` is explicitly supplied.

### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | bash
```

### Windows PowerShell

```powershell
irm https://raw.githubusercontent.com/rfdetoni/kitt/main/install.ps1 | iex
```

The default installation is resource-conscious. It installs the lightweight Agent CLI, shared protocol/memory/assistant/toolbox components, Evolution/Evals modules and reverse proxy. If Rust is available, the installer builds the shared `kitt_native` accelerator from `kitt-toolbox`; otherwise the Agent CLI keeps its portable Python fallback.

Heavy AI/STT worker dependencies are **not** installed by default. To add them, download the installer and pass `--with-ai-workers` (Bash) or `-WithAiWorkers` (PowerShell).

Requirements: Git, Python 3.12+, Node.js 20+ and npm. Rust/Cargo is strongly recommended; without it, the installer still provides the Agent CLI's portable backend and reverse proxy but skips native ecosystem services that require Rust.

## After installation

```bash
kitt
kitt-reverse-proxy start chatgpt
kittctl service status
```

Agent CLI uses the reverse proxy with stable conversation IDs and per-turn reasoning effort, while the proxy reuses an authenticated browser process and independent tabs rather than creating a browser process per conversation.

Self-evolution remains staged and explicit:

```bash
kitt evolve runs
kitt evolve skill <skill-name>
kitt evolve promote <run-id>
```

Evolution candidates do not replace live skills automatically; promotion remains an explicit operation after evaluation and adversarial review.

## Update

Run the same one-line installer again. Component repositories are refreshed to an immutable fetched ref before builds. Use `KITT_REF=<tag-or-sha>` to pin the whole source snapshot when all repositories expose that ref; production releases should prefer explicit versioned refs.

## Security

Local services bind to loopback/private interfaces by default, credentials are kept out of model-visible context, tool execution uses capability and approval boundaries, and browser challenges/CAPTCHA are never bypassed. See `SECURITY.md` and the component security documentation for reporting and trust-boundary details.

## Development validation

The ecosystem workflow freezes every requested component ref to a commit SHA and validates the composed snapshot rather than only testing repositories independently. Gates include Rust workspace fmt/clippy/tests, the native PyO3 wheel, Python namespace composition, extracted Evolution tests, Agent CLI on Linux/Windows, assistant/protocol/memory/reverse-proxy suites, and installer syntax.

## License

MIT. See `LICENSE`.
