"""Actions a player can request on one frame."""

from __future__ import annotations

from enum import Enum


class Command(Enum):
    """A single requested action."""

    START = "start"
    QUIT = "quit"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


def parse_command(text: str) -> Command | None:
    """Return a command for ``text``, or None when it is not one."""
    try:
        return Command(text.strip().lower())
    except ValueError:
        return None
