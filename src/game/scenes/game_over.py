"""The screen shown when the player has no lives left."""

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


class GameOverScene:
    """Shows the final score and waits for another try."""

    def __init__(self, score: int = 0) -> None:
        self.score = score
        self._started = False
        self._done = False

    def handle_input(self, commands: Sequence[Command]) -> None:
        """Start tries again. Quit leaves. Movement stays on this screen."""
        for command in commands:
            if command is Command.QUIT:
                self._done = True
            elif command is Command.START:
                self._started = True

    def update(self, dt: float) -> None:
        """The screen does not move."""

    def render(self, renderer: FrameRenderer) -> None:
        """Draw the score in the same window as a level."""
        lines = [" " * _WIDTH] * _HEIGHT
        lines[3] = _center("the gate is shut")
        lines[5] = _center("GAME OVER")
        lines[7] = _center(f"SCORE {self.score:06d}")
        lines[9] = _center("enter to try again")
        for line in lines:
            renderer.draw(line)

    def is_started(self) -> bool:
        """Return True after a start command."""
        return self._started

    def is_done(self) -> bool:
        """Return True after a quit command."""
        return self._done
