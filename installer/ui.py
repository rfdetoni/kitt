from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Callable, Iterator, TextIO

from .catalog import EcosystemCatalog, Resolution


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
    except OSError as exc:
        raise RuntimeError(
            "interactive selection requires a terminal; use --preset or --modules in headless mode"
        ) from exc
    try:
        yield stream
    finally:
        stream.close()


@dataclass
class _SelectionState:
    catalog: EcosystemCatalog
    ordered_ids: tuple[str, ...]
    direct: set[str]
    cursor: int = 0
    message: str = "Use Up/Down to navigate and Space to toggle a top-level module."

    @classmethod
    def create(
        cls,
        catalog: EcosystemCatalog,
        initial: tuple[str, ...] | None = None,
    ) -> "_SelectionState":
        ordered = tuple(
            module.id
            for module in sorted(
                catalog.modules.values(), key=lambda module: (module.order, module.id)
            )
        )
        direct = set(initial or catalog.preset(catalog.default_preset))
        cursor = next(
            (index for index, module_id in enumerate(ordered) if module_id in direct),
            0,
        )
        return cls(catalog=catalog, ordered_ids=ordered, direct=direct, cursor=cursor)

    @property
    def resolution(self) -> Resolution:
        return self.catalog.resolve(self.ordered_direct())

    def ordered_direct(self) -> tuple[str, ...]:
        return tuple(module_id for module_id in self.ordered_ids if module_id in self.direct)

    @property
    def current_id(self) -> str:
        return self.ordered_ids[self.cursor]

    def move(self, delta: int) -> None:
        if self.ordered_ids:
            self.cursor = (self.cursor + delta) % len(self.ordered_ids)
        self.message = "Space toggles selection. [+] entries are automatic dependencies."

    def toggle_current(self) -> None:
        module_id = self.current_id
        module = self.catalog.modules[module_id]
        resolution = self.resolution
        selected = set(resolution.ids)

        if module_id in self.direct:
            self.direct.remove(module_id)
            self.message = f"Removed {module.name} from the top-level selection."
            return

        if module_id in selected:
            # Promote an automatic dependency to an explicit selection. This makes
            # Space always feel responsive and keeps the module selected if its
            # current parent is later removed.
            self.direct.add(module_id)
            parents = resolution.auto_selected_by.get(module_id, ())
            parent_names = ", ".join(
                self.catalog.modules[parent].name if parent in self.catalog.modules else parent
                for parent in parents
            )
            suffix = f" (currently also required by {parent_names})" if parent_names else ""
            self.message = f"Selected {module.name} explicitly{suffix}."
            return

        self.direct.add(module_id)
        self.message = f"Selected {module.name}. Required technologies will be added automatically."

    def select_all(self) -> None:
        self.direct = set(self.ordered_ids)
        self.message = "Selected every K.I.T.T. module explicitly."

    def select_none(self) -> None:
        self.direct.clear()
        self.message = "Selection cleared. Choose at least one top-level module."

    def select_recommended(self) -> None:
        self.direct = set(self.catalog.preset(self.catalog.default_preset))
        self.cursor = next(
            (index for index, module_id in enumerate(self.ordered_ids) if module_id in self.direct),
            0,
        )
        self.message = "Restored the recommended K.I.T.T. Agent selection."


def _supports_ansi() -> bool:
    if os.environ.get("TERM", "").lower() == "dumb":
        return False
    return bool(getattr(sys.stdout, "isatty", lambda: False)())


def _paint(text: str, code: str, *, ansi: bool) -> str:
    return f"\x1b[{code}m{text}\x1b[0m" if ansi else text


def _render(state: _SelectionState, *, fullscreen: bool) -> None:
    resolution = state.resolution
    selected = set(resolution.ids)
    ansi = fullscreen and _supports_ansi()

    if fullscreen:
        if ansi:
            sys.stdout.write("\x1b[2J\x1b[H")
        else:
            sys.stdout.write("\n\n")

    print(_paint("K.I.T.T. Ecosystem Installer", "1;36", ansi=ansi))
    print("=" * 78)
    print(" Up/Down move   Space toggle   Enter install   A all   N none   R recommended   Q quit")
    print("-" * 78)

    for index, module_id in enumerate(state.ordered_ids):
        module = state.catalog.modules[module_id]
        is_cursor = index == state.cursor

        if module_id in state.direct:
            marker = _paint("[x]", "1;32", ansi=ansi)
            status = "selected"
        elif module_id in selected:
            marker = _paint("[+]", "1;36", ansi=ansi)
            parents = resolution.auto_selected_by.get(module_id, ())
            status = "auto via " + ", ".join(parents) if parents else "automatic"
        else:
            marker = "[ ]"
            status = ""

        pointer = _paint(">", "1;33", ansi=ansi) if is_cursor else " "
        name = _paint(module.name, "1", ansi=ansi) if is_cursor else module.name
        suffix = f"  {status}" if status else ""
        print(f" {pointer} {marker} {name:<24} {module.description}{suffix}")

    direct_names = [state.catalog.modules[module_id].name for module_id in state.ordered_direct()]
    print("-" * 78)
    print(f" Top-level: {', '.join(direct_names) if direct_names else '(none)'}")
    print(f" Will install: {len(resolution.ids)} module(s)")
    print(f" {_paint('Info:', '1;33', ansi=ansi)} {state.message}")
    print(" [x] selected directly   [+] included automatically by another selection")
    sys.stdout.flush()


