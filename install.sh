#!/usr/bin/env bash
set -euo pipefail

REF="${KITT_REF:-main}"
ROOT="${KITT_HOME:-${XDG_DATA_HOME:-$HOME/.local/share}/kitt}"
BIN_DIR="${KITT_BIN_DIR:-${XDG_BIN_HOME:-$HOME/.local/bin}}"
WITH_WORKERS=0
FORCE=0
UNINSTALL=0

usage() {
  cat <<'EOF'
K.I.T.T. ecosystem installer/updater
Usage: install.sh [--ref REF] [--with-ai-workers] [--force] [--uninstall]

Installs the lightweight Agent control plane, Assistant runtime, Evolution/Evals,
and native acceleration when Rust is available. Heavy AI/STT workers are
installed only with --with-ai-workers.
EOF
}
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ref) REF="${2:?missing ref}"; shift 2 ;;
    --with-ai-workers) WITH_WORKERS=1; shift ;;
    --force) FORCE=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

if [[ $UNINSTALL -eq 1 ]]; then
  if [[ -x "$ROOT/kitt-assistant/target/release/kittctl" ]]; then
    "$ROOT/kitt-assistant/target/release/kittctl" service stop >/dev/null 2>&1 || true
  fi
  rm -rf "$ROOT"
  for name in kitt kittctl kittd kitt-reverse-proxy kitt-agent-gateway; do
    target="$BIN_DIR/$name"
    [[ -L "$target" ]] && rm -f "$target"
  done
  echo "K.I.T.T. ecosystem removed."
  exit 0
fi

for tool in git python3 node npm; do
  command -v "$tool" >/dev/null 2>&1 || { echo "$tool is required" >&2; exit 1; }
done
python3 - <<'PY'
import sys
if sys.version_info < (3, 12): raise SystemExit('Python 3.12+ is required')
PY
node -e "if(Number(process.versions.node.split('.')[0])<20)process.exit(1)" || { echo "Node.js 20+ is required" >&2; exit 1; }

mkdir -p "$ROOT" "$BIN_DIR"

sync_repo() {
  local name="$1" dir="$ROOT/$1"
  if [[ -d "$dir/.git" ]]; then
    if [[ $FORCE -ne 1 ]] && { ! git -C "$dir" diff --quiet || ! git -C "$dir" diff --cached --quiet; }; then
      echo "$name has local changes; commit/stash them or rerun with --force" >&2
      exit 1
    fi
    [[ $FORCE -eq 1 ]] && git -C "$dir" reset --hard HEAD >/dev/null
  else
    rm -rf "$dir"
    git clone --filter=blob:none --no-checkout "https://github.com/rfdetoni/$name.git" "$dir"
  fi
  git -C "$dir" remote set-url origin "https://github.com/rfdetoni/$name.git"
  git -C "$dir" fetch --force --depth 1 origin "$REF"
  git -C "$dir" checkout --detach --force FETCH_HEAD
  git -C "$dir" clean -ffd
  printf '%-22s %s\n' "$name" "$(git -C "$dir" rev-parse --short HEAD)"
}

components=(
  kitt-protocol
  kitt-memory
  kitt-assistant
  kitt-toolbox
  kitt-agent-cli
  kitt-ai-workers
  kitt-reverse-proxy
)
for component in "${components[@]}"; do sync_repo "$component"; done

build_rust() {
  local dir="$1"
  command -v cargo >/dev/null 2>&1 || return 1
  if [[ -f "$dir/Cargo.lock" ]]; then
    (cd "$dir" && cargo build --release --locked)
  else
    (cd "$dir" && cargo build --release)
  fi
}

if command -v cargo >/dev/null 2>&1; then
  for component in kitt-protocol kitt-memory kitt-toolbox; do build_rust "$ROOT/$component"; done
  build_rust "$ROOT/kitt-assistant"
else
  echo "Rust/Cargo not found: native daemon/services and Agent native acceleration will be skipped." >&2
fi

if [[ -d "$ROOT/kitt-assistant/apps/kitt-hud" ]]; then
  (cd "$ROOT/kitt-assistant/apps/kitt-hud" && npm ci --no-audit --no-fund && npm run build)
fi

AGENT_VENV="$ROOT/.venv-agent"
[[ -x "$AGENT_VENV/bin/python" ]] || python3 -m venv "$AGENT_VENV"
AGENT_PY="$AGENT_VENV/bin/python"
"$AGENT_PY" -m pip install --disable-pip-version-check -U pip wheel >/dev/null

