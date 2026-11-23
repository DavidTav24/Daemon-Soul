"""A side-view level the player walks and jumps through."""

from __future__ import annotations

from collections.abc import Collection

from game.entities.enemy import Enemy


class Environment:
    """Ground, bricks, a key, coins, a start, and a locked door."""

    view_width = 21
    view_height = 12

    def __init__(self, level: int = 1) -> None:
        self.level = level
        if level == 1:
            self._rows = _level_one()
        elif level == 2:
            self._rows = _level_two()
        elif level == 3:
            self._rows = _level_three()
        else:
            raise ValueError(f"unknown level {level}")
        self.height = len(self._rows)
        self.width = len(self._rows[0])
        self.start = _find(self._rows, "S")
        self.door = _find_all(self._rows, "F")
        self.finish = max(self.door, key=lambda tile: tile[1])
        self.key = _find(self._rows, "K")
        self.coins = _find_all(self._rows, "o")
        self.shields = _find_all(self._rows, "+")
        self.enemies = [Enemy(x, y) for x, y in _find_all(self._rows, "E")]

    def tile_for(self, x: float, y: float) -> tuple[int, int]:
        """Map world coordinates onto a tile. The start is (0, 0)."""
        start_x, start_y = self.start
        return (start_x + int(x), start_y - int(y))

    def is_open(self, x: float, y: float, door_unlocked: bool = False) -> bool:
        """Return True when the player can occupy these world coordinates."""
        tile_x, tile_y = self.tile_for(x, y)
        if tile_x < 0 or tile_y < 0 or tile_x >= self.width or tile_y >= self.height:
            return False
        if (tile_x, tile_y) in self.door:
            return door_unlocked
        return self._rows[tile_y][tile_x] != "#"

    def is_hazard(self, x: float, y: float) -> bool:
        """Return True when this tile is a spike or a pit."""
        return self.terrain_at(x, y) in {"^", "v"}

    def terrain_at(self, x: float, y: float) -> str | None:
        """Return the level character at these world coordinates."""
        tile_x, tile_y = self.tile_for(x, y)
        if tile_x < 0 or tile_y < 0 or tile_x >= self.width or tile_y >= self.height:
            return None
        return self._rows[tile_y][tile_x]

    def enemy_tiles(self) -> tuple[tuple[int, int], ...]:
        """Return the tile each walking enemy occupies."""
        return tuple(enemy.tile() for enemy in self.enemies if enemy.alive)

    def enemy_state(self) -> tuple[tuple[int, int, int, bool], ...]:
        """Return positions, facing, and whether each enemy is still walking."""
        return tuple(
            (enemy.x, enemy.y, enemy.direction, enemy.alive) for enemy in self.enemies
        )

    def restore_enemies(self, state: tuple[tuple[int, int, int, bool], ...]) -> None:
        for enemy, (x, y, direction, alive) in zip(self.enemies, state):
            enemy.x = x
            enemy.y = y
            enemy.direction = direction
            enemy.alive = alive

    def eliminate_at(self, tile: tuple[int, int]) -> None:
        """Remove the enemy standing on ``tile``."""
        for enemy in self.enemies:
            if enemy.alive and enemy.tile() == tile:
                enemy.alive = False

    def reset_enemies(self) -> None:
        for enemy in self.enemies:
            enemy.reset()

    def step_enemies(self) -> None:
        """Walk each enemy one tile along solid ground."""
        for enemy in self.enemies:
            enemy.step(self._can_patrol)

    def _can_patrol(self, x: int, y: int) -> bool:
        if x < 0 or y < 0 or x >= self.width or y + 1 >= self.height:
            return False
        if self._rows[y][x] in {"#", "^", "v", "F"}:
            return False
        return self._rows[y + 1][x] == "#"

    def rows(
        self,
        x: float,
        y: float,
        key_collected: bool = False,
        coins_collected: Collection[tuple[int, int]] | None = None,
        shields_collected: Collection[tuple[int, int]] | None = None,
        shielded: bool = False,
        blink: bool = False,
    ) -> tuple[str, ...]:
        """Draw the whole level with the player marked at ``x``, ``y``."""
        player = self.tile_for(x, y)
        taken = set(coins_collected or ())
        taken_shields = set(shields_collected or ())
        enemies = set(self.enemy_tiles())
        drawn = []
        for tile_y, row in enumerate(self._rows):
            cells = []
            for tile_x, cell in enumerate(row):
                if (tile_x, tile_y) == player and not blink:
                    cells.append("@")
                elif (tile_x, tile_y) in enemies:
                    cells.append("E")
                elif cell == "K" and key_collected:
                    cells.append(" ")
                elif cell == "o" and (tile_x, tile_y) in taken:
                    cells.append(" ")
                elif cell == "+" and (tile_x, tile_y) in taken_shields:
                    cells.append(" ")
                elif cell == "E":
                    cells.append(" ")
                else:
                    cells.append(" " if cell == "." else cell)
            if shielded and not blink and tile_y == player[1]:
                _draw_bubble(cells, player[0])
            drawn.append("".join(cells))
        return tuple(drawn)

    def view_rows(
        self,
        x: float,
        y: float,
        key_collected: bool = False,
        coins_collected: Collection[tuple[int, int]] | None = None,
        shields_collected: Collection[tuple[int, int]] | None = None,
        shielded: bool = False,
        blink: bool = False,
    ) -> tuple[str, ...]:
        """Draw the camera window around the player."""
        full = self.rows(
            x, y, key_collected, coins_collected, shields_collected, shielded, blink
        )
        player_x, _ = self.tile_for(x, y)
        left = player_x - self.view_width // 2
        left = max(0, min(left, self.width - self.view_width))
        return tuple(row[left : left + self.view_width] for row in full)


