"""Daemon soul terminal colors. The level glyphs stay the same."""

from __future__ import annotations

from dataclasses import dataclass

_RESET = "\033[0m"


@dataclass(frozen=True)
class Palette:
    """Colors for one gate."""

    name: str
    brick: str
    hazard: str
    pit: str
    coin: str
    key: str
    door: str
    player: str
    enemy: str
    shield: str
    sky: str
    chrome: str
    text: str


def _pen(color: int, bold: bool = False) -> str:
    weight = "1;" if bold else ""
    return f"{weight}38;5;{color}"


MEADOW = Palette(
    name="MEADOW",
    brick=_pen(28),
    hazard=_pen(160, True),
    pit=_pen(23),
    coin=_pen(220, True),
    key=_pen(214, True),
    door=_pen(46, True),
    player=_pen(231, True),
    enemy=_pen(126, True),
    shield=_pen(123, True),
    sky=_pen(23),
    chrome=_pen(108),
    text=_pen(194),
)
KILN = Palette(
    name="KILN",
    brick=_pen(172),
    hazard=_pen(160, True),
    pit=_pen(94),
    coin=_pen(221, True),
    key=_pen(214, True),
    door=_pen(220, True),
    player=_pen(230, True),
    enemy=_pen(166, True),
    shield=_pen(123, True),
    sky=_pen(94),
    chrome=_pen(173),
    text=_pen(223),
)
NIGHT = Palette(
    name="NIGHT",
    brick=_pen(60),
    hazard=_pen(203, True),
    pit=_pen(17),
    coin=_pen(159, True),
    key=_pen(229, True),
    door=_pen(111, True),
    player=_pen(195, True),
    enemy=_pen(141, True),
    shield=_pen(159, True),
    sky=_pen(17),
    chrome=_pen(111),
    text=_pen(153),
)
GATE = Palette(
    name="DAEMON SOUL",
    brick=_pen(180),
    hazard=_pen(131),
    pit=_pen(95),
    coin=_pen(220, True),
    key=_pen(220, True),
    door=_pen(180),
    player=_pen(230, True),
    enemy=_pen(131),
    shield=_pen(180),
    sky=_pen(95),
    chrome=_pen(180),
    text=_pen(223),
)
ASH = Palette(
    name="ASH",
    brick=_pen(95),
    hazard=_pen(131, True),
    pit=_pen(52),
    coin=_pen(131),
    key=_pen(131),
    door=_pen(95),
    player=_pen(224, True),
    enemy=_pen(131),
    shield=_pen(131),
    sky=_pen(52),
    chrome=_pen(131),
    text=_pen(224),
)

PLACES = {1: MEADOW, 2: KILN, 3: NIGHT}
_CHROME = set("╭╮╰╯│─")
_GLYPHS = {
    "#": "brick",
    "^": "hazard",
    "v": "pit",
    "o": "coin",
    "K": "key",
    "F": "door",
    "S": "door",
    "@": "player",
    "E": "enemy",
    "+": "shield",
    "(": "shield",
    ")": "shield",
}


def palette_for(mode: str, level: int) -> Palette:
    """Pick the gate colors for the screen that is showing."""
    if mode == "play":
        return PLACES.get(level, MEADOW)
    if mode == "gameover":
        return ASH
    if mode == "win":
        return KILN
    return GATE


def paint(picture: str, palette: Palette) -> str:
    """Color a bordered frame without changing its glyphs."""
    return "\n".join(_paint_line(line, palette) for line in picture.split("\n"))


def paint_line(text: str, palette: Palette) -> str:
    """Color one status or control line."""
    return _paint_line(text, palette)


def _paint_line(line: str, palette: Palette) -> str:
    textured = _texture(line)
    parts: list[str] = []
    index = 0
    while index < len(textured):
        style = _style(textured[index], palette)
        end = index + 1
        while end < len(textured) and _style(textured[end], palette) == style:
            end += 1
        chunk = textured[index:end]
        parts.append(chunk if style == "" else f"\033[{style}m{chunk}{_RESET}")
        index = end
    return "".join(parts)


def _texture(line: str) -> str:
    """Fill wide gaps with sky marks and leave single spaces between words."""
    pieces: list[str] = []
    index = 0
    while index < len(line):
        if line[index] != " ":
            pieces.append(line[index])
            index += 1
            continue
        end = index + 1
        while end < len(line) and line[end] == " ":
            end += 1
        pieces.append("·" * (end - index) if end - index >= 2 else " ")
        index = end
    return "".join(pieces)


def _style(char: str, palette: Palette) -> str:
    if char in _CHROME or char == "·":
        return palette.chrome if char in _CHROME else palette.sky
    field = _GLYPHS.get(char)
    if field is None:
        return palette.text
    return getattr(palette, field)
