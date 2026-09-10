from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from typing import Iterator, TextIO

from .catalog import EcosystemCatalog


class UserCancelled(RuntimeError):
    pass


@contextmanager
def terminal_input() -> Iterator[TextIO]:
    """Use the real console even when the bootstrap itself came from a pipe."""
    if sys.stdin.isatty():
        yield sys.stdin
        return
    target = "CONIN$" if os.name == "nt" else "/dev/tty"
    try:
        stream = open(target, "r", encoding="utf-8", errors="replace")
    except OSError:
        raise RuntimeError(
            "interactive selection requires a terminal; use --preset or --modules in headless mode"
        )
    try:
        yield stream
    finally:
        stream.close()


def _print_menu(catalog: EcosystemCatalog, direct: set[str]) -> None:
    resolution = catalog.resolve(sorted(direct))
    selected = set(resolution.ids)
    ordered = sorted(catalog.modules.values(), key=lambda module: (module.order, module.id))

    print("\nK.I.T.T. Ecosystem Setup")
    print("Select top-level modules. Integrated technologies are pulled automatically.\n")
    for index, module in enumerate(ordered, 1):
        if module.id in direct:
            marker = "[x]"
            reason = "selected"
        elif module.id in selected:
            marker = "[+]"
            parents = ", ".join(resolution.auto_selected_by.get(module.id, ()))
            reason = f"automatic via {parents}" if parents else "automatic dependency"
        else:
            marker = "[ ]"
            reason = ""
        suffix = f"  ({reason})" if reason else ""
        print(f" {index:>2}. {marker} {module.name:<22} {module.description}{suffix}")

    print("\n[x] explicitly selected   [+] installed automatically")
    print("Commands: number=toggle  r=recommended agent  a=all  n=none  p <preset>  Enter=install  q=quit")
    print("Presets: " + ", ".join(
        f"{key} ({catalog.preset_names[key]})" for key in sorted(catalog.presets)
    ))


def choose_modules(catalog: EcosystemCatalog, initial: tuple[str, ...] | None = None) -> tuple[str, ...]:
    direct = set(initial or catalog.preset(catalog.default_preset))
    ordered = sorted(catalog.modules.values(), key=lambda module: (module.order, module.id))

    with terminal_input() as input_stream:
        while True:
            _print_menu(catalog, direct)
            print("\nSelection> ", end="", flush=True)
            line = input_stream.readline()
            if line == "":
                raise UserCancelled("terminal input closed")
            command = line.strip()
            if not command:
                if not direct:
                    print("Select at least one module.")
                    continue
                return tuple(module.id for module in ordered if module.id in direct)
            lowered = command.lower()
            if lowered in {"q", "quit", "exit"}:
                raise UserCancelled("installation cancelled")
            if lowered == "r":
                direct = set(catalog.preset(catalog.default_preset))
                continue
            if lowered == "a":
                direct = set(catalog.modules)
                continue
            if lowered == "n":
                direct.clear()
                continue
            if lowered.startswith("p "):
                preset = lowered.split(None, 1)[1].strip()
                direct = set(catalog.preset(preset))
                continue
            try:
                index = int(command)
            except ValueError:
                print(f"Unknown command: {command}")
                continue
            if index < 1 or index > len(ordered):
                print(f"Choose a number from 1 to {len(ordered)}.")
                continue
            module_id = ordered[index - 1].id
            if module_id in direct:
                direct.remove(module_id)
            else:
                direct.add(module_id)
