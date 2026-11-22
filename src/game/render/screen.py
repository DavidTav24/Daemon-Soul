"""A text screen that displays one game frame."""

from __future__ import annotations

from typing import Sequence


class Screen:
    """Draws a frame inside a fixed border."""

    def __init__(self, width: int = 24, height: int = 6) -> None:
        if width < 3 or height < 3:
            raise ValueError("screen must be at least 3 by 3")
        self.width = width
        self.height = height
        self.shown: list[str] = []

    def show(self, lines: Sequence[str]) -> str:
        """Return the bordered picture for ``lines`` and remember it."""
        inner = self.width - 2
        rows = self.height - 2
        body = []
        for row in range(rows):
            text = lines[row] if row < len(lines) else ""
            body.append("│" + text[:inner].ljust(inner) + "│")
        top = "╭" + ("─" * inner) + "╮"
        bottom = "╰" + ("─" * inner) + "╯"
        picture = "\n".join([top, *body, bottom])
        self.shown.append(picture)
        return picture
