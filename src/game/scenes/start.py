"""The screen shown before the first level."""

from __future__ import annotations

from typing import Sequence

from game.input.command import Command
from game.render.renderer import FrameRenderer

_WIDTH = 21
_HEIGHT = 12


def _center(text: str) -> str:
    pad = _WIDTH - len(text)
    left = pad // 2
    return " " * left + text + " " * (pad - left)


class StartScene:
    """Waits for start, then the first level can begin."""

    def __init__(self) -> None:
        self._started = False
        self._done = False

    def handle_input(self, commands: Sequence[Command]) -> None:
        """Start begins the game. Quit leaves. Movement stays on this screen."""
        for command in commands:
            if command is Command.QUIT:
                self._done = True
            elif command is Command.START:
                self._started = True

    def update(self, dt: float) -> None:
        """The title does not move."""

    def render(self, renderer: FrameRenderer) -> None:
        """Draw the title in the same window as a level."""
        lines = [" " * _WIDTH] * _HEIGHT
        lines[2] = _center("ASHGATE")
        lines[4] = _center("three gates")
        lines[6] = _center("meadow")
        lines[7] = _center("kiln")
        lines[8] = _center("night")
        lines[10] = _center("enter to begin")
        for line in lines:
            renderer.draw(line)

    def is_started(self) -> bool:
        """Return True after a start command."""
        return self._started

    def is_done(self) -> bool:
        """Return True after a quit command."""
        return self._done
