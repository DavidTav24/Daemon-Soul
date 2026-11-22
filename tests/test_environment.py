from game.environment import Environment
from game.input import Command
from game.scenes import PlayScene


def test_level_is_a_side_view_with_start_and_finish() -> None:
    room = Environment()

    assert room.width == 40
    assert room.height == 12
    rows = room.rows(0, 0)
    assert rows[11][26:30] == "vvvv"
    assert rows[11].count("#") == 36
    assert rows[10][2] == "@"
    assert rows[10][38] == "F"
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


def test_coins_score_points_and_spikes_spend_lives() -> None:
    scene = PlayScene()
    room = scene.environment
    start_x, start_y = room.start
    key_x, key_y = room.key

    assert scene.score == 0
    assert scene.lives == 3
    assert scene.is_game_over() is False

    scene.player.position.x = key_x - start_x
    scene.player.position.y = start_y - key_y
    scene.handle_input([])
    scene.update(1)
    assert scene.has_key is True
    assert scene.score == 0

    scene.player.velocity.y = 0
    scene.player.position.x = 5 - start_x
    scene.player.position.y = 0
    scene.handle_input([])
    scene.update(1)
    assert scene.score == 100

    scene.handle_input([])
    scene.update(1)
    assert scene.score == 100

    for lives_left in (2, 1, 0):
        scene._respawn_wait = 0
        scene.player.velocity.y = 0
        scene.player.position.x = 34 - start_x
        scene.player.position.y = 0
        scene.handle_input([])
        scene.update(1)
        assert scene.score == 0
        assert scene.lives == lives_left
        assert scene.player.position.x == 0

    assert scene.is_game_over() is True
    scene.handle_input([Command.RIGHT])
    scene.update(1)
    assert scene.player.position.x == 0


def test_bronze_coins_are_collected_by_standing_on_them() -> None:
    scene = PlayScene()
    room = scene.environment
    start_x, start_y = room.start

    assert room.coins == (
        (18, 5),
        (19, 8),
        (5, 10),
        (31, 10),
        (37, 10),
    )
    assert room.rows(0, 0)[10][5] == "o"

    scene.player.position.x = 5 - start_x
    scene.handle_input([])
    scene.update(1)
    assert (5, 10) in scene.collected_coins
    assert room.rows(0, 0, coins_collected=scene.collected_coins)[10][5] == " "

    scene.player.velocity.y = 0
    scene.player.position.x = 18 - start_x
    scene.player.position.y = start_y - 8
    scene.handle_input([Command.UP])
    scene.update(1)
    assert scene.player.position.y == start_y - 5
    assert (18, 5) in scene.collected_coins

    scene.player.velocity.y = 0
    scene.player.position.x = 34 - start_x
    scene.player.position.y = 0
    scene.handle_input([])
    scene.update(1)
    assert scene.collected_coins == set()
    assert room.rows(0, 0)[10][5] == "o"
    assert scene.is_complete() is False


def test_the_door_stays_locked_until_the_player_has_the_key() -> None:
    scene = PlayScene()
    room = scene.environment
    start_x, start_y = room.start
    door_x, door_y = room.finish
    world_x = door_x - start_x
    world_y = start_y - door_y

    assert room.door == ((door_x, door_y - 1), (door_x, door_y))
    assert room.rows(0, 0)[door_y][door_x] == "F"
    assert room.rows(0, 0)[door_y - 1][door_x] == "F"
    assert room.is_open(world_x, world_y) is False
    assert room.is_open(world_x, world_y, door_unlocked=True) is True

    scene.player.position.x = world_x - 1
    scene.handle_input([Command.RIGHT])
    scene.update(1)
    assert scene.player.position.x == world_x - 1
    assert scene.is_complete() is False

    scene.has_key = True
    scene.handle_input([Command.RIGHT])
    scene.update(1)
    assert scene.reached_finish() is True
    assert scene.is_complete() is True


def test_the_pit_and_spikes_cost_a_life() -> None:
    scene = PlayScene()
    room = scene.environment
    start_x, _ = room.start

    assert room.rows(0, 0)[10][34] == "^"
    assert room.rows(0, 0)[11][26:30] == "vvvv"
    assert room.is_hazard(26 - start_x, -1) is True

    scene.player.position.x = 26 - start_x
    scene.handle_input([])
    scene.update(1)
    assert scene.lives == 3
    assert scene.player.position.y == -1

    scene.handle_input([])
    scene.update(1)
    assert scene.lives == 2
    assert scene.player.position.x == 0
    assert scene.player.position.y == 0

    scene._respawn_wait = 0
    scene.player.velocity.y = 0
    scene.player.position.x = 34 - start_x
    scene.player.position.y = 0
    scene.handle_input([])
    scene.update(1)
    assert scene.lives == 1
    assert scene.player.position.x == 0
    assert scene.has_key is False


def test_rising_through_a_pit_does_not_cost_a_life() -> None:
    scene = PlayScene()
    room = scene.environment
    rows = [list(row) for row in room._rows]
    rows[9][10] = "v"
    room._rows = tuple("".join(row) for row in rows)
    scene.player.position.x = 8
    scene.player.position.y = 0
    scene.player.velocity.y = 2

    scene.handle_input([])
    scene.update(1)

    assert scene.environment.terrain_at(scene.player.position.x, scene.player.position.y) == "v"
    assert scene.lives == 3


def test_the_lip_of_a_pit_can_be_climbed_out_of() -> None:
    scene = PlayScene()
    start_x, _ = scene.environment.start
    scene.player.position.x = 26 - start_x
    scene.player.position.y = -1
    scene.player.velocity.y = 0

    scene.handle_input([Command.LEFT])
    scene.update(1)

    assert scene.lives == 3
    assert scene.player.position.y == 0


def test_spikes_send_the_player_back() -> None:
    scene = PlayScene()
    room = scene.environment
    start_x, start_y = room.start

    assert room.rows(0, 0)[9][15] == "#"
    assert room.rows(0, 0)[start_y][15] == " "
    assert room.rows(0, 0)[start_y][34] == "^"

    scene.has_key = True
    scene.player.position.x = 34 - start_x
    scene.player.position.y = start_y - start_y
    scene.handle_input([])
    scene.update(1)

    assert scene.player.position.x == 0
    assert scene.player.position.y == 0
    assert scene.has_key is False
    assert scene.player.facing == "right"


def test_each_level_can_be_crossed_on_the_high_road() -> None:
    routes = {
        1: ((15, 2), ["RU"] + ["R"] * 6 + ["RU"] + ["R"] * 6),
        2: ((21, 4), ["RU"] + ["R"] * 8 + ["RU"] + ["R"] * 6),
        3: ((26, 4), ["RU"] + ["R"] * 8 + ["RU"] + ["R"] * 6),
    }
    commands = {
        "R": [Command.RIGHT],
        "RU": [Command.RIGHT, Command.UP],
    }
    for level, ((x, y), script) in routes.items():
        scene = PlayScene(level=level)
        scene.has_key = True
        scene.player.position.x = x
        scene.player.position.y = y
        for name in script:
            scene.handle_input(commands[name])
            scene.update(1)
        assert scene.lives == 3
        assert scene.player.position.y == 5
