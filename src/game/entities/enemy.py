"""A hazard that walks the ground."""

from __future__ import annotations

from typing import Callable


class Enemy:
    """Patrols solid ground and turns around at anything it cannot walk on."""

    def __init__(self, x: int, y: int) -> None:
        self.home_x = x
        self.home_y = y
        self.x = x
        self.y = y
        self.direction = 1
        self.alive = True

    def tile(self) -> tuple[int, int]:
        return (self.x, self.y)

    def reset(self) -> None:
        self.x = self.home_x
        self.y = self.home_y
        self.direction = 1
        self.alive = True

    def step(self, can_walk: Callable[[int, int], bool]) -> None:
        """Walk one tile, reversing at the edge of the patrol."""
        if not self.alive:
            return
        nxt = self.x + self.direction
        if not can_walk(nxt, self.y):
            self.direction *= -1
            nxt = self.x + self.direction
            if not can_walk(nxt, self.y):
                return
        self.x = nxt
