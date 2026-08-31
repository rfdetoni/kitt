#!/usr/bin/env bash
# ==============================================================================
# K.I.T.T. Ecosystem Installer for macOS
# ==============================================================================
set -euo pipefail

BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_err() { echo -e "${RED}[ERROR]${NC} $1"; }

echo -e "${BOLD}${GREEN}"
echo "  _  __ _____ _______ _______ "
echo " | |/ /|_   _|__   __|__   __|"
echo " | ' /   | |    | |     | |   "
echo " |  <    | |    | |     | |   "
echo " | . \  _| |_   | |     | |   "
echo " |_|\_\|_____|  |_|     |_|   "
echo "  Ecosystem Installer (macOS) "
echo -e "${NC}"

# 1. Determine Ecosystem Root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -d "$SCRIPT_DIR/../../kitt-assistant" ]; then
    ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
elif [ -d "$SCRIPT_DIR/../kitt-assistant" ]; then
    ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
elif [ -d "$PWD/kitt-assistant" ]; then
    ROOT_DIR="$PWD"
else
    ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

log_info "KITT workspace root detected at: ${BOLD}$ROOT_DIR${NC}"

# 2. Check Prerequisites
log_info "Verifying prerequisites..."

check_cmd() {
    if ! command -v "$1" &>/dev/null; then
        log_err "Missing required command: $1. Please install it (e.g. via brew install $1) before proceeding."
        return 1
    fi
}

check_cmd git
check_cmd cargo
check_cmd rustc
check_cmd python3
check_cmd node
check_cmd npm

# 3. Create Configuration Directories
CONFIG_ROOT="$HOME/Library/Application Support/kitt"
mkdir -p "$CONFIG_ROOT/control-center" "$CONFIG_ROOT/assistant"
chmod 700 "$CONFIG_ROOT" "$CONFIG_ROOT/control-center" "$CONFIG_ROOT/assistant" 2>/dev/null || true
log_ok "Configuration directory initialized at: $CONFIG_ROOT"

# 4. Helper to ensure repo exists
get_repo() {
    local name="$1"
    local dir="$ROOT_DIR/$name"
    if [ ! -d "$dir" ]; then
        log_info "Cloning $name from GitHub..."
        git clone "https://github.com/rfdetoni/$name.git" "$dir"
    fi
}

# 5. Build kitt-protocol
if [ -d "$ROOT_DIR/kitt-protocol" ]; then
    log_info "Building kitt-protocol..."
    ( cd "$ROOT_DIR/kitt-protocol" && cargo build --release )
    log_ok "kitt-protocol ready."
fi

# 6. Build kitt-memory
if [ -d "$ROOT_DIR/kitt-memory" ]; then
    log_info "Building kitt-memory..."
    ( cd "$ROOT_DIR/kitt-memory" && cargo build --release )
    log_ok "kitt-memory ready."
fi

# 7. Build kitt-assistant (kittd, kittctl, Control Center Web)
get_repo "kitt-assistant"
log_info "Building kitt-assistant (daemon kittd + CLI kittctl)..."
(
    cd "$ROOT_DIR/kitt-assistant"
    cargo build --release --workspace
    if [ -d "apps/kitt-hud" ]; then
        log_info "Building ephemeral HUD frontend..."
        cd apps/kitt-hud
        npm install --silent
        npm run build --silent
    fi
)
log_ok "kitt-assistant and KITT Control Center built successfully."

# 8. Setup kitt-agent-cli
get_repo "kitt-agent-cli"
log_info "Setting up kitt-agent-cli (Python virtualenv)..."
(
    cd "$ROOT_DIR/kitt-agent-cli"
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi
    source .venv/bin/activate
    pip install --upgrade pip --quiet
    pip install -e . --quiet
)
log_ok "kitt-agent-cli ready in $ROOT_DIR/kitt-agent-cli/.venv."

# 9. Setup kitt-reverse-proxy
if [ -d "$ROOT_DIR/kitt-reverse-proxy" ]; then
    log_info "Building kitt-reverse-proxy..."
    (
        cd "$ROOT_DIR/kitt-reverse-proxy"
        npm install --silent
        npm run build --silent
    )
    log_ok "kitt-reverse-proxy ready."
fi

# 10. Build kitt-toolbox
if [ -d "$ROOT_DIR/kitt-toolbox" ]; then
    log_info "Building kitt-toolbox..."
    ( cd "$ROOT_DIR/kitt-toolbox" && cargo build --release )
    log_ok "kitt-toolbox ready."
# 11. Install and Start Background Service Natively
log_info "Installing and starting K.I.T.T. native background service..."
"$ROOT_DIR/kitt-assistant/target/release/kittctl" service install
"$ROOT_DIR/kitt-assistant/target/release/kittctl" service start || true
log_ok "K.I.T.T. background service is active."

echo ""
echo -e "${BOLD}${GREEN}================================================================${NC}"
echo -e "${BOLD}${GREEN}        K.I.T.T. Ecosystem Installed & Running!                ${NC}"
echo -e "${BOLD}${GREEN}================================================================${NC}"
echo ""
echo -e "${BOLD}The K.I.T.T. daemon is now running natively in the background.${NC}"
echo ""
echo -e " 1. ${BOLD}Open KITT Control Center Web Dashboard:${NC}"
echo -e "    ${BLUE}http://127.0.0.1:41828/${NC}"
echo ""
echo -e " 2. ${BOLD}Manage Background Service:${NC}"
echo -e "    $ROOT_DIR/kitt-assistant/target/release/kittctl service status"
echo -e "    $ROOT_DIR/kitt-assistant/target/release/kittctl service restart"
echo -e "    $ROOT_DIR/kitt-assistant/target/release/kittctl service stop"
echo ""
echo -e " 3. ${BOLD}Run Agent CLI:${NC}"
echo -e "    source $ROOT_DIR/kitt-agent-cli/.venv/bin/activate"
echo -e "    kitt"
echo ""
echo -e " 4. ${BOLD}Query Assistant directly via CLI/hotkey:${NC}"
echo -e "    $ROOT_DIR/kitt-assistant/target/release/kittctl ask \"Olá KITT\""
echo ""
