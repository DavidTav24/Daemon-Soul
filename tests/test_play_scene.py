from game.input import Command
from game.scenes import PlayScene


def test_play_scene_moves_player_from_directions() -> None:
    scene = PlayScene()

    scene.handle_input([Command.RIGHT, Command.UP])
    scene.update(1)

    assert scene.player.position.x == 1
    assert scene.player.position.y == 3
    assert scene.is_done() is False


def test_play_scene_stops_when_a_frame_has_no_direction() -> None:
    scene = PlayScene()
    scene.handle_input([Command.RIGHT])
    scene.update(1)

    scene.handle_input([])
    scene.update(1)

    assert scene.player.position.x == 1
    assert scene.player.position.y == 0


def test_quit_finishes_the_scene_without_moving() -> None:
    scene = PlayScene()

    scene.handle_input([Command.QUIT])
    scene.update(1)

    assert scene.is_done() is True
    assert scene.player.position.x == 0
    assert scene.player.position.y == 0


def test_start_does_not_move_or_finish() -> None:
    scene = PlayScene()

    scene.handle_input([Command.START])
    scene.update(1)

    assert scene.is_done() is False
    assert scene.player.position.x == 0
    assert scene.player.position.y == 0
