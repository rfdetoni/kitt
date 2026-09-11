from __future__ import annotations

import argparse
import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .catalog import CatalogError, EcosystemCatalog
from .core import EcosystemInstaller, InstallerError, InstallerOptions
from .platforms import PlatformAdapter
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
        default=os.environ.get("KITT_REF") or "main",
        help=(
            "component branch/tag/SHA installed from every selected repository "
            "(default: main); use 'locked' for ecosystem.lock.json revisions"
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
    parser.add_argument("--force", action="store_true", help="discard local changes in managed component checkouts")
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


def _print_path_status(platform: PlatformAdapter, bin_dir: Path) -> None:
    conflicts = platform.launcher_shadow_conflicts(bin_dir)
    if conflicts:
        print("K.I.T.T. launchers were installed, but older commands shadow them in PATH:")
        for name, active in sorted(conflicts.items()):
            print(f"  - {name}: {active}")
        print(
            f"Put {bin_dir} before those command directories in PATH, then open a new shell "
            "(or run `hash -r` in POSIX shells)."
        )
        return
    if not platform.ensure_user_path(bin_dir):
        print(
            f"Ensure {bin_dir} is in PATH before any older K.I.T.T. command directory, "
            "then open a new shell."
        )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    source_root = _source_root()
    quiet_log: Path | None = None
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
            force=bool(args.force),
            ref=args.ref,
            with_ai_workers=bool(args.with_ai_workers),
            portable=bool(args.portable),
            dry_run=bool(args.dry_run),
            start_services=not bool(args.no_start_services),
        )
        installer = EcosystemInstaller(catalog, platform, options)
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
            print("Installing K.I.T.T...", flush=True)
            with _quiet_install_output() as log_path:
                quiet_log = log_path
                installer.install(resolution)
            quiet_log.unlink(missing_ok=True)
            quiet_log = None
            print("K.I.T.T. installed.")
            _print_path_status(platform, bin_dir)
            if "agent-cli" in resolution.ids:
                print("Run: kitt")
        else:
            installer.install(resolution)
            _print_path_status(platform, bin_dir)
        return 0
    except UserCancelled as exc:
        print(str(exc), file=sys.stderr)
        return 130
    except (CatalogError, InstallerError, OSError, ValueError) as exc:
        print(f"K.I.T.T. install failed: {exc}", file=sys.stderr)
        if quiet_log is not None and quiet_log.exists():
            print(f"Details: {quiet_log}", file=sys.stderr)
            print("Re-run with KITT_VERBOSE=1 for live output.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
