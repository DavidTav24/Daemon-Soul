"""Show a few play frames on the text screen."""

from __future__ import annotations

from game.input.command import Command
from game.render.renderer import FrameRenderer
from game.render.screen import Screen
from game.scenes.play import PlayScene


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
    """Print the demo screen."""
    for picture in play_demo():
        print(picture)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
