# Manual do Ecossistema K.I.T.T. — Guia Geral de Orquestração

> Guia definitivo de arquitetura, instalação integrada, configuração centralizada e operação nos sistemas operacionais **Linux**, **macOS** e **Windows**.

---

## 1. Visão Geral e Arquitetura do Ecossistema

O ecossistema **K.I.T.T.** (*Knight Industries Two Thousand / Knowledge & Intelligence Task Toolkit*) é uma plataforma modular, local-first, resiliente e segura para assistência pessoal, engenharia de software autônoma e orquestração de Inteligência Artificial.

### Diagrama de Comunicação e Topologia

```text
                                  +---------------------------------------+
                                  |    Navegador Web / HUD / Cliente      |
                                  +-------------------+-------------------+
                                                      |
                                                      | HTTP / WebSocket (127.0.0.1:41828)
                                                      v
+---------------------------------------------------------------------------------------------------------+
|                                    kittd (Daemon do K.I.T.T. Assistant)                                 |
|  - Servidor Web & Control Center                                                                        |
|  - Roteamento Inteligente (Fast vs Heavy LLM)                                                           |
|  - Motor de Áudio / Wake Word / VAD / TTS                                                               |
+------------------+------------------------------+-------------------------------------+-----------------+
                   |                              |                                     |
    Unix Socket /  |               IPC / Library  |                      Protocol V1 /  |
    Named Pipe     |               Memory Store   |                      Shared DB      |
                   v                              v                                     v
+-----------------------------+  +-------------------------------+  +-------------------------------------+
|      kitt-ai-workers        |  |          kitt-memory          |  |           kitt-agent-cli            |
| - STT Whisper Local         |  | - SQLite WAL Store            |  | - Pair Programmer Autônomo TUI     |
| - APIs de Visão e Embeddings|  | - Sensibilidade Monotônica    |  | - Engine de Contexto (Aider-style)  |
| - Framing NDJSON Seguro     |  | - Migração Schema Canônico V1 |  | - Ferramentas com Políticas de Auth |
+-----------------------------+  +-------------------------------+  +-------------------------------------+
                   |                                                                    |
                   | HTTP Ingress (127.0.0.1:3000)                                      | Probe / Snapshots
                   v                                                                    v
+-----------------------------------------+                        +--------------------------------------+
|           kitt-reverse-proxy            |                        |             kitt-toolbox             |
| - Bridge Web Chat -> OpenAI API         |                        | - Coleta de Métricas de CPU/RAM/Disco|
| - Proteção Anti-CSRF / Origens Locais   |                        | - Inspeção de Processos e Git State  |
| - Filas Serializadas com Failover       |                        +--------------------------------------+
+-----------------------------------------+
```

### Matriz dos 8 Módulos do Ecossistema

| Repositório | Descrição / Responsabilidade | Tecnologias | Interfaces Padrão |
|---|---|---|---|
| **`kitt`** | Meta-repositório, orquestração, CI/CD e governança | Bash, Python, YAML | N/A |
| **`kitt-protocol`** | Contratos canônicos, Envelopes Protocol-V1 e SDKs | Rust, Python, TypeScript | Tipos & Serialização |
| **`kitt-memory`** | Memória persistente compartilhada de alta performance | Rust, SQLite (WAL) | Biblioteca / CLI Migração |
| **`kitt-toolbox`** | Inspeção de recursos do sistema e execução de ferramentas | Rust | CLI (`kitt-toolbox snapshot`) |
| **`kitt-ai-workers`** | Serviços de IA locais (Speech-to-Text Whisper, etc.) | Python 3.12+ | HTTP (127.0.0.1:8000) / NDJSON |
| **`kitt-assistant`** | Daemon central 24/7, voz, roteador e interface HUD | Rust, Tauri, Vue/Vite | `127.0.0.1:41827` / `41828` |
| **`kitt-agent-cli`** | Agente de codificação autônomo e Pair Programmer de terminal | Python 3.12+ (3.14 OK) | TUI Terminal / Daemon CLI |
| **`kitt-reverse-proxy`**| Proxy de IA web para compatibilidade com API OpenAI | TypeScript, Node.js 20+ | `http://127.0.0.1:3000` |

---

## 2. Requisitos de Sistema e Pré-requisitos Globais

