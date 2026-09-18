from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .catalog import CatalogError, EcosystemCatalog
from .core import InstallerError, InstallerOptions
from .path_priority import ensure_managed_path
from .platforms import PlatformAdapter
from .progress import InstallProgress
from .source_free import SourceFreeEcosystemInstaller
from .ui import UserCancelled, choose_modules


_TRUTHY = {"1", "true", "yes", "on"}


def _source_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _split_modules(values: list[str] | None) -> list[str]:
    result: list[str] = []
    for value in values or []:
        for item in value.split(","):
            item = item.strip()
            if item and item not in result:
                result.append(item)
    return result


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in _TRUTHY


@contextmanager
def _quiet_install_output() -> Iterator[Path]:
    """Redirect installer/build chatter to a temporary log while keeping the UI clean."""
    fd, raw_path = tempfile.mkstemp(prefix="kitt-install-", suffix=".log")
    os.close(fd)
    path = Path(raw_path)
    saved_stdout = os.dup(1)
    saved_stderr = os.dup(2)
    try:
        sys.stdout.flush()
        sys.stderr.flush()
        with path.open("ab", buffering=0) as sink:
            os.dup2(sink.fileno(), 1)
            os.dup2(sink.fileno(), 2)
            try:
                yield path
            finally:
                sys.stdout.flush()
                sys.stderr.flush()
    finally:
        os.dup2(saved_stdout, 1)
        os.dup2(saved_stderr, 2)
        os.close(saved_stdout)
        os.close(saved_stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kitt-installer",
        description=(
            "Install K.I.T.T. ecosystem modules. Selecting a module automatically "
            "pulls its required and integrated ecosystem technologies."
        ),
    )
    parser.add_argument(
        "--modules",
        action="append",
        metavar="MODULES",
        help="comma-separated top-level modules (for example: agent-cli)",
    )
    parser.add_argument("--preset", help="catalog preset (agent, assistant, web, full)")
    parser.add_argument(
        "--ref",
        default=os.environ.get("KITT_REF") or "locked",
        help=(
            "component branch/tag/SHA installed from every selected repository "
            "(default: locked snapshot from ecosystem.lock.json)"
        ),
    )
    parser.add_argument("--root", type=Path, help="installation root")
    parser.add_argument("--bin-dir", type=Path, help="command launcher directory")
    parser.add_argument("--with-ai-workers", action="store_true", help="also install heavy AI/STT worker dependencies")
    parser.add_argument(
        "--portable",
        action="store_true",
        help="explicitly skip Rust/native builds and use portable fallbacks where available",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="non-interactive; use --modules/--preset or the default agent preset",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="show repository, build and package-manager output",
    )
    parser.add_argument("--dry-run", "--plan", action="store_true", help="resolve and validate the plan without changing the system")
    parser.add_argument("--no-start-services", action="store_true", help="install services without starting them")
    parser.add_argument("--uninstall", action="store_true", help="remove the complete managed K.I.T.T. installation")
    parser.add_argument("--list", action="store_true", help="list modules and presets, then exit")
    return parser


def _print_catalog(catalog: EcosystemCatalog) -> None:
    print(catalog.name)
    print("\nModules:")
    for module in sorted(catalog.modules.values(), key=lambda item: (item.order, item.id)):
        companions = [*module.requires, *module.companions]
        suffix = f" -> auto: {', '.join(companions)}" if companions else ""
        print(f"  {module.id:<14} {module.name:<22} {module.description}{suffix}")
    print("\nPresets:")
    for preset_id in sorted(catalog.presets):
        print(
            f"  {preset_id:<14} {catalog.preset_names[preset_id]:<22} "
            f"{catalog.preset_descriptions[preset_id]}"
        )


def _ensure_launcher_priority(platform: PlatformAdapter, bin_dir: Path) -> None:
    """Fail installation finalization unless new terminals will prefer managed launchers."""
    path_ready = ensure_managed_path(platform, bin_dir)
    conflicts = platform.launcher_shadow_conflicts(bin_dir)
    if conflicts:
        details = ", ".join(f"{name} -> {active}" for name, active in sorted(conflicts.items()))
        raise InstallerError(
            "K.I.T.T. installed its launchers but could not guarantee that they are first in PATH: "
            f"{details}. Managed launcher directory: {bin_dir}"
        )
    if not path_ready:
        raise InstallerError(
            "K.I.T.T. installed its launchers but could not persist the managed launcher directory "
            f"at the front of PATH for new terminals: {bin_dir}"
        )


