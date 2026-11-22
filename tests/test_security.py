import re
from pathlib import Path

import pytest

from game.environment import Environment
from game.input.command import Command, commands_from_names, parse_command
from game.markup import ansi_to_html
from game.scenes import PlayScene
from game.session import GameSession

_PAGE = Path(__file__).parents[1] / "index.html"
_PLAY = Path(__file__).parents[1] / "play.js"
_PAYLOAD = '<img src=x onerror="alert(1)">'


def test_markup_is_shown_as_text_not_html() -> None:
    html = ansi_to_html(_PAYLOAD)

    assert "<img" not in html
    assert "<script" not in html
    assert "&lt;img" in html
    assert "&quot;" in html
    assert 'onerror="' not in html


def test_a_hostile_color_code_cannot_set_a_style() -> None:
    html = ansi_to_html("\033[0;background:url(javascript:alert(1))mX")

    assert "javascript" not in html
    assert "background" not in html
    assert "X" in html


def test_a_known_palette_color_still_renders() -> None:
    html = ansi_to_html("\033[1;38;5;231m@\033[0m")

    assert 'style="font-weight:700;color:#ffffff;"' in html
    assert "@" in html


def test_command_names_keep_only_known_controls() -> None:
    commands = commands_from_names(
        ["RIGHT", "banana", "<script>", "", 12, None, "UP", "RIGHT"]
    )

    assert commands == [Command.RIGHT, Command.UP, Command.RIGHT]


def test_a_string_is_not_read_as_a_list_of_commands() -> None:
    assert commands_from_names("RIGHT") == []
    assert commands_from_names(None) == []
    assert parse_command(12) is None
    assert parse_command("banana") is None


@pytest.mark.parametrize("level", [-100, 0, 4, 10**12, "banana"])
def test_a_level_outside_the_three_gates_is_rejected(level) -> None:
    with pytest.raises(ValueError):
        Environment(level)
    session = GameSession()
    with pytest.raises(ValueError):
        session._begin_level(level, 0, 3)


@pytest.mark.parametrize(
    ("score", "lives", "shield"),
    [(-1, 3, False), (10**7, 3, False), ("100", 3, False), (0, -1, False), (0, 9, False), (0, True, False), (0, 3, "yes")],
)
def test_score_lives_and_shield_outside_range_are_rejected(score, lives, shield) -> None:
    session = GameSession()
    with pytest.raises(ValueError):
        session._begin_level(1, score, lives, shield)


def test_a_normal_level_start_still_works() -> None:
    session = GameSession()
    session._begin_level(2, 100, 2, True)

    assert session.level == 2
    assert session.play is not None
    assert session.play.score == 100
    assert session.play.lives == 2
    assert session.play.shield is True


def test_the_page_does_not_fetch_outside_the_game_package() -> None:
    text = _PLAY.read_text()
    paths = re.findall(r'"(src/game/[^"]+)"', text)

    assert paths
    assert all(".." not in path and path.startswith("src/game/") for path in paths)
    assert "src/game/input/keyboard.py" not in paths


def test_the_page_does_not_print_exception_text_and_pins_the_loader() -> None:
    page = _PAGE.read_text()
    play = _PLAY.read_text()

    assert "error.message" not in play
    assert "<script>" not in page
    assert "integrity=\"sha384-" in page
    assert "Content-Security-Policy" in page
    assert 'src="play.js"' in page


def test_play_still_moves_after_the_checks() -> None:
    scene = PlayScene()
    scene.handle_input(commands_from_names(["RIGHT", "UP"]))
    scene.update(1)

    assert scene.player.position.x == 1
    assert scene.player.position.y == 3
