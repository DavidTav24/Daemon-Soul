from game.input import Command
from game.render import FrameRenderer
from game.scenes import GameOverScene


def test_game_over_screen_shows_the_score() -> None:
    scene = GameOverScene(score=100)
    renderer = FrameRenderer()

    scene.render(renderer)
    renderer.present()

    frame = renderer.frames[0]
    assert len(frame) == 12
    assert frame[3] == "  the gate is shut   "
    assert frame[5] == "      GAME OVER      "
    assert frame[7] == "    SCORE 000100     "
    assert frame[9] == " enter to try again  "
    assert all(len(row) == 21 for row in frame)


def test_start_tries_again() -> None:
    scene = GameOverScene()

    scene.handle_input([Command.START])
    scene.update(1)

    assert scene.is_started() is True
    assert scene.is_done() is False


def test_quit_leaves_the_game_over_screen() -> None:
    scene = GameOverScene()

    scene.handle_input([Command.QUIT])
    scene.update(1)

    assert scene.is_started() is False
    assert scene.is_done() is True


def test_movement_stays_on_the_game_over_screen() -> None:
    scene = GameOverScene()

    scene.handle_input([Command.LEFT, Command.RIGHT, Command.UP])
    scene.update(1)

    assert scene.is_started() is False
    assert scene.is_done() is False
