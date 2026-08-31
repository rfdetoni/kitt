# K.I.T.T. Ecosystem

> Modular, resilient, and lightweight AI companion and developer ecosystem.

Meta-repository for architecture, compatibility guidelines, release coordination, and cross-product contracts. Runtime implementations are decoupled into specialized repositories.

---

## 🏛️ Ecosystem Overview

| Repository | Responsibility | Primary Stack | Scope / Boundaries |
|---|---|---|---|
| **[kitt-agent-cli](https://github.com/rfdetoni/kitt-agent-cli)** | Autonomous coding agent & terminal pair programmer | Python + Rust | Interactive CLI, Git/Code indexing, Dreaming Mode memory, autonomous tool execution |
| **[kitt-assistant](https://github.com/rfdetoni/kitt-assistant)** | 24/7 personal assistant daemon + ephemeral HUD | Rust + Tauri / TS | Loopback IPC daemon (`kittd`), CLI (`kittctl`), transparent on-demand overlay (`kitt-hud`) |
| **[kitt-reverse-proxy](https://github.com/rfdetoni/kitt-reverse-proxy)** | Web chat to AI provider bridge | TypeScript | Web UI / reverse proxy integration with local & remote AI backends |
| **[kitt-memory](https://github.com/rfdetoni/kitt-memory)** | Shared persistent memory engine | Rust | SQLite WAL storage, exact deduplication, lexical ranking, privacy egress filtering |
| **[kitt-protocol](https://github.com/rfdetoni/kitt-protocol)** | Cross-product communication contracts | JSON Schema + SDKs | Envelopes, memory DTOs, HUD event contracts, Python/TypeScript/Rust SDKs |
| **[kitt-toolbox](https://github.com/rfdetoni/kitt-toolbox)** | Shared low-level OS utilities | Rust | Lightweight system resource monitoring & probe snapshots |
| **[kitt-ai-workers](https://github.com/rfdetoni/kitt-ai-workers)** | On-demand ML & vision execution workers | Python | Dependency-free protocol foundation, out-of-process execution |

---

## 📐 Core Architecture Principles

1. **Clean Architecture & Strict Boundaries**: Domain layers remain pure with zero external I/O or GUI framework dependencies.
2. **Minimal Footprint**: Services maintain near-zero CPU and low memory when idle (~5MB RSS for `kittd`).
3. **Ephemeral UI**: Visual interfaces (HUD/WebView) spawn only on demand and automatically terminate after response TTL.
4. **Standalone Resilience**: Individual components (`kitt-agent-cli`, `kitt-assistant`) retain full standalone capability when other subsystems are absent.
5. **Strict Local Security**: Control surfaces bind exclusively to loopback addresses (`127.0.0.1`) authenticated via owner-only tokens with strict filesystem permissions (`0600`).
6. **Privacy & Data Sovereignty**: Secrets and private memories never leak to external or remote model providers.

---

## 📚 Ecosystem Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Detailed Clean Architecture dependency rules and subsystem communication.
- **[ROADMAP.md](ROADMAP.md)**: Phased evolutionary roadmap and capabilities.
- **[SECURITY.md](SECURITY.md)**: Threat model and security policies.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