def _decode_windows_key() -> str:
    import msvcrt

    char = msvcrt.getwch()
    if char in {"\x00", "\xe0"}:
        special = msvcrt.getwch()
        return {
            "H": "up",
            "P": "down",
            "K": "left",
            "M": "right",
        }.get(special, "unknown")
    if char in {"\r", "\n"}:
        return "enter"
    if char == " ":
        return "space"
    if char == "\x03":
        raise KeyboardInterrupt
    if char == "\x1b":
        return "escape"
    return char.lower()


def _decode_posix_key(fd: int) -> str:
    import select

    first = os.read(fd, 1)
    if not first:
        return "eof"
    if first in {b"\r", b"\n"}:
        return "enter"
    if first == b" ":
        return "space"
    if first == b"\x03":
        raise KeyboardInterrupt
    if first == b"\x1b":
        if not select.select([fd], [], [], 0.06)[0]:
            return "escape"
        second = os.read(fd, 1)
        if second not in {b"[", b"O"} or not select.select([fd], [], [], 0.06)[0]:
            return "escape"
        third = os.read(fd, 1)
        return {
            b"A": "up",
            b"B": "down",
            b"C": "right",
            b"D": "left",
        }.get(third, "unknown")
    return first.decode("utf-8", errors="ignore").lower()


@contextmanager
def _key_reader(stream: TextIO) -> Iterator[Callable[[], str] | None]:
    """Yield a single-key reader and always restore terminal mode afterwards."""
    if os.environ.get("KITT_INSTALLER_LINE_UI") == "1":
        yield None
        return

    if os.name == "nt":
        try:
            import msvcrt  # noqa: F401
        except ImportError:
            yield None
            return
        yield _decode_windows_key
        return

    try:
        import termios
        import tty
    except ImportError:
        yield None
        return

    try:
        fd = stream.fileno()
        previous = termios.tcgetattr(fd)
    except (OSError, AttributeError, ValueError, termios.error):
        yield None
        return

    try:
        tty.setcbreak(fd)
        yield lambda: _decode_posix_key(fd)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, previous)


def _handle_key(state: _SelectionState, key: str) -> str | None:
    if key in {"up", "left", "k", "h"}:
        state.move(-1)
        return None
    if key in {"down", "right", "j", "l"}:
        state.move(1)
        return None
    if key == "space":
        state.toggle_current()
        return None
    if key == "a":
        state.select_all()
        return None
    if key == "n":
        state.select_none()
        return None
    if key == "r":
        state.select_recommended()
        return None
    if key in {"q", "escape", "eof"}:
        return "quit"
    if key == "enter":
        if not state.direct:
            state.message = "Select at least one top-level module before continuing."
            return None
        return "install"
    if len(key) == 1 and key.isdigit() and key != "0":
        index = int(key) - 1
        if index < len(state.ordered_ids):
            state.cursor = index
            state.toggle_current()
            return None
    if key not in {"unknown", ""}:
        state.message = f"Unknown key: {key!r}. Use arrows, Space and Enter."
    return None


def _choose_modules_keys(
    state: _SelectionState,
    read_key: Callable[[], str],
) -> tuple[str, ...]:
    ansi = _supports_ansi()
    if ansi:
        sys.stdout.write("\x1b[?25l")
        sys.stdout.flush()
    try:
        while True:
            _render(state, fullscreen=True)
            action = _handle_key(state, read_key())
            if action == "quit":
                raise UserCancelled("installation cancelled")
            if action == "install":
                return state.ordered_direct()
    finally:
        if ansi:
            sys.stdout.write("\x1b[?25h\x1b[0m\n")
            sys.stdout.flush()


def _choose_modules_lines(
    state: _SelectionState,
    input_stream: TextIO,
) -> tuple[str, ...]:
    """Accessible fallback when raw single-key input is unavailable."""
    while True:
        _render(state, fullscreen=False)
        print("\nSelection (number, a/n/r, Enter=install, q=quit)> ", end="", flush=True)
        line = input_stream.readline()
        if line == "":
            raise UserCancelled("terminal input closed")
        command = line.strip().lower()

        if not command:
            key = "enter"
        elif command in {"q", "quit", "exit"}:
            key = "q"
        elif command in {"a", "n", "r"}:
            key = command
        elif command.isdigit():
            index = int(command) - 1
            if 0 <= index < len(state.ordered_ids):
                state.cursor = index
                key = "space"
            else:
                state.message = f"Choose a number from 1 to {len(state.ordered_ids)}."
                continue
        else:
            state.message = f"Unknown command: {command}."
            continue

        action = _handle_key(state, key)
        if action == "quit":
            raise UserCancelled("installation cancelled")
        if action == "install":
            return state.ordered_direct()


def choose_modules(
    catalog: EcosystemCatalog,
    initial: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    """Cross-platform interactive picker with a line-oriented fallback."""
    state = _SelectionState.create(catalog, initial)
    try:
        with terminal_input() as input_stream:
            with _key_reader(input_stream) as read_key:
                if read_key is not None:
                    return _choose_modules_keys(state, read_key)
                return _choose_modules_lines(state, input_stream)
    except KeyboardInterrupt as exc:
        raise UserCancelled("installation cancelled") from exc
