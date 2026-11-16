"""Where a frame's commands come from."""

from __future__ import annotations

from typing import Sequence

from game.input.command import Command


class ScriptedInput:
    """Replays a list of command frames. Later frames are empty."""

    def __init__(self, frames: Sequence[Sequence[Command]]) -> None:
        self._frames = [list(frame) for frame in frames]
        self._index = 0

    def poll(self) -> list[Command]:
        """Return the commands for the next frame."""
        if self._index >= len(self._frames):
            return []
        frame = self._frames[self._index]
        self._index += 1
        return frame
