"""Runs the start screen, the levels, and game over one frame at a time."""

from __future__ import annotations

import sys
import time
from typing import Sequence

from game.input.command import Command
from game.render.renderer import FrameRenderer
from game.render.screen import Screen
from game.scenes.game_over import GameOverScene
from game.scenes.play import PlayScene
from game.scenes.start import StartScene
from game.theme import paint, paint_line, palette_for

_WIDTH = 21
_HEIGHT = 12
_FRAME_SECONDS = 0.05
# Jump and move pressed together often arrive a few milliseconds apart.
_CHORD_SECONDS = 0.03
_CONTROLS = "A D walk   W leap   P pause   R retry   Enter begin   Q leave"


def _center(text: str) -> str:
    pad = _WIDTH - len(text)
    left = pad // 2
    return " " * left + text + " " * (pad - left)


class GameSession:
    """Hands frames to the start screen, a level, or game over."""

    def __init__(self) -> None:
        self.mode = "start"
        self.level = 1
        self.score = 0
        self.running = True
        self.start = StartScene()
        self.play: PlayScene | None = None
        self.game_over: GameOverScene | None = None

    def step(self, commands: Sequence[Command]) -> None:
        """Apply one frame of commands to the current screen."""
        if not self.running:
            return
        if self.mode == "start":
            self._step_start(commands)
        elif self.mode == "play":
            self._step_play(commands)
        elif self.mode == "gameover":
            self._step_game_over(commands)
        elif self.mode == "win":
            self._step_win(commands)

    def status_line(self) -> str:
        """One line of score and lives for the terminal."""
        if self.mode == "play" and self.play is not None:
            paused = "  PAUSED" if self.play.is_paused() else ""
            shield = "  SHIELD" if self.play.shield or self.play._invincible > 0 else ""
            place = palette_for("play", self.level).name
            return (
                f"{place}  SCORE {self.play.score:06d}  "
                f"LIVES {self.play.lives:02d}{shield}{paused}"
            )
        if self.mode == "gameover" and self.game_over is not None:
            return f"THE GATE IS SHUT  SCORE {self.game_over.score:06d}"
        if self.mode == "win":
            return f"YOU WIN  SCORE {self.score:06d}"
        return "ASHGATE  ENTER TO BEGIN"

    def render(self, renderer: FrameRenderer) -> None:
        """Draw the current screen into ``renderer``."""
        if self.mode == "start":
            self.start.render(renderer)
        elif self.mode == "play" and self.play is not None:
            self.play.render(renderer)
        elif self.mode == "gameover" and self.game_over is not None:
            self.game_over.render(renderer)
        elif self.mode == "win":
            lines = [" " * _WIDTH] * _HEIGHT
            lines[2] = _center("ASHGATE")
            lines[4] = _center("YOU WIN")
            lines[6] = _center(f"SCORE {self.score:06d}")
            lines[8] = _center("the last gate")
            for line in lines:
                renderer.draw(line)

    def _step_start(self, commands: Sequence[Command]) -> None:
        self.start.handle_input(commands)
        self.start.update(1)
        if self.start.is_done():
            self.running = False
            return
        if self.start.is_started():
            self._begin_level(1, 0, PlayScene.starting_lives)

    def _step_play(self, commands: Sequence[Command]) -> None:
        scene = self.play
        if scene is None:
            return
        scene.handle_input(commands)
        scene.update(1)
        if scene.is_done():
            self.running = False
            return
        if scene.is_game_over():
            self.score = scene.score
            self.game_over = GameOverScene(scene.score)
            self.mode = "gameover"
            return
        if scene.is_complete():
            self.score = scene.score
            if self.level >= 3:
                self.mode = "win"
                return
            carried = scene.shield if self.level == 2 else False
            self._begin_level(self.level + 1, scene.score, scene.lives, carried)

    def _step_game_over(self, commands: Sequence[Command]) -> None:
        if self.game_over is None:
            return
        self.game_over.handle_input(commands)
        self.game_over.update(1)
        if self.game_over.is_done():
            self.running = False
            return
        if self.game_over.is_started():
            self._begin_level(1, 0, PlayScene.starting_lives)

    def _step_win(self, commands: Sequence[Command]) -> None:
        if Command.QUIT in commands:
            self.running = False
        elif Command.START in commands:
            self._begin_level(1, 0, PlayScene.starting_lives)

    def _begin_level(self, level: int, score: int, lives: int, shield: bool = False) -> None:
        scene = PlayScene(level=level)
        scene.score = score
        scene.lives = lives
        scene.shield = shield
        self.play = scene
        self.level = level
        self.score = score
        self.mode = "play"


def run_game() -> int:
    """Play in the terminal until the player quits."""
    from game.input.keyboard import KeyboardInput

    session = GameSession()
    keyboard = KeyboardInput()
    screen = Screen(width=_WIDTH + 2, height=_HEIGHT + 2)
    renderer = FrameRenderer()
    sys.stdout.write("\033[?1049h\033[?25l\033[2J\033[H")
    sys.stdout.flush()
    try:
        keyboard.open()
        next_tick = time.monotonic()
        while session.running:
            text = _read_frame(keyboard, next_tick)
            session.step(keyboard.commands_from(text))
            _draw(session, screen, renderer)
            rest = next_tick - time.monotonic()
            if rest > 0:
                time.sleep(rest)
            next_tick += _FRAME_SECONDS
            if next_tick < time.monotonic():
                next_tick = time.monotonic()
    finally:
        keyboard.close()
        sys.stdout.write("\033[?25h\033[?1049l")
        sys.stdout.flush()
    return 0


def _read_frame(keyboard: KeyboardInput, next_tick: float) -> str:
    """Read this frame's keys, including a jump and a move pressed together."""
    text = ""
    while True:
        remaining = next_tick - time.monotonic()
        if remaining <= 0:
            return text
        keyboard.wait(remaining)
        chunk = keyboard.read_available()
        if not chunk:
            continue
        text += chunk
        extra = min(_CHORD_SECONDS, max(0.0, next_tick - time.monotonic()))
        if extra > 0:
            keyboard.wait(extra)
            text += keyboard.read_available()
        return text


def _draw(session: GameSession, screen: Screen, renderer: FrameRenderer) -> None:
    renderer.clear()
    session.render(renderer)
    renderer.present()
    picture = screen.show(renderer.frames[-1])
    palette = palette_for(session.mode, session.level)
    sys.stdout.write("\033[H\033[2J")
    sys.stdout.write(paint_line(session.status_line(), palette) + "\n\n")
    sys.stdout.write(paint(picture, palette) + "\n")
    sys.stdout.write(paint_line(_CONTROLS, palette) + "\n")
    sys.stdout.flush()
