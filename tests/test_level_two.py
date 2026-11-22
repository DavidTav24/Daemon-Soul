from collections import deque

import pytest

from game.entities.entity import Vec2
from game.environment import Environment
from game.input import Command
from game.scenes import PlayScene


def test_level_two_is_a_climb_to_a_locked_door() -> None:
    room = Environment(2)

    assert room.level == 2
    assert (room.width, room.height) == (48, 12)
    assert room.start == (2, 10)
    assert room.key == (22, 6)
    assert room.door == ((44, 9), (44, 10))
    assert room.rows(0, 0)[11][8:12] == "vvvv"
    assert room.rows(0, 0)[10][15:18] == "^^^"
    assert room.rows(0, 0)[9][19] == "#"
    assert room.rows(0, 0)[8][20] == "^"
    assert room.rows(0, 0)[7][27] == "^"
    assert room.rows(0, 0)[10][32:37] == "^^^^^"
    assert room.rows(0, 0)[10][42:44] == "^^"
    assert room.rows(0, 0)[10][12] == "E"
    assert room.enemy_tiles() == ((12, 10),)
    assert room.coins == (
        (4, 4),
        (20, 6),
        (31, 7),
        (17, 8),
        (7, 10),
        (46, 10),
    )
    assert _hazard_tiles(2) > _hazard_tiles(1)


def _hazard_tiles(level: int) -> int:
    return sum(
        cell in {"^", "v"}
        for row in Environment(level).rows(0, 0)
        for cell in row
    )


def test_the_walker_moves_on_every_other_frame() -> None:
    scene = PlayScene(level=2)

    scene.handle_input([])
    scene.update(1)
    assert scene.environment.enemy_tiles() == ((12, 10),)

    scene.handle_input([])
    scene.update(1)
    assert scene.environment.enemy_tiles() == ((13, 10),)


def test_landing_on_the_walker_removes_it() -> None:
    scene = PlayScene(level=2)
    start_x, _ = scene.environment.start
    scene.player.position.x = 12 - start_x
    scene.player.position.y = 1
    scene.player.velocity.y = -1

    scene.handle_input([])
    scene.update(1)

    assert scene.lives == 3
    assert scene.player.position.y == 0
    assert scene.environment.enemy_tiles() == ()


def test_the_walker_hurts_on_contact_and_can_be_jumped() -> None:
    room = Environment(2)
    room.step_enemies()
    assert room.enemy_tiles() == ((13, 10),)
    room.step_enemies()
    assert room.enemy_tiles() == ((14, 10),)
    room.step_enemies()
    assert room.enemy_tiles() == ((13, 10),)

    scene = PlayScene(level=2)
    start_x, _ = scene.environment.start
    scene.player.position.x = 12 - start_x
    scene.handle_input([])
    scene.update(1)
    assert scene.lives == 2
    assert scene.player.position.x == 0
    assert scene.environment.enemy_tiles() == ((12, 10),)

    scene = PlayScene(level=2)
    scene.player.position.x = 7 - start_x
    scene.handle_input([Command.UP])
    scene.update(1)
    for _ in range(5):
        scene.handle_input([Command.RIGHT])
        scene.update(1)
    assert scene.lives == 3
    assert scene.player.position.y > 0
    assert scene.environment.tile_for(scene.player.position.x, scene.player.position.y)[0] == 12


def test_level_two_can_be_finished_without_losing_a_life() -> None:
    scene = PlayScene(level=2)
    actions = {
        "": [],
        "L": [Command.LEFT],
        "R": [Command.RIGHT],
        "U": [Command.UP],
        "LU": [Command.LEFT, Command.UP],
        "RU": [Command.RIGHT, Command.UP],
    }
    start = _snapshot(scene)
    queue = deque([start])
    seen = {start}

    while queue:
        x, y, vy, has_key, tick, enemies = queue.popleft()
        for commands in actions.values():
            _restore(scene, x, y, vy, has_key, tick, enemies)
            scene.handle_input(commands)
            scene.update(1)
            if scene.is_complete() and scene.lives == 3:
                return
            if scene.lives < 3:
                continue
            nxt = _snapshot(scene)
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)

    raise AssertionError("level 2 has no safe path to the door")


def test_an_unknown_level_is_rejected() -> None:
    with pytest.raises(ValueError):
        Environment(4)


def _snapshot(scene: PlayScene) -> tuple:
    return (
        scene.player.position.x,
        scene.player.position.y,
        scene.player.velocity.y,
        scene.has_key,
        scene._enemy_tick,
        scene.environment.enemy_state(),
    )


def _restore(
    scene: PlayScene,
    x: float,
    y: float,
    vy: float,
    has_key: bool,
    tick: int,
    enemies: tuple,
) -> None:
    scene.player.position.x = x
    scene.player.position.y = y
    scene.player.velocity = Vec2(0, vy)
    scene.player.facing = "right"
    scene.has_key = has_key
    scene.lives = 3
    scene._game_over = False
    scene.collected_coins.clear()
    scene.score = 0
    scene._jump_pressed = False
    scene._respawn_wait = 0
    scene._enemy_tick = tick
    scene.environment.restore_enemies(enemies)
