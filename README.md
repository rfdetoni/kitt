# K.I.T.T. Ecosystem

K.I.T.T. is a local-first agent ecosystem centered on a high-performance Agent CLI and an authorized browser reverse proxy.

## Core architecture

| Component | Role | Primary technology |
| --- | --- | --- |
| `kitt-agent-cli` | autonomous coding agent/control plane | Python + Rust native engine + SQLite/FTS5 |
| `kitt-reverse-proxy` | web-chat/API gateway and reasoning/session bridge | TypeScript/Node.js + Playwright |
| `kitt-assistant` | local daemon/control center | Rust + web frontend |
| `kitt-protocol` | cross-component contracts/SDKs | Rust + Python/TypeScript SDKs |
| `kitt-memory` | shared local memory service | Rust |
| `kitt-toolbox` | native utility layer | Rust |
| `kitt-ai-workers` | optional STT/ML workers | Python, optional because of heavier dependencies |

The architecture deliberately keeps flexible orchestration in Python/TypeScript and moves CPU/data-plane work to Rust rather than rewriting I/O-bound control planes for marginal gains.

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

Default installation is resource-conscious and does not install the heavy AI/STT worker extras. To install them, download the installer and pass `--with-ai-workers` (Bash) or `-WithAiWorkers` (PowerShell).

Requirements: Git, Python 3.12+, Node.js 20+ and npm. Rust/Cargo is strongly recommended; without it, the installer still provides Agent CLI's portable backend and the reverse proxy but skips native ecosystem services that require Rust.

## After installation

```bash
kitt
kitt-reverse-proxy start chatgpt
kittctl service status
```

Agent CLI uses the reverse proxy with stable conversation IDs and per-turn reasoning effort, while the proxy reuses an authenticated browser process and independent tabs rather than creating a browser process per conversation.

## Update

Run the same one-line installer again. Component repositories are refreshed to an immutable fetched ref before builds. Use `KITT_REF=<tag-or-sha>` to pin the whole source snapshot when all repositories expose that ref; production releases should prefer explicit versioned refs.

## Security

Local services bind to loopback/private interfaces by default, credentials are kept out of model-visible context, tool execution uses capability and approval boundaries, and browser challenges/CAPTCHA are never bypassed. See `SECURITY.md` and the component security documentation for reporting and trust-boundary details.

## Development validation

The ecosystem workflow freezes every requested component ref to a commit SHA and independently runs Rust, Python and reverse-proxy gates before marking the ecosystem snapshot healthy.

## License

MIT. See `LICENSE`.
