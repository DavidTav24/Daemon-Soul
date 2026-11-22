from game import __main__ as game_main
from game.input import Command
from game.render import FrameRenderer, Screen
from game.scenes import PlayScene


def test_screen_draws_a_bordered_frame() -> None:
    screen = Screen(width=24, height=6)

    picture = screen.show(["Play", "player @ (1, 1)"])

    inner = " " * 22
    assert picture == "\n".join(
        [
            "╭" + "─" * 22 + "╮",
            "│Play" + " " * 18 + "│",
            "│player @ (1, 1)" + " " * 7 + "│",
            "│" + inner + "│",
            "│" + inner + "│",
            "╰" + "─" * 22 + "╯",
        ]
    )
    assert screen.shown == [picture]


def test_screen_clips_a_line_that_does_not_fit() -> None:
    screen = Screen(width=8, height=3)

    picture = screen.show(["player @ (1, 1)"])

    assert picture == "\n".join(
        [
            "╭" + "─" * 6 + "╮",
            "│player│",
            "╰" + "─" * 6 + "╯",
        ]
    )


def test_demo_shows_the_player_moving_on_the_screen() -> None:
    pictures = game_main.play_demo()

    assert len(pictures) == 3
    assert _player_at(pictures[0]) == (3, 11)
    assert _player_at(pictures[1]) == (4, 8)
    assert _player_at(pictures[2]) == (5, 6)


def test_one_presented_play_frame_fits_on_the_screen() -> None:
    scene = PlayScene()
    renderer = FrameRenderer()
    room = scene.environment
    screen = Screen(width=room.view_width + 2, height=room.view_height + 2)

    scene.handle_input([Command.RIGHT])
    scene.update(1)
    scene.render(renderer)
    renderer.present()
    picture = screen.show(renderer.frames[-1])

    assert len(picture.splitlines()) == room.view_height + 2
    assert len(picture.splitlines()[0]) == room.view_width + 2
    assert _player_at(picture) == (4, 11)


def _player_at(picture: str) -> tuple[int, int]:
    for y, row in enumerate(picture.splitlines()):
        x = row.find("@")
        if x != -1:
            return (x, y)
    raise AssertionError("player is missing from the screen")