### Dependências Comuns:
- **Rust Toolchain**: 1.80+ (com `cargo`, `rustc`, `rustfmt`, `clippy`)
- **Python**: 3.12, 3.13 ou 3.14 (com `venv`, `pip`, `setuptools`)
- **Node.js**: LTS 20.x ou 22.x (com `npm`)
- **Git**: 2.40+
- **Provedor de LLM Local**: [Ollama](https://ollama.com/) instalado com modelos sugeridos:
  - `ollama pull qwen2.5-coder:1.5b` (para contexto rápido)
  - `ollama pull qwen2.5-coder:7b` ou `14b` (para execução e código)

---

## 3. Guia de Instalação Passo a Passo por Sistema Operacional

### 🐧 A. Instalação no LINUX (Ubuntu/Debian/Fedora/Arch)

#### 1. Instalar Ferramentas de Sistema e Compilação
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y \
  build-essential \
  curl \
  git \
  pkg-config \
  libasound2-dev \
  libssl-dev \
  sqlite3 \
  libsqlite3-dev \
  python3-dev \
  python3-venv \
  python3-pip

# Fedora
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y alsa-lib-devel openssl-devel sqlite-devel python3-devel

# Arch Linux
sudo pacman -S --needed base-devel alsa-lib openssl sqlite python
```

#### 2. Instalar Rust, Node.js e Ollama
```bash
# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"

# Node.js (via NodeSource no Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5-coder:1.5b
```

#### 3. Clonar e Compilar o Ecossistema
```bash
git clone https://github.com/rfdetoni/kitt.git ~/kitt-ecosystem
cd ~/kitt-ecosystem

# Se os sub-repositórios estiverem em diretórios irmãos:
# ./install.sh
```

---

### 🍏 B. Instalação no macOS (Apple Silicon M1/M2/M3 & Intel)

#### 1. Instalar Homebrew e Dependências
```bash
# Homebrew (se não instalado)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Dependências
brew install git python node@22 sqlite pkg-config
brew link node@22
```

#### 2. Instalar Rust e Ollama
```bash
# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"

# Ollama macOS
brew install --cask ollama
# Iniciar o Ollama e baixar modelos
ollama pull qwen2.5-coder:1.5b
```

#### 3. Instalação Integrada
```bash
git clone https://github.com/rfdetoni/kitt.git ~/kitt-ecosystem
cd ~/kitt-ecosystem
./install.sh
```

---

### 🪟 C. Instalação no WINDOWS (Windows 10/11 x64)

#### 1. Instalar Gerenciador de Pacotes e Ferramentas Base
Abra o **PowerShell como Administrador**:
```powershell
# Instalar ferramentas via winget
winget install Git.Git
winget install Rustlang.Rustup
winget install Python.Python.3.12
winget install OpenJS.NodeJS.LTS
winget install Ollama.Ollama
winget install Microsoft.VisualStudio.2022.BuildTools --override "--passive --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
```

#### 2. Configurar Rust no Windows
```powershell
# Inicializar toolchain MSVC
rustup default stable-x86_64-pc-windows-msvc
```

#### 3. Executar Script de Instalação Windows
```powershell
git clone https://github.com/rfdetoni/kitt.git C:\kitt-ecosystem
cd C:\kitt-ecosystem
powershell -ExecutionPolicy Bypass -File scripts/install-windows.ps1
```

---

## 4. Configuração Centralizada e Hierarquia de Overlays

O K.I.T.T. utiliza um sistema unificado de sobreposição de configurações gerido pelo **Control Center**:

### Localização dos Arquivos de Configuração por OS:
- **Linux**: `~/.config/kitt/control-center/overrides.json`
- **macOS**: `~/Library/Application Support/kitt/control-center/overrides.json`
- **Windows**: `%APPDATA%\kitt\control-center\overrides.json`

### Exemplo de Configuração `overrides.json`:
```json
{
  "version": 1,
  "profiles": {
    "default": {
      "llm_base_url": "http://127.0.0.1:11434",
      "model_fast": "qwen2.5-coder:1.5b",
      "model_heavy": "qwen2.5-coder:7b",
      "voice_enabled": false,
      "memory_sync": true
    }
  }
}
```

### Regra de Precedência:
```text
Configurações Padrão < Arquivos Locais do Projeto < Control Center Overlay < Variáveis de Ambiente < Argumentos de CLI
```

---

## 5. Guia de Operação e Uso Integrado

### Inicializando a Suíte Completa:

```bash
# 1. Iniciar o Ollama (se não estiver rodando como serviço)
ollama serve &

# 2. Iniciar o Daemon Central do Assistente
cd kitt-assistant && cargo run --release --bin kittd &

# 3. Iniciar o Proxy de IA (Opcional para integrações Web/OpenAI)
cd kitt-reverse-proxy && npm start &

# 4. Iniciar o Servidor de Áudio e Visão Local (Opcional)
cd kitt-ai-workers && python3 -m kitt_workers.stt_server &

# 5. Executar o Agente de Código no Terminal
cd kitt-agent-cli && ./bin/kitt
```

### Acessando o Control Center Web:
Abra seu navegador em: `http://127.0.0.1:41828`

---

## 6. Diagnóstico e Resolução de Problemas (Troubleshooting)

### 1. `PermissionError (13)` em arquivos de Lock no Windows:
- **Causa**: Concorrência de escrita no arquivo `auth.json`.
- **Solução**: O R5 inclui lock in-process via `_credential_thread_lock_for`. Certifique-se de estar utilizando a versão atualizada da branch `main`.

### 2. Erro de compilação ALSA no Linux (`libasound2` missing):
- **Solução**: Execute `sudo apt-get install -y libasound2-dev pkg-config`.

### 3. Falha de conexão com o Ollama (`Connection Refused`):
- **Verificação**: `curl http://127.0.0.1:11434/api/tags`
- **Solução**: Inicie o daemon do Ollama com `ollama serve`.

---

## 7. Validação da Suíte de Testes (Ecosystem CI)

```bash
# Executar validação automatizada de todos os repositórios:
python3 scripts/validate_workspace.py --root .
```
