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
    PAUSE = "pause"
    RESTART = "restart"


def parse_command(text: str) -> Command | None:
    """Return a command for ``text``, or None when it is not one."""
    if not isinstance(text, str):
        return None
    try:
        return Command(text.strip().lower())
    except ValueError:
        return None


def commands_from_names(names: object) -> list[Command]:
    """Keep known command names and drop everything else."""
    try:
        items = list(names)  # type: ignore[arg-type]
    except TypeError:
        return []
    if isinstance(names, str):
        return []
    allowed = {command.name for command in Command}
    return [Command[name] for name in items if isinstance(name, str) and name in allowed]
