from game.environment import Environment
from game.input import Command
from game.render.renderer import FrameRenderer
from game.scenes import PlayScene


def test_play_scene_moves_player_from_directions() -> None:
    scene = PlayScene()

    scene.handle_input([Command.RIGHT, Command.UP])
    scene.update(1)

    assert scene.player.position.x == 1
    assert scene.player.position.y == 3
    assert scene.is_done() is False


def test_the_player_stops_on_the_ground_when_there_is_no_input() -> None:
    scene = PlayScene()
    scene.handle_input([Command.RIGHT])
    scene.update(1)

    scene.handle_input([])
    scene.update(1)

    assert scene.player.position.x == 1
    assert scene.player.position.y == 0
    assert scene.player.velocity.x == 0


def test_the_player_can_steer_while_jumping() -> None:
    scene = PlayScene()
    scene.handle_input([Command.UP])
    scene.update(1)
    assert scene.player.position.x == 0
    assert scene.player.position.y == 3

    scene.handle_input([Command.RIGHT])
    scene.update(1)

    assert scene.player.position.x == 1
    assert scene.player.position.y > 3

    scene.handle_input([Command.LEFT])
    scene.update(1)

    assert scene.player.position.x == 0
    assert scene.player.position.y > 3


def test_jump_and_move_together_leave_the_edge_of_a_platform() -> None:
    scene = PlayScene()
    scene.player.position.x = 19
    scene.player.position.y = 2

    scene.handle_input([Command.RIGHT, Command.UP])
    scene.update(1)

    assert scene.player.position.x == 20
    assert scene.player.position.y > 2


def test_jumping_while_moving_follows_an_arc() -> None:
    scene = PlayScene()
    scene.handle_input([Command.RIGHT, Command.UP])
    scene.update(1)

    path = [(scene.player.position.x, scene.player.position.y)]
    while scene.player.position.y > 0:
        scene.handle_input([])
        scene.update(1)
        path.append((scene.player.position.x, scene.player.position.y))

    heights = [y for _, y in path]
    assert heights[-1] == 0
    assert max(heights) > heights[0]
    assert all(path[i + 1][0] - path[i][0] == scene.walk_speed for i in range(len(path) - 1))


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


def test_pause_freezes_the_level_until_pause_again() -> None:
    scene = PlayScene()
    scene.handle_input([Command.RIGHT])
    scene.update(1)

    scene.handle_input([Command.PAUSE, Command.RIGHT])
    scene.update(1)

    assert scene.is_paused() is True
    assert scene.player.position.x == 1
    assert scene.player.position.y == 0

    scene.handle_input([Command.PAUSE])
    scene.handle_input([Command.RIGHT])
    scene.update(1)

    assert scene.is_paused() is False
    assert scene.player.position.x == 2


def test_a_shield_absorbs_the_next_hit() -> None:
    assert Environment(1).shields == ()
    assert Environment(3).shields == ()

    scene = PlayScene(level=2)
    start_x, _ = scene.environment.start
    room = scene.environment

    assert room.shields == ((4, 10),)
    assert room.rows(0, 0)[10][4] == "+"

    scene.player.position.x = 4 - start_x
    scene.handle_input([])
    scene.update(1)

    assert scene.shield is True
    assert scene.lives == 3
    assert room.rows(0, 0, shields_collected=scene.collected_shields)[10][4] == " "
    picture = room.rows(
        scene.player.position.x,
        scene.player.position.y,
        shields_collected=scene.collected_shields,
        shielded=True,
    )
    assert "(@)" in picture[10]

    scene.has_key = True
    scene.score = 100
    scene.collected_coins.add((7, 10))
    scene.player.velocity.y = 0
    scene.player.position.x = 15 - start_x
    scene.player.position.y = 0
    scene.handle_input([])
    scene.update(1)

    assert scene.lives == 3
    assert scene.shield is False
    assert scene.is_game_over() is False
    assert scene.has_key is True
    assert scene.score == 100
    assert scene.player.position.x == 15 - start_x
    assert room.rows(0, 0, shields_collected=scene.collected_shields)[10][4] == " "

    for _ in range(PlayScene.invincible_frames - 1):
        scene.handle_input([])
        scene.update(1)
        assert scene.lives == 3
        assert scene.player.position.x == 15 - start_x

    scene.handle_input([])
    scene.update(1)

    assert scene.lives == 2
    assert scene.has_key is False
    assert scene.score == 0
    assert scene.player.position.x == 0
    assert room.rows(0, 0)[10][4] == "+"


def test_the_player_flashes_after_taking_damage() -> None:
    scene = PlayScene(level=2)
    scene.shield = True
    scene.player.position.x = 15 - scene.environment.start[0]
    scene.player.position.y = 0
    scene.handle_input([])
    scene.update(1)

    hidden = _player_glyph(scene)
    scene.handle_input([])
    scene.update(1)
    shown = _player_glyph(scene)

    assert hidden == "^"
    assert shown == "@"
    assert scene.lives == 3


def _player_glyph(scene: PlayScene) -> str:
    renderer = FrameRenderer()
    scene.render(renderer)
    tile_x, tile_y = scene.environment.tile_for(
        scene.player.position.x, scene.player.position.y
    )
    left = tile_x - scene.environment.view_width // 2
    left = max(0, min(left, scene.environment.width - scene.environment.view_width))
    return renderer._lines[tile_y][tile_x - left]


def test_the_next_life_waits_before_the_player_can_move() -> None:
    scene = PlayScene()
    start_x, _ = scene.environment.start
    scene.player.velocity.y = 0
    scene.player.position.x = 34 - start_x
    scene.player.position.y = 0
    scene.handle_input([])
    scene.update(1)

    assert scene.lives == 2
    for _ in range(PlayScene.respawn_delay):
        scene.handle_input([Command.RIGHT, Command.UP])
        scene.update(1)
        assert scene.player.position.x == 0
        assert scene.player.position.y == 0

    scene.handle_input([Command.RIGHT])
    scene.update(1)
    assert scene.player.position.x == 1


def test_restart_from_pause_resets_the_level_and_keeps_lives() -> None:
    scene = PlayScene(level=2)
    start_x, _ = scene.environment.start

    scene.player.velocity.y = 0
    scene.player.position.x = 15 - start_x
    scene.player.position.y = 0
    scene.handle_input([])
    scene.update(1)
    assert scene.lives == 2

    scene._respawn_wait = 0
    scene.player.velocity.y = 0
    scene.player.position.x = 7 - start_x
    scene.player.position.y = 0
    scene.handle_input([])
    scene.update(1)
    scene.handle_input([])
    scene.update(1)
    assert scene.score == 100
    assert scene.environment.enemy_tiles() == ((13, 10),)

    scene.player.position.x = 4 - start_x
    scene.has_key = True
    scene.handle_input([Command.RESTART])
    scene.update(1)
    assert scene.is_paused() is False
    assert scene.player.position.x == 4 - start_x
    assert scene.score == 100
    assert scene.has_key is True

    scene.handle_input([Command.PAUSE])
    scene.handle_input([Command.RESTART])

    assert scene.is_paused() is False
    assert scene.player.position.x == 0
    assert scene.player.position.y == 0
    assert scene.has_key is False
    assert scene.score == 0
    assert scene.collected_coins == set()
    assert scene.lives == 2
    assert scene.environment.enemy_tiles() == ((12, 10),)
