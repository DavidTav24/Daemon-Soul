from game.input.command import Command
from game.render import FrameRenderer
from game.session import GameSession


def test_start_begins_level_one() -> None:
    session = GameSession()

    session.step([Command.START])

    assert session.mode == "play"
    assert session.level == 1
    assert session.play is not None
    assert session.play.lives == 3


def test_finishing_a_level_opens_the_next_one_and_keeps_the_score() -> None:
    session = GameSession()
    session.step([Command.START])
    scene = session.play
    assert scene is not None
    scene.score = 100
    scene.has_key = True
    finish_x, finish_y = scene.environment.finish
    start_x, start_y = scene.environment.start
    scene.player.position.x = finish_x - start_x
    scene.player.position.y = start_y - finish_y

    session.step([])

    assert session.mode == "play"
    assert session.level == 2
    assert session.play is not None
    assert session.play.score == 100
    assert session.play.lives == 3


def test_a_shield_from_level_two_is_brought_into_level_three() -> None:
    session = GameSession()
    session.step([Command.START])
    session.level = 2
    from game.scenes import PlayScene

    scene = PlayScene(level=2)
    scene.shield = True
    scene.has_key = True
    scene.score = 100
    finish_x, finish_y = scene.environment.finish
    start_x, start_y = scene.environment.start
    scene.player.position.x = finish_x - start_x
    scene.player.position.y = start_y - finish_y
    session.play = scene

    session.step([])

    assert session.level == 3
    assert session.play is not None
    assert session.play.shield is True
    assert "SHIELD" in session.status_line()
    picture = session.play.environment.rows(0, 0, shielded=session.play.shield)
    assert "(@)" in picture[10]


def test_finishing_level_three_wins() -> None:
    session = GameSession()
    session.step([Command.START])
    session.level = 3
    from game.scenes import PlayScene

    scene = PlayScene(level=3)
    scene.has_key = True
    scene.score = 200
    finish_x, finish_y = scene.environment.finish
    start_x, start_y = scene.environment.start
    scene.player.position.x = finish_x - start_x
    scene.player.position.y = start_y - finish_y
    session.play = scene

    session.step([])

    assert session.mode == "win"
    assert session.score == 200
    renderer = FrameRenderer()
    session.render(renderer)
    renderer.present()
    assert renderer.frames[0][4].strip() == "YOU WIN"


def test_losing_the_last_life_opens_game_over_and_start_tries_again() -> None:
    session = GameSession()
    session.step([Command.START])
    scene = session.play
    assert scene is not None
    start_x, _ = scene.environment.start
    scene.lives = 1
    scene.player.velocity.y = 0
    scene.player.position.x = 34 - start_x
    scene.player.position.y = 0

    session.step([])

    assert session.mode == "gameover"
    session.step([Command.START])
    assert session.mode == "play"
    assert session.level == 1
    assert session.play is not None
    assert session.play.lives == 3
    assert session.play.score == 0


def test_quit_on_the_start_screen_ends_the_session() -> None:
    session = GameSession()

    session.step([Command.QUIT])

    assert session.running is False
