#!/usr/bin/env python3
"""Check the Proxy schema against the Protocol sources resolved for this run."""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--proxy', type=Path, required=True)
    args = parser.parse_args()
    subprocess.run([
        sys.executable, str(args.protocol.resolve() / 'scripts/export_context_schema.py'),
        '--check', '--output', str(args.proxy.resolve() / 'src/contracts/context-schema.ts'),
    ], check=True)
    print('Protocol / Proxy context schema: identical')


if __name__ == '__main__':
    main()
