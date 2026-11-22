import re

from game.theme import GATE, MEADOW, paint, palette_for


def test_each_gate_has_its_own_palette() -> None:
    assert palette_for("play", 1).name == "MEADOW"
    assert palette_for("play", 2).name == "KILN"
    assert palette_for("play", 3).name == "NIGHT"
    assert palette_for("start", 1) is GATE
    assert palette_for("gameover", 1).name == "ASH"


def test_paint_colors_the_frame_and_keeps_the_glyphs() -> None:
    picture = "\n".join(
        [
            "╭───╮",
            "│#@ │",
            "╰───╯",
        ]
    )

    painted = paint(picture, MEADOW)

    assert "\033[" in painted
    assert re.sub(r"\033\[[0-9;]*m", "", painted) == picture
