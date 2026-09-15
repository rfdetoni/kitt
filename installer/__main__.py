from __future__ import annotations

import sys
from pathlib import Path

from .cli import build_parser, main
from .managed_drift import repair_known_managed_drift
from .platforms import PlatformAdapter


def _managed_root(argv: list[str]) -> Path | None:
    args = build_parser().parse_args(argv)
    if args.list or args.uninstall or args.dry_run:
        return None
    return (args.root or PlatformAdapter.detect().default_root()).expanduser().resolve()


def run(argv: list[str] | None = None) -> int:
    effective_argv = list(sys.argv[1:] if argv is None else argv)
    root = _managed_root(effective_argv)
    if root is not None:
        repair_known_managed_drift(root)

    result = main(effective_argv)
    if result == 0 and root is not None:
        repair_known_managed_drift(root)
    return result


raise SystemExit(run())
