from collections import deque

from game.entities.entity import Vec2
from game.environment import Environment
from game.input import Command
from game.scenes import PlayScene


def test_level_three_is_the_hardest_layout() -> None:
    room = Environment(3)

    assert room.level == 3
    assert (room.width, room.height) == (56, 12)
    assert room.start == (2, 10)
    assert room.key == (27, 6)
    assert room.door == ((52, 9), (52, 10))
    assert room.enemy_tiles() == ((6, 10), (46, 10))
    assert room.rows(0, 0)[11][9:14] == "vvvvv"
    assert room.rows(0, 0)[7][36:39] == "   "
    assert room.rows(0, 0)[10][39:46] == " ^^  o "
    assert room.coins == (
        (27, 3),
        (21, 5),
        (29, 6),
        (3, 7),
        (20, 8),
        (44, 10),
        (54, 10),
    )
    assert _hazard_tiles(2) > _hazard_tiles(1)


def test_level_three_can_be_finished_without_losing_a_life() -> None:
    scene = PlayScene(level=3)
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

    raise AssertionError("level 3 has no safe path to the door")


def _hazard_tiles(level: int) -> int:
    return sum(
        cell in {"^", "v"}
        for row in Environment(level).rows(0, 0)
        for cell in row
    )


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
