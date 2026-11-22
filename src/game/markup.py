"""Turn game text into HTML without letting it become markup."""

from __future__ import annotations

_COLORS = {
    17: "#00005f",
    23: "#005f5f",
    28: "#008700",
    46: "#00ff00",
    52: "#5f0000",
    60: "#5f5f87",
    94: "#875f00",
    95: "#875f5f",
    108: "#87af87",
    111: "#87afff",
    123: "#87ffff",
    126: "#af0087",
    131: "#af5f5f",
    141: "#af87ff",
    153: "#afd7ff",
    159: "#afffff",
    160: "#d70000",
    166: "#d75f00",
    172: "#d78700",
    173: "#d7875f",
    180: "#d7af87",
    194: "#d7ffd7",
    195: "#d7ffff",
    203: "#ff5f5f",
    214: "#ffaf00",
    220: "#ffd700",
    221: "#ffd75f",
    223: "#ffd7af",
    224: "#ffd7d7",
    229: "#ffffaf",
    230: "#ffffd7",
    231: "#ffffff",
}


def escape_text(text: str) -> str:
    """Encode characters that would otherwise open an HTML tag or attribute."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def ansi_to_html(text: str) -> str:
    """Color ANSI text with a fixed palette. Game text is escaped first."""
    parts = text.split("\033[")
    html = escape_text(parts[0])
    for part in parts[1:]:
        end = part.find("m")
        code = "" if end == -1 else part[:end]
        body = part if end == -1 else part[end + 1 :]
        style = _style(code) if end != -1 else ""
        escaped = escape_text(body)
        if style:
            html += f'<span style="{style}">{escaped}</span>'
        else:
            html += escaped
    return html


def _style(code: str) -> str:
    """Return a style only for a known palette color. Ignore every other code."""
    bold = code.startswith("1;")
    number = ""
    marker = "38;5;"
    start = code.find(marker)
    if start != -1:
        digits = code[start + len(marker) :]
        if digits.isdigit():
            number = digits
    color = _COLORS.get(int(number)) if number else None
    style = "font-weight:700;" if bold else ""
    if color:
        style += f"color:{color};"
    return style
