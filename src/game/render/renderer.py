"""Collects draw calls into frames."""

from __future__ import annotations

from typing import Callable


class FrameRenderer:
    """Stores each presented frame. Optionally prints it."""

    def __init__(self, output: Callable[[str], None] | None = None) -> None:
        self.frames: list[tuple[str, ...]] = []
        self._lines: list[str] = []
        self._output = output

    def clear(self) -> None:
        """Drop anything drawn since the last present."""
        self._lines = []

    def draw(self, text: str) -> None:
        """Add one line to the current frame."""
        self._lines.append(text)

    def present(self) -> None:
        """Finish the current frame and keep it."""
        frame = tuple(self._lines)
        self.frames.append(frame)
        if self._output is not None:
            self._output("\n".join(frame))
