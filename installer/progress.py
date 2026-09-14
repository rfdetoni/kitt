from __future__ import annotations

import os
import threading
import time
from typing import TextIO


def progress_frame(tick: int, width: int = 30, span: int = 7) -> str:
    """Return a deterministic bouncing activity bar without pretending to know ETA."""
    width = max(8, int(width))
    span = max(2, min(int(span), width - 1))
    travel = max(1, width - span)
    cycle = travel * 2
    offset = int(tick) % cycle
    position = offset if offset <= travel else cycle - offset
    cells = [" "] * width
    for index in range(position, position + span):
        cells[index] = "="
    head = min(width - 1, position + span)
    if head < width and cells[head] == " ":
        cells[head] = ">"
    return "".join(cells)


class InstallProgress:
    """Small dependency-free progress renderer that survives stdout log redirection."""

    def __init__(self, label: str = "Installing K.I.T.T.", stream: TextIO | None = None) -> None:
        self.label = label
        self._owns_stream = stream is None
        if stream is None:
            duplicated = os.dup(1)
            stream = os.fdopen(duplicated, "w", encoding="utf-8", buffering=1, closefd=True)
        self.stream = stream
        self.tty = bool(getattr(stream, "isatty", lambda: False)())
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._started = 0.0

    def start(self) -> None:
        self._started = time.monotonic()
        if not self.tty:
            self.stream.write(f"{self.label}...\n")
            self.stream.flush()
            return
        self._thread = threading.Thread(target=self._animate, name="kitt-installer-progress", daemon=True)
        self._thread.start()

    def _animate(self) -> None:
        tick = 0
        while not self._stop.wait(0.12):
            elapsed = max(0, int(time.monotonic() - self._started))
            minutes, seconds = divmod(elapsed, 60)
            frame = progress_frame(tick)
            self.stream.write(f"\r{self.label:<22} [{frame}] {minutes:02d}:{seconds:02d}")
            self.stream.flush()
            tick += 1

    def finish(self, success: bool = True) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        elapsed = max(0, int(time.monotonic() - self._started)) if self._started else 0
        minutes, seconds = divmod(elapsed, 60)
        if self.tty:
            mark = "done" if success else "failed"
            fill = "=" * 30 if success else "!" * 30
            self.stream.write(f"\r{self.label:<22} [{fill}] {mark:<6} {minutes:02d}:{seconds:02d}\n")
        else:
            self.stream.write(f"{self.label} {'complete' if success else 'failed'}.\n")
        self.stream.flush()
        if self._owns_stream:
            self.stream.close()