def _draw_bubble(cells: list[str], player_x: int) -> None:
    """Put parentheses around the player when the neighboring tiles are open."""
    if player_x - 1 >= 0 and cells[player_x - 1] == " ":
        cells[player_x - 1] = "("
    if player_x + 1 < len(cells) and cells[player_x + 1] == " ":
        cells[player_x + 1] = ")"


def _level_one() -> tuple[str, ...]:
    """Meadow. A low step over the pit, then a higher bridge over the spikes."""
    width = 40
    height = 12
    rows = [["." for _ in range(width)] for _ in range(height)]
    for y in range(height):
        rows[y][0] = "#"
        rows[y][width - 1] = "#"
    for x in range(width):
        rows[height - 1][x] = "#"
    rows[10][2] = "S"
    rows[10][5] = "o"
    for x in range(15, 22):
        rows[9][x] = "#"
    for x in range(27, 31):
        rows[8][x] = "#"
    for x in range(32, 38):
        rows[6][x] = "#"
    rows[8][17] = "K"
    rows[8][19] = "o"
    rows[5][18] = "o"
    for x in range(26, 30):
        rows[11][x] = "v"
    rows[10][31] = "o"
    rows[10][34] = "^"
    rows[10][35] = "^"
    rows[10][37] = "o"
    rows[9][38] = "F"
    rows[10][38] = "F"
    return tuple("".join(row) for row in rows)


def _level_two() -> tuple[str, ...]:
    """Climb to the key, then take the ground or the upper platforms."""
    width = 48
    height = 12
    rows = [["." for _ in range(width)] for _ in range(height)]
    for y in range(height):
        rows[y][0] = "#"
        rows[y][width - 1] = "#"
    for x in range(width):
        rows[height - 1][x] = "#"
    rows[10][2] = "S"
    rows[10][4] = "+"
    for x in range(8, 12):
        rows[11][x] = "v"
    rows[10][12] = "E"
    for x in range(15, 18):
        rows[10][x] = "^"
    for x in range(14, 18):
        rows[9][x] = "#"
    rows[10][19] = "#"
    rows[9][19] = "#"
    for x in range(20, 25):
        rows[7][x] = "#"
    for x in range(20, 23):
        rows[8][x] = "^"
    rows[6][22] = "K"
    for span in ((28, 34), (37, 42), (44, 46)):
        for x in range(*span):
            rows[6][x] = "#"
    for x in range(26, 29):
        rows[11][x] = "v"
    for x in range(27, 30):
        rows[7][x] = "^"
    for x in range(32, 37):
        rows[10][x] = "^"
    for x in range(40, 42):
        rows[11][x] = "v"
    for x in range(42, 44):
        rows[10][x] = "^"
    rows[9][44] = "F"
    rows[10][44] = "F"
    rows[4][4] = "o"
    rows[10][7] = "o"
    rows[8][17] = "o"
    rows[6][20] = "o"
    rows[7][31] = "o"
    rows[10][46] = "o"
    return tuple("".join(row) for row in rows)


def _level_three() -> tuple[str, ...]:
    """The final level: a low road and the upper platforms to the door."""
    width = 56
    height = 12
    rows = [["." for _ in range(width)] for _ in range(height)]
    for y in range(height):
        rows[y][0] = "#"
        rows[y][width - 1] = "#"
    for x in range(width):
        rows[height - 1][x] = "#"
    rows[10][2] = "S"
    rows[7][3] = "o"
    rows[10][4] = "^"
    rows[10][6] = "E"
    for x in range(9, 14):
        rows[11][x] = "v"
    for x in range(15, 18):
        rows[10][x] = "^"
    for x in range(18, 22):
        rows[9][x] = "#"
    for x in range(19, 22):
        rows[10][x] = "^"
    rows[8][20] = "o"
    rows[5][21] = "o"
    rows[9][23] = "#"
    rows[10][23] = "#"
    for x in range(25, 30):
        rows[7][x] = "#"
    for x in range(25, 29):
        rows[8][x] = "^"
    rows[6][27] = "K"
    rows[3][27] = "o"
    rows[6][29] = "o"
    for span in ((33, 39), (42, 47), (50, 52)):
        for x in range(*span):
            rows[6][x] = "#"
    for x in range(31, 34):
        rows[11][x] = "v"
    for x in range(40, 42):
        rows[10][x] = "^"
    rows[10][46] = "E"
    rows[10][51] = "^"
    rows[9][52] = "F"
    rows[10][52] = "F"
    rows[10][44] = "o"
    rows[10][54] = "o"
    return tuple("".join(row) for row in rows)


def _find_all(rows: tuple[str, ...], marker: str) -> tuple[tuple[int, int], ...]:
    found = []
    for y, row in enumerate(rows):
        for x, cell in enumerate(row):
            if cell == marker:
                found.append((x, y))
    return tuple(found)


def _find(rows: tuple[str, ...], marker: str) -> tuple[int, int]:
    for y, row in enumerate(rows):
        x = row.find(marker)
        if x != -1:
            return (x, y)
    raise ValueError(f"level is missing {marker}")
