from __future__ import annotations

import os
from typing import Any


class Console:
    def __init__(self, verbosity: int = 2) -> None:
        self.verbosity = verbosity

    def _emit(self, level: str, message: str) -> None:
        print(f"[{level.upper()}] {message}")

    def success(self, message: str) -> None:
        if self.verbosity >= 1:
            self._emit("success", message)

    def info(self, message: str) -> None:
        if self.verbosity >= 2:
            self._emit("info", message)

    def debug(self, message: str) -> None:
        if self.verbosity >= 3:
            self._emit("debug", message)

    def warning(self, message: str) -> None:
        self._emit("warning", message)

    def error(self, message: str) -> None:
        self._emit("error", message)

    def critical(self, message: str) -> None:
        self._emit("critical", message)


console = Console(int(os.getenv("VERBOSITY", "2")))
