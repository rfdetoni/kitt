from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    temp_root = Path(os.environ.get("RUNNER_TEMP") or tempfile.gettempdir())
    root = temp_root / "kitt-portable-smoke"
    bin_dir = temp_root / "kitt-portable-bin"
    shutil.rmtree(root, ignore_errors=True)
    shutil.rmtree(bin_dir, ignore_errors=True)

    command = [
        sys.executable,
        "-m",
        "installer",
        "--modules",
        "agent-cli",
        "--minimal",
        "--portable",
        "--yes",
        "--root",
        str(root),
        "--bin-dir",
        str(bin_dir),
        "--no-start-services",
        "--no-auto-prerequisites",
        "--verbose",
    ]
    subprocess.run(command, check=True)

    state = json.loads((root / "installed-state.json").read_text(encoding="utf-8"))
    assert state["source_ref"] == "main", state
    assert set(state["resolved_modules"]) == {"protocol", "memory", "agent-cli"}, state
    assert state["repositories"], state
    assert all(len(sha) == 40 for sha in state["repositories"].values()), state

    if os.name == "nt":
        python = root / ".venv-agent" / "Scripts" / "python.exe"
        launcher = bin_dir / "kitt.cmd"
    else:
        python = root / ".venv-agent" / "bin" / "python"
        launcher = bin_dir / "kitt"

    assert python.exists(), python
    assert launcher.exists(), launcher
    subprocess.run([str(python), "-m", "kitt.cli.main", "--help"], check=True)

    print(f"portable installer smoke: ok ({sys.platform})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
