"""A side-view level the player walks and jumps through."""

from __future__ import annotations


class Environment:
    """Ground, bricks, a key, a start, and a finish, shown through a camera."""

    view_width = 21
    view_height = 12

    def __init__(self) -> None:
        self._rows = _level()
        self.height = len(self._rows)
        self.width = len(self._rows[0])
        self.start = _find(self._rows, "S")
        self.finish = _find(self._rows, "F")
        self.key = _find(self._rows, "K")

    def tile_for(self, x: float, y: float) -> tuple[int, int]:
        """Map world coordinates onto a tile. The start is (0, 0)."""
        start_x, start_y = self.start
        return (start_x + int(x), start_y - int(y))

    def is_open(self, x: float, y: float) -> bool:
        """Return True when the player can occupy these world coordinates."""
        tile_x, tile_y = self.tile_for(x, y)
        if tile_x < 0 or tile_y < 0 or tile_x >= self.width or tile_y >= self.height:
            return False
        return self._rows[tile_y][tile_x] != "#"

    def is_hazard(self, x: float, y: float) -> bool:
        """Return True when this tile hurts the player."""
        tile_x, tile_y = self.tile_for(x, y)
        if tile_x < 0 or tile_y < 0 or tile_x >= self.width or tile_y >= self.height:
            return False
        return self._rows[tile_y][tile_x] == "^"

    def rows(self, x: float, y: float, key_collected: bool = False) -> tuple[str, ...]:
        """Draw the whole level with the player marked at ``x``, ``y``."""
        player = self.tile_for(x, y)
        drawn = []
        for tile_y, row in enumerate(self._rows):
            cells = []
            for tile_x, cell in enumerate(row):
                if (tile_x, tile_y) == player:
                    cells.append("@")
                elif cell == "K" and key_collected:
                    cells.append(" ")
                else:
                    cells.append(" " if cell == "." else cell)
            drawn.append("".join(cells))
        return tuple(drawn)

    def view_rows(
        self, x: float, y: float, key_collected: bool = False
    ) -> tuple[str, ...]:
        """Draw the camera window around the player."""
        full = self.rows(x, y, key_collected)
        player_x, _ = self.tile_for(x, y)
        left = player_x - self.view_width // 2
        left = max(0, min(left, self.width - self.view_width))
        return tuple(row[left : left + self.view_width] for row in full)


def _level() -> tuple[str, ...]:
    width = 40
    height = 12
    rows = [["." for _ in range(width)] for _ in range(height)]
    for y in range(height):
        rows[y][0] = "#"
        rows[y][width - 1] = "#"
    for x in range(width):
        rows[height - 1][x] = "#"
    for x in range(8, 12):
        rows[7][x] = "#"
    rows[6][10] = "K"
    for x in range(18, 24):
        rows[6][x] = "#"
    for x in range(28, 33):
        rows[7][x] = "#"
    for x in range(14, 15):
        rows[10][x] = "#"
        rows[9][x] = "#"
    for x in range(17, 20):
        rows[10][x] = "^"
    rows[10][2] = "S"
    rows[10][36] = "F"
    return tuple("".join(row) for row in rows)


def _find(rows: tuple[str, ...], marker: str) -> tuple[int, int]:
    for y, row in enumerate(rows):
        x = row.find(marker)
        if x != -1:
            return (x, y)
    raise ValueError(f"level is missing {marker}")
