# K.I.T.T. Ecosystem

> Modular, resilient, local-first AI companion, personal assistant, and developer ecosystem.

This meta-repository coordinates architecture, configuration standards, cross-product contracts, and release integration for the K.I.T.T. ecosystem.

---

## 🏛️ Ecosystem Overview & Component Matrix

```text
Browser / Web UI
   │
   │  HTTP (127.0.0.1:41828)
   ▼
kittd Control Center (Rust / std web server)
   │
   ├── Schema & Dynamic Catalog (settings.*)
   ├── Revisioned Atomic Overlay (~/.config/kitt/control-center/overrides.json)
   ├── Validation Engine & Diff Redaction
   └── Health & Component Status
         │
         ├──► kitt-assistant    (Daemon 127.0.0.1:41827, Voice, Routing, HUD)
         ├──► kitt-agent-cli    (Autonomous Pair Programmer, Context, Tools)
         ├──► kitt-memory       (Shared SQLite WAL Store, Monotonic Sensitivity)
         ├──► kitt-reverse-proxy(OpenAI Bridge 127.0.0.1:3000, UI/Network Transports)
         ├──► kitt-ai-workers   (On-demand NDJSON ML/Vision Worker Foundation)
         └──► kitt-toolbox      (Low-overhead System Snapshots & Probes)
```

