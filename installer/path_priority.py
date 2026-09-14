from __future__ import annotations

import os
import re
import shlex
import tempfile
from pathlib import Path

from .platforms import PlatformAdapter

_START = "# >>> K.I.T.T. managed PATH >>>"
_END = "# <<< K.I.T.T. managed PATH <<<"
_BLOCK_RE = re.compile(
    rf"(?:^|\n){re.escape(_START)}\n.*?\n{re.escape(_END)}(?:\n|$)",
    re.DOTALL,
)


def _same_path(left: str | Path, right: str | Path) -> bool:
    left_path = os.path.normcase(os.path.abspath(os.path.expanduser(str(left))))
    right_path = os.path.normcase(os.path.abspath(os.path.expanduser(str(right))))
    return left_path == right_path


def _prepend_process_path(bin_dir: Path) -> None:
    current = [part for part in os.environ.get("PATH", "").split(os.pathsep) if part]
    remainder = [part for part in current if not _same_path(part, bin_dir)]
    os.environ["PATH"] = os.pathsep.join([str(bin_dir), *remainder])


def _managed_block(bin_dir: Path) -> str:
    quoted = shlex.quote(str(bin_dir))
    return "\n".join(
        (
            _START,
            f"_KITT_MANAGED_BIN={quoted}",
            'case "${PATH:-}" in',
            '  "$_KITT_MANAGED_BIN"|"$_KITT_MANAGED_BIN":*) ;;',
            '  *) export PATH="$_KITT_MANAGED_BIN:${PATH:-}" ;;',
            "esac",
            "unset _KITT_MANAGED_BIN",
            _END,
        )
    )


def _replace_managed_block(existing: str, block: str) -> str:
    cleaned = _BLOCK_RE.sub("\n", existing).strip("\n")
    if cleaned:
        return f"{cleaned}\n\n{block}\n"
    return f"{block}\n"


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(raw)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _profile_targets(platform: PlatformAdapter) -> tuple[Path, ...]:
    home = Path.home()
    shell = Path(os.environ.get("SHELL", "")).name.lower()
    targets: list[Path] = [home / ".profile"]

    if shell == "bash" or (home / ".bashrc").exists():
        targets.append(home / ".bashrc")
        bash_profile = home / ".bash_profile"
        if bash_profile.exists():
            targets.append(bash_profile)

    if shell == "zsh" or platform.name == "macos" or (home / ".zshrc").exists():
        targets.extend((home / ".zprofile", home / ".zshrc"))

    if shell == "ksh" and (home / ".kshrc").exists():
        targets.append(home / ".kshrc")

    unique: list[Path] = []
    seen: set[str] = set()
    for target in targets:
        key = os.path.normcase(str(target))
        if key not in seen:
            seen.add(key)
            unique.append(target)
    return tuple(unique)


def _persist_posix_path(platform: PlatformAdapter, bin_dir: Path) -> None:
    block = _managed_block(bin_dir)
    for profile in _profile_targets(platform):
        try:
            existing = profile.read_text(encoding="utf-8") if profile.exists() else ""
            desired = _replace_managed_block(existing, block)
            if desired != existing:
                _atomic_write(profile, desired)
        except OSError:
            # Continue with the other common shell profiles. Verification below
            # will still fail closed when the managed launcher remains shadowed.
            continue


def ensure_managed_path(platform: PlatformAdapter, bin_dir: Path) -> bool:
    """Put the managed K.I.T.T. launcher directory first for current and new shells.

    Windows persistence is delegated to PlatformAdapter's HKCU Path handling.
    POSIX shells receive a small idempotent managed block in the profiles they
    actually use. Reinstalling with another bin directory replaces that block,
    so the newest managed launcher is selected in newly opened terminals.
    """
    bin_dir = bin_dir.expanduser().resolve()
    bin_dir.mkdir(parents=True, exist_ok=True)

    if platform.name == "windows":
        return platform.ensure_user_path(bin_dir)

    if not platform.posix:
        return platform.ensure_user_path(bin_dir)

    _persist_posix_path(platform, bin_dir)
    _prepend_process_path(bin_dir)
    return not platform.launcher_shadow_conflicts(bin_dir)
