#!/bin/sh
set -eu

INSTALLER_REPO="${KITT_INSTALLER_REPO:-https://github.com/rfdetoni/kitt.git}"
INSTALLER_REF="${KITT_INSTALLER_REF:-main}"
PROGRESS_WIDTH=28

progress_bar() {
  percent="$1"
  filled=$((percent * PROGRESS_WIDTH / 100))
  empty=$((PROGRESS_WIDTH - filled))
  bar=""
  i=0
  while [ "$i" -lt "$filled" ]; do bar="${bar}#"; i=$((i + 1)); done
  i=0
  while [ "$i" -lt "$empty" ]; do bar="${bar}-"; i=$((i + 1)); done
  printf '%s' "$bar"
}

show_progress() {
  percent="$1"
  status="$2"
  bar="$(progress_bar "$percent")"
  if [ -t 1 ]; then
    printf '\rPreparing K.I.T.T.  [%s] %3s%%  %-28s' "$bar" "$percent" "$status"
  else
    printf 'Preparing K.I.T.T.  %3s%%  %s\n' "$percent" "$status"
  fi
}

finish_progress() {
  [ -t 1 ] && printf '\n'
  return 0
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

show_progress 2 "Checking Python"
PYTHON="$(find_python || true)"
if [ -z "$PYTHON" ]; then
  finish_progress
  echo "K.I.T.T. requires Python 3.10+ for the installer (Agent requires Python 3.12+)." >&2
  exit 1
fi
show_progress 10 "Python ready"

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" 2>/dev/null && pwd || pwd)
if [ -f "$SCRIPT_DIR/installer/__main__.py" ] && [ -f "$SCRIPT_DIR/ecosystem.json" ]; then
  show_progress 100 "Starting local installer"
  finish_progress
  cd "$SCRIPT_DIR"
  exec "$PYTHON" -m installer --force "$@"
fi

show_progress 15 "Checking Git"
command -v git >/dev/null 2>&1 || {
  finish_progress
  echo "K.I.T.T. requires git." >&2
  exit 1
}

TMP_BASE="${TMPDIR:-/tmp}"
show_progress 20 "Creating workspace"
if command -v mktemp >/dev/null 2>&1; then
  WORKDIR=$(mktemp -d "$TMP_BASE/kitt-installer.XXXXXX")
else
  WORKDIR="$TMP_BASE/kitt-installer.$$"
  (umask 077 && mkdir "$WORKDIR")
fi
cleanup() { rm -rf "$WORKDIR"; }
trap cleanup EXIT HUP INT TERM

SRC="$WORKDIR/kitt"
show_progress 28 "Preparing installer repository"
mkdir -p "$SRC"
if ! git init --quiet "$SRC" >/dev/null 2>&1 ||
   ! git -C "$SRC" remote add origin "$INSTALLER_REPO" >/dev/null 2>&1; then
  finish_progress
  echo "Failed to prepare the K.I.T.T. installer repository." >&2
  exit 1
fi
show_progress 58 "Downloading $INSTALLER_REF"
if ! git -C "$SRC" fetch --force --depth 1 origin "$INSTALLER_REF" >/dev/null 2>&1; then
  finish_progress
  echo "Failed to resolve K.I.T.T. installer ref: $INSTALLER_REF" >&2
  exit 1
fi
show_progress 82 "Preparing files"
if ! git -C "$SRC" checkout --detach --force FETCH_HEAD >/dev/null 2>&1; then
  finish_progress
  echo "Failed to prepare the K.I.T.T. installer." >&2
  exit 1
fi
show_progress 100 "Starting installation"
finish_progress

cd "$SRC"
"$PYTHON" -m installer --force "$@"
