from __future__ import annotations

import sys

from .cli import main


def run(argv: list[str] | None = None) -> int:
    return main(list(sys.argv[1:] if argv is None else argv))


raise SystemExit(run())
