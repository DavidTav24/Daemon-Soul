"""Play the game in the terminal, or show the short demo."""

from __future__ import annotations

import sys

from game.input.command import Command
from game.render.renderer import FrameRenderer
from game.render.screen import Screen
from game.scenes.play import PlayScene
from game.session import run_game


def play_demo(screen: Screen | None = None) -> list[str]:
    """Move the player through three frames and display each one."""
    scene = PlayScene()
    room = scene.environment
    display = screen if screen is not None else Screen(
        width=room.view_width + 2,
        height=room.view_height + 2,
    )
    renderer = FrameRenderer()
    script = (
        [],
        [Command.RIGHT, Command.UP],
        [Command.RIGHT],
    )
    pictures = []
    for commands in script:
        scene.handle_input(commands)
        scene.update(1)
        renderer.clear()
        scene.render(renderer)
        renderer.present()
        picture = display.show(renderer.frames[-1])
        pictures.append(picture)
    return pictures


def main() -> int:
    """Play when a keyboard is attached. Otherwise print the demo."""
    if not sys.stdin.isatty():
        for picture in play_demo():
            print(picture)
            print()
        return 0
    return run_game()


if __name__ == "__main__":
    raise SystemExit(main())
