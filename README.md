# K.I.T.T. Ecosystem

K.I.T.T. is a local-first agent ecosystem centered on a high-performance Agent CLI, shared native/data-plane services, a resident assistant and an authorized browser bridge.

## Core architecture

| Component | Role | Primary technology |
| --- | --- | --- |
| `kitt-agent-cli` | autonomous coding-agent control plane | Python + SQLite/FTS5 |
| `kitt-reverse-proxy` | web-chat/API gateway and reasoning/session bridge | TypeScript/Node.js + Playwright |
| `kitt-assistant` | local daemon/control center and resident runtime | Rust + web frontend + Python runtime |
| `kitt-protocol` | cross-component contracts/SDKs | Rust + Python/TypeScript SDKs |
| `kitt-memory` | shared local memory service | Rust |
| `kitt-toolbox` | shared native code-intelligence/system data plane and Python accelerator | Rust + PyO3 |
| `kitt-ai-workers` | Evolution/Evals plus optional heavy STT/ML workers | Python |

Flexible orchestration remains in Python/TypeScript while deterministic CPU/data-plane work can run in Rust. Independently packaged Python capabilities compose through the shared `kitt.*` namespace instead of vendoring code between repositories.

## Ecosystem installer

`rfdetoni/kitt` is the single distribution/orchestration point for the ecosystem. The installer is implemented once in portable Python stdlib; `install.sh` and `install.ps1` are intentionally small bootstraps.

The module catalog lives in `ecosystem.json`, while `ecosystem.lock.json` pins every repository to an immutable commit SHA. Adding another operating system normally requires only a small platform adapter because dependency resolution and install orchestration are OS-independent.

### Interactive install

Linux / macOS / POSIX:

```bash
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/rfdetoni/kitt/main/install.ps1 | iex
```

The installer opens a terminal list of KITT modules. Explicit selections are marked `[x]`; technologies pulled transitively by the selection are marked `[+]`.

### Complete Agent guarantee

Selecting **KITT Agent CLI** always resolves the complete technology stack that the Agent integrates with:

```text
KITT Agent CLI
  + KITT Protocol
  + KITT Memory
  + KITT Toolbox
  + KITT Assistant
  + KITT AI Workers (base + Evolution/Evals)
  + KITT Reverse Proxy
```

This is enforced by the catalog resolver and CI. The Agent is never silently installed as an incomplete subset just because its technologies are owned by different repositories.

Heavy STT/ML dependencies remain opt-in because they are hardware/workload-specific rather than part of normal Agent execution. Enable them with `--with-ai-workers`.

### Non-interactive examples

Install the complete Agent stack:

```bash
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | sh -s -- --modules agent-cli --yes
```

PowerShell:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/rfdetoni/kitt/main/install.ps1))) --modules agent-cli --yes
```

Resolve without changing the machine:

```bash
python -m installer --modules agent-cli --dry-run
```

Other useful options:

```text
--preset agent|assistant|web|full
--modules <id[,id...]>
--with-ai-workers
--force
--no-start-services
--portable
--ref <branch|tag|sha>
--uninstall
```

`--portable` is an explicit degraded mode that skips Rust/native builds where a portable fallback exists. It is **not** the default: a normal complete Agent installation requires the native toolchain so all selected KITT technologies are actually installed.

## Requirements

Requirements are calculated from the resolved module set instead of being globally hard-coded. For the complete Agent stack they currently include Git, Python 3.12+, Node.js 20+/npm and Rust 1.85+/Cargo.

The installer checks all prerequisites before changing repositories. Missing dependencies produce OS-specific setup hints. Windows, Linux and macOS are first-class targets. Other POSIX systems use the generic POSIX adapter; Haiku is explicitly detected and can use that path when the selected ecosystem components and their upstream toolchains support the OS.

## Installation safety

The installer is idempotent and source-locked by default. It refuses to overwrite local component changes unless `--force` is provided. Repository revisions are frozen by `ecosystem.lock.json`; `--ref` is an explicit override for development/testing.

Python packages are composed from the locally checked-out, locked repositories with `--no-deps` where needed, so VCS dependency declarations cannot silently replace one ecosystem component with another revision. Native wheels are built from the selected `kitt-toolbox` checkout.

The install ends with smoke tests and writes `<KITT_HOME>/installed-state.json` describing requested modules, automatically resolved modules, exact repository SHAs, platform and launchers.

## After installation

```bash
kitt
kitt-reverse-proxy start chatgpt
kittctl service status
```

Self-evolution remains staged and explicit:

```bash
kitt evolve runs
kitt evolve skill <skill-name>
kitt evolve promote <run-id>
```

Evolution candidates do not replace live skills automatically; promotion remains an explicit operation after evaluation and adversarial review.

## Update

Run the same installer again. By default it installs the immutable snapshot in `ecosystem.lock.json`. Production releases should update that lockfile to reviewed SHAs rather than depending on moving branches.

## Security

Local services bind to loopback/private interfaces by default, credentials are kept out of model-visible context, tool execution uses capability and approval boundaries, and browser challenges/CAPTCHA are never bypassed. See `SECURITY.md` and component security documentation for trust-boundary details.

## Development validation

Installer invariants and dependency resolution are validated on Linux, Windows and macOS. The broader ecosystem integration workflow separately validates Rust workspaces, the PyO3 wheel, Python namespace composition, Agent CLI, Assistant, Protocol, Memory, AI Workers and Reverse Proxy at frozen revisions.

Run installer tests locally with:

```bash
python -m unittest discover -s tests -v
python scripts/validate_ecosystem_lock.py
python -m installer --modules agent-cli --dry-run --portable
```

## License

MIT. See `LICENSE`.
