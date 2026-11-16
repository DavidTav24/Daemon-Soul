"""The playable scene."""

from __future__ import annotations

from typing import Sequence

from game.entities.entity import Vec2
from game.entities.player import Player
from game.environment import Environment
from game.input.command import Command
from game.render.renderer import FrameRenderer


class PlayScene:
    """Walks and jumps a player through a side-view level."""

    gravity = 1
    jump_speed = 3
    max_fall = 3

    def __init__(self, environment: Environment | None = None) -> None:
        self.environment = environment if environment is not None else Environment()
        self.player = Player()
        self.has_key = False
        self._done = False
        self._jump_pressed = False

    def handle_input(self, commands: Sequence[Command]) -> None:
        """Set the player's velocity from this frame's commands."""
        velocity = Vec2()
        self._jump_pressed = False
        for command in commands:
            if command is Command.QUIT:
                self._done = True
            elif command is Command.LEFT:
                velocity.x -= 1
            elif command is Command.RIGHT:
                velocity.x += 1
            elif command is Command.UP:
                self._jump_pressed = True
        self.player.velocity = Vec2(velocity.x, self.player.velocity.y)
        self.player.turn()

    def update(self, dt: float) -> None:
        """Walk, then apply gravity and move vertically."""
        old_x = self.player.position.x
        old_y = self.player.position.y
        vertical = self.player.velocity.y
        self.player.velocity = Vec2(self.player.velocity.x, 0)
        self.player.update(dt)
        if not self.environment.is_open(self.player.position.x, old_y):
            self.player.position.x = old_x
        self.player.velocity.y = vertical
        self._apply_gravity()
        if self._touch_hazard():
            self._jump_pressed = False
            return
        self._collect_key()
        self._jump_pressed = False

    def _touch_hazard(self) -> bool:
        position = self.player.position
        if not self.environment.is_hazard(position.x, position.y):
            return False
        self.player.position.x = 0
        self.player.position.y = 0
        self.player.velocity = Vec2()
        self.player.facing = "right"
        self.has_key = False
        return True

    def _collect_key(self) -> None:
        position = self.player.position
        tile = self.environment.tile_for(position.x, position.y)
        if tile == self.environment.key:
            self.has_key = True

    def _apply_gravity(self) -> None:
        position = self.player.position
        grounded = not self.environment.is_open(position.x, position.y - 1)
        if self._jump_pressed and grounded:
            self.player.velocity.y = self.jump_speed
        else:
            self.player.velocity.y = max(
                -self.max_fall,
                self.player.velocity.y - self.gravity,
            )
        step = 1 if self.player.velocity.y > 0 else -1
        for _ in range(int(abs(self.player.velocity.y))):
            if self.environment.is_open(position.x, position.y + step):
                position.y += step
            else:
                self.player.velocity.y = 0
                return
        landed = not self.environment.is_open(position.x, position.y - 1)
        if landed and self.player.velocity.y < 0:
            self.player.velocity.y = 0

    def render(self, renderer: FrameRenderer) -> None:
        """Draw the camera window and the player."""
        position = self.player.position
        for row in self.environment.view_rows(
            position.x, position.y, self.has_key
        ):
            renderer.draw(row)

    def is_done(self) -> bool:
        """Return True after a quit command."""
        return self._done

    def reached_finish(self) -> bool:
        """Return True when the player is standing on the finish."""
        position = self.player.position
        return self.environment.tile_for(position.x, position.y) == self.environment.finish

    def is_complete(self) -> bool:
        """Return True when the key has been collected and the player is at the end."""
        return self.has_key and self.reached_finish()