def _record_source_ref(root: Path, ref: str | None) -> None:
    """Persist the update channel used for the completed installation."""
    state_path = root / "installed-state.json"
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallerError(f"could not read installed state at {state_path}") from exc
    if not isinstance(payload, dict):
        raise InstallerError(f"installed state at {state_path} is not an object")

    source_ref = (ref or "locked").strip() or "locked"
    if source_ref.lower() == "lock":
        source_ref = "locked"
    payload["source_ref"] = source_ref

    temporary = state_path.with_suffix(".ref.tmp")
    try:
        temporary.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, state_path)
    except OSError as exc:
        temporary.unlink(missing_ok=True)
        raise InstallerError(f"could not persist install source ref at {state_path}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    source_root = _source_root()
    quiet_log: Path | None = None
    active_progress: InstallProgress | None = None
    verbose = bool(args.verbose or _env_flag("KITT_VERBOSE"))
    non_interactive = bool(args.yes or _env_flag("KITT_NON_INTERACTIVE"))

    try:
        catalog = EcosystemCatalog.load(source_root)
        platform = PlatformAdapter.detect()
        if args.list:
            _print_catalog(catalog)
            return 0

        root = (args.root or platform.default_root()).expanduser().resolve()
        bin_dir = (args.bin_dir or platform.default_bin_dir()).expanduser().resolve()
        options = InstallerOptions(
            root=root,
            bin_dir=bin_dir,
            ref=args.ref,
            with_ai_workers=bool(args.with_ai_workers),
            portable=bool(args.portable),
            dry_run=bool(args.dry_run),
            start_services=not bool(args.no_start_services),
        )
        installer = SourceFreeEcosystemInstaller(catalog, platform, options)
        if args.uninstall:
            installer.uninstall()
            return 0

        requested = _split_modules(args.modules)
        env_modules = os.environ.get("KITT_MODULES")
        if not requested and env_modules:
            requested = _split_modules([env_modules])
        preset = args.preset or os.environ.get("KITT_PRESET")
        if preset:
            requested.extend(
                module for module in catalog.preset(preset) if module not in requested
            )
        if args.with_ai_workers and "ai-workers" not in requested:
            requested.append("ai-workers")

        if not requested:
            if non_interactive:
                requested = list(catalog.preset(catalog.default_preset))
            else:
                requested = list(choose_modules(catalog))

        resolution = catalog.resolve(requested)
        concise = not verbose and not args.dry_run
        if concise:
            active_progress = InstallProgress()
            active_progress.start()
            try:
                with _quiet_install_output() as log_path:
                    quiet_log = log_path
                    installer.install(resolution)
                    _record_source_ref(root, args.ref)
                _ensure_launcher_priority(platform, bin_dir)
            except Exception:
                active_progress.finish(False)
                active_progress = None
                raise
            active_progress.finish(True)
            active_progress = None
            quiet_log.unlink(missing_ok=True)
            quiet_log = None
            if "agent-cli" in resolution.ids:
                print("Run: kitt")
        else:
            installer.install(resolution)
            if not args.dry_run:
                _record_source_ref(root, args.ref)
                _ensure_launcher_priority(platform, bin_dir)
        return 0
    except UserCancelled as exc:
        if active_progress is not None:
            active_progress.finish(False)
        print(str(exc), file=sys.stderr)
        return 130
    except (CatalogError, InstallerError, OSError, ValueError) as exc:
        if active_progress is not None:
            active_progress.finish(False)
        print(f"K.I.T.T. install failed: {exc}", file=sys.stderr)
        if quiet_log is not None and quiet_log.exists():
            print(f"Details: {quiet_log}", file=sys.stderr)
            print("Re-run with KITT_VERBOSE=1 for live output.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
