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

Defaults to a resource-conscious core installation. AI/STT workers are optional.
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

components=(kitt-protocol kitt-memory kitt-assistant kitt-toolbox kitt-agent-cli kitt-reverse-proxy)
[[ $WITH_WORKERS -eq 1 ]] && components+=(kitt-ai-workers)
for component in "${components[@]}"; do sync_repo "$component"; done

build_rust() {
  local dir="$1"
  command -v cargo >/dev/null 2>&1 || return 1
  if [[ -f "$dir/Cargo.lock" ]]; then (cd "$dir" && cargo build --release --locked); else (cd "$dir" && cargo build --release); fi
}

if command -v cargo >/dev/null 2>&1; then
  for component in kitt-protocol kitt-memory kitt-toolbox; do build_rust "$ROOT/$component"; done
  build_rust "$ROOT/kitt-assistant"
else
  echo "Rust/Cargo not found: native daemon, memory/toolbox and Agent native backend will be skipped." >&2
fi

if [[ -d "$ROOT/kitt-assistant/apps/kitt-hud" ]]; then
  (cd "$ROOT/kitt-assistant/apps/kitt-hud" && npm ci --no-audit --no-fund && npm run build)
fi

AGENT_VENV="$ROOT/.venv-agent"
[[ -x "$AGENT_VENV/bin/python" ]] || python3 -m venv "$AGENT_VENV"
AGENT_PY="$AGENT_VENV/bin/python"
"$AGENT_PY" -m pip install --disable-pip-version-check -U pip wheel >/dev/null
native_ok=0
if command -v cargo >/dev/null 2>&1; then
  "$AGENT_PY" -m pip install --disable-pip-version-check -U 'maturin>=1.8,<2' >/dev/null
  NATIVE_DIST="$ROOT/.cache/agent-native"
  rm -rf "$NATIVE_DIST"; mkdir -p "$NATIVE_DIST"
  if "$AGENT_PY" "$ROOT/kitt-agent-cli/packaging/build_native_release.py" --out "$NATIVE_DIST" \
     && compgen -G "$NATIVE_DIST/*.whl" >/dev/null \
     && "$AGENT_PY" -m pip install --disable-pip-version-check --force-reinstall "$NATIVE_DIST"/*.whl; then
    native_ok=1
  fi
fi
if [[ $native_ok -eq 0 ]]; then
  "$AGENT_PY" -m pip install --disable-pip-version-check --upgrade --force-reinstall "$ROOT/kitt-agent-cli"
fi

if [[ $WITH_WORKERS -eq 1 ]]; then
  "$AGENT_PY" -m pip install --disable-pip-version-check -e "$ROOT/kitt-ai-workers[stt]"
fi

(cd "$ROOT/kitt-reverse-proxy" && npm ci --no-audit --no-fund && npm run build && npm prune --omit=dev --no-audit --no-fund)
has_browser=0
for candidate in google-chrome google-chrome-stable chromium chromium-browser; do command -v "$candidate" >/dev/null 2>&1 && has_browser=1 && break; done
if [[ $has_browser -eq 0 ]]; then (cd "$ROOT/kitt-reverse-proxy" && npx --yes playwright install chromium); fi

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
backend="$($AGENT_PY -c "from kitt.native.bridge import NativeCodeEngine; print(NativeCodeEngine(r'$ROOT/kitt-agent-cli').status.backend)")"
echo "K.I.T.T. ecosystem installed/updated at $ROOT (Agent backend: $backend)."
case ":$PATH:" in *":$BIN_DIR:"*) ;; *) echo "Add $BIN_DIR to PATH." ;; esac