| Repository | Responsibility | Stack | Default Port / Interface |
|---|---|---|---|
| **[`kitt-assistant`](https://github.com/rfdetoni/kitt-assistant)** | 24/7 Personal Assistant Daemon, Hands-free Voice, Fast/Heavy Routing, Control Center Web & HUD | Rust + Tauri | `127.0.0.1:41827` (IPC)<br>`127.0.0.1:41828` (Control Center) |
| **[`kitt-agent-cli`](https://github.com/rfdetoni/kitt-agent-cli)** | Autonomous coding agent & terminal pair programmer with Dreaming memory | Python 3.12+ | CLI / TUI / Protocol-v1 Client |
| **[`kitt-memory`](https://github.com/rfdetoni/kitt-memory)** | High-performance shared SQLite WAL persistent memory store | Rust | Library / `kittd` embedded backend |
| **[`kitt-reverse-proxy`](https://github.com/rfdetoni/kitt-reverse-proxy)** | Web chat to OpenAI-compatible API bridge (UI & Network transports) | TypeScript / Node.js | `127.0.0.1:3000` (HTTP) |
| **[`kitt-protocol`](https://github.com/rfdetoni/kitt-protocol)** | Canonical contracts, schemas, and SDKs (Rust, Python, TS) | Rust / Python / TS | Protocol-v1 framing |
| **[`kitt-toolbox`](https://github.com/rfdetoni/kitt-toolbox)** | Low-overhead system resource inspection & probe snapshots | Rust | CLI (`kitt-toolbox snapshot`) |
| **[`kitt-ai-workers`](https://github.com/rfdetoni/kitt-ai-workers)** | On-demand ML & vision execution workers | Python 3.12+ | Stdio NDJSON protocol |

---

## ⚙️ Configuration Hierarchy & Overlay Architecture

The ecosystem uses a unified, atomic configuration overlay managed via **KITT Control Center**:

- **Linux**: `${XDG_CONFIG_HOME:-~/.config}/kitt/control-center/overrides.json`
- **macOS**: `~/Library/Application Support/kitt/control-center/overrides.json`
- **Windows**: `%APPDATA%\kitt\control-center\overrides.json`

### Precedence Rule:
```text
defaults < native config files < Control Center overlay < env variables < CLI flags
```

- Control Center GUI is an on-demand SPA served by `kittd` in loopback (`http://127.0.0.1:41828`), with strict CSRF protection, same-origin checks, and CSP.
- Secret credentials are never stored in plain text in the overlay; they reference environment variable identifiers (e.g. `api_key_env: "OPENAI_API_KEY"`).

---

## 🚀 Step-by-Step: Setting Up and Running the Ecosystem

### Prerequisites

- **Rust**: 1.80+ (`rustup default stable`)
- **Python**: 3.12+ with `venv`
- **Node.js**: 20+ and `npm`
- **LLM Provider (Local)**: [Ollama](https://ollama.ai/) with models (e.g., `ollama pull qwen3:4b`, `ollama pull qwen2.5-coder:7b`)
- **System TTS (Linux optional)**: `espeak-ng` or `speech-dispatcher` for voice synthesis

### Quick Automated Installation (Linux, macOS, Windows)

You can install and configure all modules automatically using the provided installer scripts:

#### Linux & macOS:
```bash
# Clone the root repository
git clone https://github.com/rfdetoni/kitt.git
cd kitt

# Run universal installer (auto-detects Linux vs macOS)
./install.sh
```

#### Windows (PowerShell):
```powershell
# In PowerShell (Run as Administrator if needed):
git clone https://github.com/rfdetoni/kitt.git
cd kitt
powershell -ExecutionPolicy Bypass -File scripts/install-windows.ps1
```

---

### Step 1: Clone or Enter the Ecosystem Directory

```bash
git clone https://github.com/rfdetoni/kitt.git
cd kitt
# Ensure all sub-repositories are cloned into the workspace
```

---

### Step 2: Build and Start `kitt-assistant` & KITT Control Center

`kittd` is the central 24/7 daemon. It serves both the authenticated IPC interface on port `41827` and the Control Center Web GUI on port `41828`.

```bash
cd kitt-assistant

# Build workspace binaries
cargo build --release --workspace

# Build the ephemeral HUD overlay (optional desktop UI)
cd apps/kitt-hud
npm install
npm run build
cd ../..

# Start the daemon
./target/release/kittd
```

> **Access Control Center**: Open your browser at **`http://127.0.0.1:41828/`** to view system health, adjust model routing, voice parameters, agent limits, and proxy configuration with live diffs.

---

### Step 3: Test Assistant IPC with `kittctl`

In another terminal, interact with the running daemon:

```bash
cd kitt-assistant

# Ping daemon
./target/release/kittctl ping

# Ask a question (routed to fast or heavy model)
./target/release/kittctl ask "Olá KITT, qual é o status do sistema?"

# Save an explicit memory
./target/release/kittctl remember "Stack principal do projeto é Rust e Python"
```

---

### Step 4: Setup and Run `kitt-agent-cli`

`kitt-agent-cli` is the autonomous terminal pair programmer. It automatically connects to the shared `kittd` memory when available and falls back gracefully to standalone mode.

```bash
cd ../kitt-agent-cli

# Setup Python virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Launch interactive coding agent
kitt

# Or run with CLI commands
kitt --help
```

---

### Step 5: (Optional) Setup and Run `kitt-reverse-proxy`

The reverse proxy exposes web AI sessions as a standard OpenAI-compatible API (`http://127.0.0.1:3000/v1/chat/completions`):

```bash
cd ../kitt-reverse-proxy

npm install
npm run build

# Start proxy with UI transport for ChatGPT, Claude, Gemini, etc.
npm start -- --provider auto --port 3000
```

---

### Step 6: (Optional) Run `kitt-toolbox` System Snapshot

```bash
cd ../kitt-toolbox
cargo run --release -- snapshot
```

---

## 🧪 Validating the Entire Ecosystem

Run the test suites across all 8 repositories:

```bash
# Protocol
( cd kitt-protocol && cargo fmt -- --check && cargo test && npm test )

# Memory
( cd kitt-memory && cargo clippy --all-targets -- -D warnings && cargo test )

# Assistant & Control Center
( cd kitt-assistant && cargo clippy --workspace --all-targets -- -D warnings && cargo test --workspace )

# Agent CLI
( cd kitt-agent-cli && pytest )

# AI Workers
( cd kitt-ai-workers && pytest )

# Toolbox
( cd kitt-toolbox && cargo test )

# Reverse Proxy
( cd kitt-reverse-proxy && npm test && npm run build )
```

---

## 🔒 Security Principles

1. **Strict Loopback Binding**: `127.0.0.1` and `[::1]` only. Remote bind attempts fail-closed.
2. **Monotonic Sensitivity**: Memory records cannot be downgraded in sensitivity on upsert or import.
3. **No Secret Egress**: API keys and private/secret memory items are never transmitted to external providers.
4. **Owner-Only Filesystem Permissions**: Tokens, cache, and TTS files are created with `0600` / `0700` POSIX permissions.
5. **No Stealth / CAPTCHA Bypass**: When automated web endpoints require human challenge resolution, the system demands explicit user intervention in visible Chromium.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
