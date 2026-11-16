from game.input import Command
from game.scenes import PlayScene


def test_player_starts_facing_right() -> None:
    scene = PlayScene()

    assert scene.player.facing == "right"
    assert scene.player.name == "player"


def test_player_turns_to_face_the_way_they_walk() -> None:
    scene = PlayScene()

    scene.handle_input([Command.LEFT])
    assert scene.player.facing == "left"

    scene.handle_input([Command.RIGHT])
    assert scene.player.facing == "right"

    scene.handle_input([])
    assert scene.player.facing == "right"
