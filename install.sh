#!/usr/bin/env bash
# ==============================================================================
# K.I.T.T. Universal Entrypoint Installer (detects Linux vs macOS)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$(uname -s)" in
    Linux*)     "$SCRIPT_DIR/scripts/install-linux.sh" "$@" ;;
    Darwin*)    "$SCRIPT_DIR/scripts/install-macos.sh" "$@" ;;
    CYGWIN*|MINGW*|MSYS*)
        echo "On Windows, please run PowerShell as Administrator and execute:"
        echo "powershell -ExecutionPolicy Bypass -File scripts/install-windows.ps1"
        ;;
    *)
        echo "Unsupported OS: $(uname -s)"
        exit 1
        ;;
esac
