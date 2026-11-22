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
    walk_speed = 1
    coin_points = 100
    starting_lives = 3
    respawn_delay = 10
    enemy_pace = 2
    invincible_frames = 20

    def __init__(self, environment: Environment | None = None, level: int = 1) -> None:
        self.environment = environment if environment is not None else Environment(level)
        self.player = Player()
        self.has_key = False
        self.collected_coins: set[tuple[int, int]] = set()
        self.collected_shields: set[tuple[int, int]] = set()
        self.shield = False
        self.score = 0
        self.lives = self.starting_lives
        self._game_over = False
        self._paused = False
        self._done = False
        self._jump_pressed = False
        self._holding_direction = False
        self._respawn_wait = 0
        self._invincible = 0
        self._enemy_tick = 0

    def handle_input(self, commands: Sequence[Command]) -> None:
        """Set the player's velocity from this frame's commands."""
        if self._game_over:
            return
        if Command.PAUSE in commands:
            self._paused = not self._paused
        if self._paused:
            self._jump_pressed = False
            if Command.QUIT in commands:
                self._done = True
            if Command.RESTART in commands:
                self._restart_level()
            return
        if self._respawn_wait > 0:
            self._jump_pressed = False
            self._holding_direction = False
            if Command.QUIT in commands:
                self._done = True
            return
        held = 0
        self._jump_pressed = False
        for command in commands:
            if command is Command.QUIT:
                self._done = True
            elif command is Command.LEFT:
                held -= 1
            elif command is Command.RIGHT:
                held += 1
            elif command is Command.UP:
                self._jump_pressed = True
        self._holding_direction = held != 0
        if held > 0:
            self.player.velocity.x = self.walk_speed
        elif held < 0:
            self.player.velocity.x = -self.walk_speed
        self.player.turn()

    def update(self, dt: float) -> None:
        """Walk, then apply gravity and move vertically."""
        if self._game_over or self._paused:
            return
        if self._respawn_wait > 0:
            self._respawn_wait -= 1
            self._holding_direction = False
            self._jump_pressed = False
            self.player.velocity = Vec2()
            return
        if self._invincible > 0:
            self._invincible -= 1
        if not self._holding_direction:
            grounded = not self._is_open(self.player.position.x, self.player.position.y - 1)
            if grounded and not self._jump_pressed:
                self.player.velocity.x = 0
        old_x = self.player.position.x
        old_y = self.player.position.y
        takeoff = self._jump_pressed and not self._is_open(old_x, old_y - 1)
        vertical = self.player.velocity.y
        self.player.velocity = Vec2(self.player.velocity.x, 0)
        self.player.update(dt)
        foot_y = old_y + 1 if self.environment.terrain_at(old_x, old_y) == "v" else old_y
        if not self._is_open(self.player.position.x, foot_y):
            self.player.position.x = old_x
        elif foot_y != old_y and not self._is_open(self.player.position.x, foot_y - 1):
            self.player.position.y = foot_y
        self.player.velocity.y = vertical
        self._apply_gravity(takeoff)
        player_before = self.environment.tile_for(old_x, old_y)
        player_after = self.environment.tile_for(
            self.player.position.x, self.player.position.y
        )
        fell = self.player.position.y < old_y
        if fell:
            self.environment.eliminate_at(player_after)
        enemies_before = self.environment.enemy_tiles()
        if (
            self._touch_hazard(old_y)
            or player_before in enemies_before
            or player_after in enemies_before
        ):
            if self._take_hit():
                return
        self._enemy_tick += 1
        if self._enemy_tick % self.enemy_pace == 0:
            self.environment.step_enemies()
        if fell:
            self.environment.eliminate_at(player_after)
        elif player_after in self.environment.enemy_tiles():
            if self._take_hit():
                return
        self._collect_key()
        self._collect_coin()
        self._collect_shield()
        self._jump_pressed = False

    def is_paused(self) -> bool:
        """Return True while the pause menu is open."""
        return self._paused

    def _restart_level(self) -> None:
        """Put this level back to its start and close the pause menu."""
        self.player.position.x = 0
        self.player.position.y = 0
        self.player.velocity = Vec2()
        self.player.facing = "right"
        self.has_key = False
        self.score -= self.coin_points * len(self.collected_coins)
        self.collected_coins.clear()
        self.collected_shields.clear()
        self.shield = False
        self._invincible = 0
        self.environment.reset_enemies()
        self._paused = False
        self._jump_pressed = False
        self._respawn_wait = 0
        self._enemy_tick = 0

    def _take_hit(self) -> bool:
        """Spend the shield for one safe second, or lose a life. Return True when play stops."""
        if self._invincible > 0:
            return False
        if self.shield:
            self.shield = False
            self._invincible = self.invincible_frames
            return False
        self._suffer_hit()
        return True

    def _suffer_hit(self) -> None:
        self.player.position.x = 0
        self.player.position.y = 0
        self.player.velocity = Vec2()
        self.player.facing = "right"
        self.environment.reset_enemies()
        self._enemy_tick = 0
        self._invincible = 0
        self._jump_pressed = False
        self.has_key = False
        self.score -= self.coin_points * len(self.collected_coins)
        self.collected_coins.clear()
        self.collected_shields.clear()
        self.lives -= 1
        if self.lives <= 0:
            self.lives = 0
            self._game_over = True
        else:
            self._respawn_wait = self.respawn_delay
        self._jump_pressed = False

    def _touch_hazard(self, old_y: float) -> bool:
        position = self.player.position
        cell = self.environment.terrain_at(position.x, position.y)
        if cell == "^":
            return True
        sunk_below_pit = self.environment.terrain_at(position.x, position.y + 1) == "v"
        return sunk_below_pit and position.y < old_y

    def _collect_key(self) -> None:
        position = self.player.position
        tile = self.environment.tile_for(position.x, position.y)
        if tile == self.environment.key:
            self.has_key = True

    def _collect_coin(self) -> None:
        position = self.player.position
        tile = self.environment.tile_for(position.x, position.y)
        if tile in self.environment.coins and tile not in self.collected_coins:
            self.collected_coins.add(tile)
            self.score += self.coin_points

    def _collect_shield(self) -> None:
        position = self.player.position
        tile = self.environment.tile_for(position.x, position.y)
        if tile in self.environment.shields and tile not in self.collected_shields:
            self.collected_shields.add(tile)
            self.shield = True

    def _apply_gravity(self, takeoff: bool) -> None:
        position = self.player.position
        if takeoff:
            self.player.velocity.y = self.jump_speed
        else:
            self.player.velocity.y = max(
                -self.max_fall,
                self.player.velocity.y - self.gravity,
            )
        step = 1 if self.player.velocity.y > 0 else -1
        for _ in range(int(abs(self.player.velocity.y))):
            if self._is_open(position.x, position.y + step):
                position.y += step
            else:
                self.player.velocity.y = 0
                return
        landed = not self._is_open(position.x, position.y - 1)
        if landed and self.player.velocity.y < 0:
            self.player.velocity.y = 0

    def render(self, renderer: FrameRenderer) -> None:
        """Draw the camera window and the player."""
        position = self.player.position
        for row in self.environment.view_rows(
            position.x,
            position.y,
            self.has_key,
            self.collected_coins,
            self.collected_shields,
            self.shield or self._invincible > 0,
            self._hurt_flash(),
        ):
            renderer.draw(row)

    def _hurt_flash(self) -> bool:
        """Hide the player on alternate frames after a hit, like Mario."""
        frames = self._invincible or self._respawn_wait
        return frames > 0 and frames % 2 == 0

    def is_done(self) -> bool:
        """Return True after a quit command."""
        return self._done

    def is_game_over(self) -> bool:
        """Return True when the player has no lives left."""
        return self._game_over

    def _is_open(self, x: float, y: float) -> bool:
        if self.environment.is_open(x, y, self.has_key):
            return True
        return self.environment.terrain_at(x, y + 1) == "v"

    def reached_finish(self) -> bool:
        """Return True when the player is standing in the doorway."""
        position = self.player.position
        return self.environment.tile_for(position.x, position.y) == self.environment.finish

    def is_complete(self) -> bool:
        """Return True when the key has unlocked the door and the player is inside."""
        return self.has_key and self.reached_finish()
