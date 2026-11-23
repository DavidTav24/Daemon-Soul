from game.input import Command
from game.render import FrameRenderer
from game.scenes import StartScene


def test_start_screen_fills_the_play_window() -> None:
    scene = StartScene()
    renderer = FrameRenderer()

    scene.render(renderer)
    renderer.present()

    frame = renderer.frames[0]
    assert len(frame) == 12
    assert frame[2] == "     Daemon soul     "
    assert frame[4] == "     three gates     "
    assert frame[6] == "       meadow        "
    assert frame[7] == "        kiln         "
    assert frame[8] == "        night        "
    assert frame[10] == "   enter to begin    "
    assert all(len(row) == 21 for row in frame)


def test_start_begins_the_game() -> None:
    scene = StartScene()

    scene.handle_input([Command.START])
    scene.update(1)

    assert scene.is_started() is True
    assert scene.is_done() is False


def test_quit_leaves_the_start_screen() -> None:
    scene = StartScene()

    scene.handle_input([Command.QUIT])
    scene.update(1)

    assert scene.is_started() is False
    assert scene.is_done() is True


def test_movement_stays_on_the_start_screen() -> None:
    scene = StartScene()

    scene.handle_input([Command.RIGHT, Command.UP, Command.LEFT])
    scene.update(1)

    assert scene.is_started() is False
    assert scene.is_done() is False
