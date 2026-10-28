"""Mirror Python console output to a persistent session log and optional run log."""

from __future__ import annotations

import atexit
import sys
import threading
from pathlib import Path
from typing import TextIO


class TeeStream:
    """Write text to the original console and all configured UTF-8 log files."""

    def __init__(self, console: TextIO, log_paths: list[Path]) -> None:
        self.console = console
        self.logs = [path.open("a", encoding="utf-8", buffering=1) for path in log_paths]
        self.lock = threading.RLock()

    def write(self, text: str) -> int:
        with self.lock:
            written = self.console.write(text)
            for log in self.logs:
                log.write(text)
            return written

    def flush(self) -> None:
        with self.lock:
            self.console.flush()
            for log in self.logs:
                log.flush()

    def isatty(self) -> bool:
        return self.console.isatty()

    @property
    def encoding(self) -> str:
        return getattr(self.console, "encoding", None) or "utf-8"

    def close_logs(self) -> None:
        with self.lock:
            for log in self.logs:
                log.flush()
                log.close()

    def fileno(self) -> int:
        return self.console.fileno()

    def writable(self) -> bool:
        return True

    def __getattr__(self, name: str):
        return getattr(self.console, name)


_installed = False
_session_log: Path | None = None
_run_log: Path | None = None
_streams: list[TeeStream] = []


def install_console_logging(session_log: str | Path) -> "ConsoleLog":
    """Start mirroring Python stdout/stderr to a persistent session log."""
    global _installed, _session_log
    if _installed:
        return _console_log
    _session_log = Path(session_log)
    _session_log.parent.mkdir(parents=True, exist_ok=True)
    for name in ("stdout", "stderr"):
        stream = TeeStream(getattr(sys, name), [_session_log])
        setattr(sys, name, stream)
        _streams.append(stream)
    _installed = True
    atexit.register(_close)
    return _console_log


class ConsoleLog:
    """Handle that adds a per-run destination to the installed console tee."""

    def add_log_target(self, run_log: str | Path) -> None:
        set_run_log(run_log)


_console_log = ConsoleLog()


def set_run_log(run_log: str | Path) -> None:
    """Also mirror subsequent Python output to the current run's log."""
    global _run_log
    _run_log = Path(run_log)
    _run_log.parent.mkdir(parents=True, exist_ok=True)
    for stream in _streams:
        if str(_run_log.resolve()) not in [str(Path(log.name).resolve()) for log in stream.logs]:
            stream.logs.append(_run_log.open("a", encoding="utf-8", buffering=1))


def _close() -> None:
    for stream in _streams:
        stream.flush()
        stream.close_logs()