# Install the portable control plane first. Separately owned Python companions
# then extend the same kitt namespace without vendoring code back into Agent.
"$AGENT_PY" -m pip install \
  --disable-pip-version-check --upgrade --force-reinstall \
  "$ROOT/kitt-agent-cli"
"$AGENT_PY" -m pip install \
  --disable-pip-version-check --no-deps --upgrade --force-reinstall \
  "$ROOT/kitt-assistant/packages/kitt-assistant-runtime" \
  "$ROOT/kitt-ai-workers/packages/kitt-evolution" \
  "$ROOT/kitt-ai-workers/packages/kitt-evals"

native_ok=0
if command -v cargo >/dev/null 2>&1; then
  "$AGENT_PY" -m pip install --disable-pip-version-check -U 'maturin>=1.8,<2' >/dev/null
  NATIVE_DIST="$ROOT/.cache/toolbox-native"
  rm -rf "$NATIVE_DIST"; mkdir -p "$NATIVE_DIST"
  if "$AGENT_PY" "$ROOT/kitt-toolbox/packaging/build_native_release.py" --out "$NATIVE_DIST" \
     && compgen -G "$NATIVE_DIST/*.whl" >/dev/null \
     && "$AGENT_PY" -m pip install --disable-pip-version-check --no-deps --force-reinstall "$NATIVE_DIST"/*.whl; then
    native_ok=1
  else
    echo "Native acceleration build/install failed; keeping the safe Python fallback." >&2
  fi
fi

if [[ $WITH_WORKERS -eq 1 ]]; then
  "$AGENT_PY" -m pip install --disable-pip-version-check -e "$ROOT/kitt-ai-workers[stt]"
fi

PROXY_DIR="$ROOT/kitt-reverse-proxy"
(cd "$PROXY_DIR" && npm ci --no-audit --no-fund && npm run build)
has_browser=0
for candidate in google-chrome google-chrome-stable chromium chromium-browser; do
  command -v "$candidate" >/dev/null 2>&1 && has_browser=1 && break
done
if [[ $has_browser -eq 0 ]]; then
  PLAYWRIGHT_BIN="$PROXY_DIR/node_modules/.bin/playwright"
  [[ -x "$PLAYWRIGHT_BIN" ]] || { echo "Locked Playwright binary is missing after npm ci" >&2; exit 1; }
  (cd "$PROXY_DIR" && "$PLAYWRIGHT_BIN" install chromium)
fi
(cd "$PROXY_DIR" && npm prune --omit=dev --no-audit --no-fund)

ln -sfn "$AGENT_VENV/bin/kitt" "$BIN_DIR/kitt"
cat >"$BIN_DIR/kitt-reverse-proxy" <<EOF
#!/usr/bin/env bash
exec node "$ROOT/kitt-reverse-proxy/dist/cli.js" "\$@"
EOF
cat >"$BIN_DIR/kitt-agent-gateway" <<EOF
#!/usr/bin/env bash
exec node "$ROOT/kitt-reverse-proxy/dist/gateway/cli.js" "\$@"
EOF
chmod +x "$BIN_DIR/kitt-reverse-proxy" "$BIN_DIR/kitt-agent-gateway"

if [[ -x "$ROOT/kitt-assistant/target/release/kittctl" ]]; then
  ln -sfn "$ROOT/kitt-assistant/target/release/kittctl" "$BIN_DIR/kittctl"
  [[ -x "$ROOT/kitt-assistant/target/release/kittd" ]] && ln -sfn "$ROOT/kitt-assistant/target/release/kittd" "$BIN_DIR/kittd"
  "$ROOT/kitt-assistant/target/release/kittctl" service install || true
  "$ROOT/kitt-assistant/target/release/kittctl" service start || true
fi

"$BIN_DIR/kitt" --help >/dev/null
"$BIN_DIR/kitt-reverse-proxy" --help >/dev/null
"$AGENT_PY" - <<'PY'
import kitt.daemon.client
import kitt.remote.server
import kitt.evolution
import kitt.evals.corpus
print('split KITT namespace: ok')
PY
backend="$($AGENT_PY -c "from kitt.native.bridge import NativeCodeEngine; print(NativeCodeEngine(r'$ROOT/kitt-agent-cli').status.backend)")"
echo "K.I.T.T. ecosystem installed/updated at $ROOT (Agent backend: $backend; native wheel: $native_ok)."
case ":$PATH:" in *":$BIN_DIR:"*) ;; *) echo "Add $BIN_DIR to PATH." ;; esac
