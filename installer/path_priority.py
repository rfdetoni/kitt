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
    left_path = os.path.normcase(
        os.path.realpath(os.path.abspath(os.path.expanduser(str(left))))
    )
    right_path = os.path.normcase(
        os.path.realpath(os.path.abspath(os.path.expanduser(str(right))))
    )
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
            '  *)',
            '    _KITT_MANAGED_REST=""',
            '    _KITT_MANAGED_OLD_IFS=$IFS',
            "    IFS=':'",
            '    for _KITT_MANAGED_ENTRY in ${PATH:-}; do',
            '      [ "$_KITT_MANAGED_ENTRY" = "$_KITT_MANAGED_BIN" ] && continue',
            '      if [ -n "$_KITT_MANAGED_REST" ]; then',
            '        _KITT_MANAGED_REST="$_KITT_MANAGED_REST:$_KITT_MANAGED_ENTRY"',
            '      else',
            '        _KITT_MANAGED_REST="$_KITT_MANAGED_ENTRY"',
            '      fi',
            '    done',
            '    IFS=$_KITT_MANAGED_OLD_IFS',
            '    export PATH="$_KITT_MANAGED_BIN${_KITT_MANAGED_REST:+:$_KITT_MANAGED_REST}"',
            '    unset _KITT_MANAGED_REST _KITT_MANAGED_OLD_IFS _KITT_MANAGED_ENTRY',
            '    ;;',
            "esac",
            "unset _KITT_MANAGED_BIN",
            _END,
        )
    )


def _fish_quote(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def _managed_fish_block(bin_dir: Path) -> str:
    quoted = _fish_quote(str(bin_dir))
    return "\n".join(
        (
            _START,
            f"set -l _kitt_managed_bin {quoted}",
            "set -l _kitt_managed_rest",
            "for _kitt_managed_entry in $PATH",
            '    if test "$_kitt_managed_entry" != "$_kitt_managed_bin"',
            '        set -a _kitt_managed_rest "$_kitt_managed_entry"',
            "    end",
            "end",
            'set -gx PATH "$_kitt_managed_bin" $_kitt_managed_rest',
            "set -e _kitt_managed_bin _kitt_managed_rest _kitt_managed_entry",
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


def _fish_target() -> Path | None:
    home = Path.home()
    shell = Path(os.environ.get("SHELL", "")).name.lower()
    fish_config = home / ".config" / "fish"
    if shell == "fish" or fish_config.exists():
        return fish_config / "conf.d" / "kitt-path.fish"
    return None


def _persist_block(path: Path, block: str) -> bool:
    try:
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        desired = _replace_managed_block(existing, block)
        if desired != existing:
            _atomic_write(path, desired)
        return path.read_text(encoding="utf-8") == desired
    except OSError:
        return False


def _persist_posix_path(platform: PlatformAdapter, bin_dir: Path) -> bool:
    shell_block = _managed_block(bin_dir)
    results = [_persist_block(profile, shell_block) for profile in _profile_targets(platform)]
    fish = _fish_target()
    if fish is not None:
        results.append(_persist_block(fish, _managed_fish_block(bin_dir)))
    return bool(results) and all(results)


def ensure_managed_path(platform: PlatformAdapter, bin_dir: Path) -> bool:
    """Put the managed K.I.T.T. launcher directory first for current and new shells.

    Windows persistence is delegated to PlatformAdapter's HKCU Path handling.
    POSIX shells receive an idempotent managed block in their startup profiles;
    Fish receives a conf.d entry. Reinstalling replaces the owned block, so an
    older managed directory cannot regain priority. Failure to persist any
    required startup file is reported to the installer instead of being ignored.
    """
    bin_dir = bin_dir.expanduser().resolve()
    bin_dir.mkdir(parents=True, exist_ok=True)

    if platform.name == "windows":
        return platform.ensure_user_path(bin_dir)

    if not platform.posix:
        return platform.ensure_user_path(bin_dir)

    persisted = _persist_posix_path(platform, bin_dir)
    _prepend_process_path(bin_dir)
    return persisted and not platform.launcher_shadow_conflicts(bin_dir)
