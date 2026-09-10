from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .catalog import CatalogError, EcosystemCatalog
from .core import EcosystemInstaller, InstallerError, InstallerOptions
from .platforms import PlatformAdapter
from .ui import UserCancelled, choose_modules


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
        default=os.environ.get("KITT_REF") or None,
        help="override ecosystem.lock.json and install the same branch/tag/SHA from every selected repository",
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
    parser.add_argument("--yes", "-y", action="store_true", help="non-interactive; use --modules/--preset or the default agent preset")
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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    source_root = _source_root()

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
            if args.yes:
                requested = list(catalog.preset(catalog.default_preset))
            else:
                requested = list(choose_modules(catalog))
        elif not args.yes and not args.dry_run:
            # Explicit module arguments are already an intentional selection; avoid a
            # second menu so automation and shell history stay predictable.
            pass

        resolution = catalog.resolve(requested)
        installer.install(resolution)
        return 0
    except UserCancelled as exc:
        print(str(exc), file=sys.stderr)
        return 130
    except (CatalogError, InstallerError, OSError, ValueError) as exc:
        print(f"K.I.T.T. installer error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
