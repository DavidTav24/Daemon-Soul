from game.environment import Environment
from game.input import Command
from game.scenes import PlayScene


def test_level_is_a_side_view_with_start_and_finish() -> None:
    room = Environment()

    assert room.width == 40
    assert room.height == 12
    rows = room.rows(0, 0)
    assert rows[11] == "#" * 40
    assert rows[10][2] == "@"
    assert rows[10][36] == "F"
    assert room.view_width < room.width


def test_player_stops_at_the_left_wall() -> None:
    scene = PlayScene()

    for _ in range(40):
        scene.handle_input([Command.LEFT])
        scene.update(1)

    assert scene.player.position.x == -1
    assert scene.environment.is_open(scene.player.position.x, 0)
    assert scene.environment.is_open(-2, 0) is False


def test_gravity_accelerates_the_fall() -> None:
    scene = PlayScene()
    scene.player.position.y = 6

    scene.handle_input([])
    scene.update(1)
    assert (scene.player.position.y, scene.player.velocity.y) == (5, -1)

    scene.update(1)
    assert (scene.player.position.y, scene.player.velocity.y) == (3, -2)

    scene.update(1)
    assert (scene.player.position.y, scene.player.velocity.y) == (0, 0)


def test_jump_rises_then_gravity_returns_the_player_to_the_ground() -> None:
    scene = PlayScene()

    scene.handle_input([Command.UP])
    scene.update(1)
    assert scene.player.position.y == 3

    scene.handle_input([])
    scene.update(1)
    scene.update(1)
    scene.update(1)
    scene.update(1)
    scene.update(1)
    scene.update(1)

    assert scene.player.position.x == 0
    assert scene.player.position.y == 0
    assert scene.player.velocity.y == 0


def test_player_begins_on_start_and_can_reach_finish() -> None:
    scene = PlayScene()
    room = scene.environment
    start_x, start_y = room.start
    finish_x, finish_y = room.finish

    at_start = room.rows(0, 0)
    assert at_start[start_y][start_x] == "@"
    assert at_start[finish_y][finish_x] == "F"
    assert scene.reached_finish() is False

    scene.handle_input([Command.RIGHT])
    scene.update(1)
    left_start = room.rows(scene.player.position.x, scene.player.position.y)
    assert left_start[start_y][start_x] == "S"

    scene.player.position.x = finish_x - start_x
    scene.player.position.y = start_y - finish_y
    assert scene.reached_finish() is True
    assert scene.is_complete() is False


def test_collecting_the_key_and_reaching_the_end_completes_the_level() -> None:
    scene = PlayScene()
    room = scene.environment
    key_x, key_y = room.key
    start_x, start_y = room.start
    finish_x, finish_y = room.finish

    assert room.rows(0, 0)[key_y][key_x] == "K"
    assert scene.has_key is False

    scene.player.position.x = key_x - start_x
    scene.player.position.y = start_y - key_y
    scene.handle_input([])
    scene.update(1)

    assert scene.has_key is True
    assert room.rows(scene.player.position.x, scene.player.position.y, True)[key_y][key_x] == "@"

    scene.player.position.x = finish_x - start_x
    scene.player.position.y = start_y - finish_y
    scene.handle_input([])
    scene.update(1)

    assert scene.reached_finish() is True
    assert scene.is_complete() is True


def test_the_gate_blocks_walking_and_spikes_send_the_player_back() -> None:
    scene = PlayScene()
    room = scene.environment
    start_x, start_y = room.start

    assert room.rows(0, 0)[9][14] == "#"
    assert room.rows(0, 0)[10][14] == "#"
    assert room.rows(0, 0)[start_y][17] == "^"

    scene.player.position.x = 14 - start_x - 1
    scene.handle_input([Command.RIGHT])
    scene.update(1)
    assert scene.player.position.x == 14 - start_x - 1

    scene.has_key = True
    scene.player.position.x = 17 - start_x
    scene.player.position.y = start_y - start_y
    scene.handle_input([])
    scene.update(1)

    assert scene.player.position.x == 0
    assert scene.player.position.y == 0
    assert scene.has_key is False
    assert scene.player.facing == "right"
