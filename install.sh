#!/bin/sh
set -eu

INSTALLER_REPO="${KITT_INSTALLER_REPO:-https://github.com/rfdetoni/kitt.git}"
INSTALLER_REF="${KITT_INSTALLER_REF:-main}"

show_progress() {
  [ -t 1 ] || return 0
  percent="$1"
  bar="$2"
  printf '\rPreparing K.I.T.T. installer  [%s] %3s%%' "$bar" "$percent"
}

finish_progress() {
  [ -t 1 ] || return 0
  printf '\n'
}

find_python() {
  for candidate in python3.14 python3.13 python3.12 python3.11 python3.10 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
      if "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)' >/dev/null 2>&1; then
        command -v "$candidate"
        return 0
      fi
    fi
  done
  return 1
}

PYTHON="$(find_python || true)"
if [ -z "$PYTHON" ]; then
  echo "K.I.T.T. requires Python 3.10+ for the installer (Agent requires Python 3.12+)." >&2
  exit 1
fi

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" 2>/dev/null && pwd || pwd)
if [ -f "$SCRIPT_DIR/installer/__main__.py" ] && [ -f "$SCRIPT_DIR/ecosystem.json" ]; then
  cd "$SCRIPT_DIR"
  exec "$PYTHON" -m installer "$@"
fi

command -v git >/dev/null 2>&1 || {
  echo "K.I.T.T. requires git." >&2
  exit 1
}

TMP_BASE="${TMPDIR:-/tmp}"
if command -v mktemp >/dev/null 2>&1; then
  WORKDIR=$(mktemp -d "$TMP_BASE/kitt-installer.XXXXXX")
else
  WORKDIR="$TMP_BASE/kitt-installer.$$"
  (umask 077 && mkdir "$WORKDIR")
fi
cleanup() { rm -rf "$WORKDIR"; }
trap cleanup EXIT HUP INT TERM

SRC="$WORKDIR/kitt"
show_progress 10 "##------------------"
if ! git clone --filter=blob:none --no-checkout "$INSTALLER_REPO" "$SRC" >/dev/null 2>&1; then
  finish_progress
  echo "Failed to download the K.I.T.T. installer." >&2
  exit 1
fi
show_progress 55 "###########---------"
if ! git -C "$SRC" fetch --force --depth 1 origin "$INSTALLER_REF" >/dev/null 2>&1; then
  finish_progress
  echo "Failed to resolve K.I.T.T. installer ref: $INSTALLER_REF" >&2
  exit 1
fi
show_progress 85 "#################---"
if ! git -C "$SRC" checkout --detach --force FETCH_HEAD >/dev/null 2>&1; then
  finish_progress
  echo "Failed to prepare the K.I.T.T. installer." >&2
  exit 1
fi
show_progress 100 "####################"
finish_progress

cd "$SRC"
"$PYTHON" -m installer "$@"
