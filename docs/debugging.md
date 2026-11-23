# Debugging phase

This is the record of playtesting the terminal game after it became runnable with `python -m game`. The canvas picture is not the game. A code change is invisible until that process is restarted.

Run the suite from the project root with the virtualenv Python. Pytest and git need to run outside the sandbox on this machine, because `sandbox-exec` is missing:

```bash
cd ~/Projects/game && .venv/bin/pytest
```

Python is 3.9.6, so every module that uses modern type hints needs `from __future__ import annotations`.

## How a frame works

`run_game` ticks every 0.05 seconds (20 frames per second). A key steps the simulation immediately, then the loop sleeps the rest of the frame so key repeat cannot sprint the player. After the first key of a frame, the loop waits up to 0.03 seconds for a second key. That is how jump and move pressed together stay on one frame.

`PlayScene.update(1)` always means one tile-step, not a variable `dt`.

World origin is the start tile. Up is positive world y, which is a smaller screen row. `tile_for` is `(start_x + int(x), start_y - int(y))`, and `int` truncates toward zero. On these maps `start_y` is 10, so the floor row 10 is world y 0 and tile row `r` is world y `10 - r`.

`PlayScene(1)` is wrong. The first argument is an `Environment`, so pass `PlayScene(level=1)`.

## Movement

Ground release stops at once. While airborne and not steering, horizontal speed stays constant, so a moving jump is an arc. Holding a direction sets speed to `walk_speed` (1) immediately. There is no ground slide and no air drag.

Jump speed is 3 and gravity subtracts 1 per airborne frame, capped at `max_fall` 3. A running jump from y 0 climbs through y 3, 5, 6, 6, 5, 3 and lands about seven tiles later. The apex is world y 6, which is tile row 4. Any solid in world y 1 through 6 directly above that arc clips it.

The jump used to be decided after the horizontal step. Pressing right and jump on the last tile of a platform walked off, then the ground check failed, so the jump never happened. Takeoff is now decided from the tile you were standing on before that step. Holding jump still hops again on the next landing, because jump is only taken while grounded.

## Keyboard

Held A, D, and the arrow keys must keep moving until release. Pause, restart, start, and quit stay one-shot.

The terminal is asked for the kitty keyboard protocol (`CSI > 11 u`): press, repeat, and release. A press followed by release in the same chunk still emits the command once. Terminals that only repeat characters fall back to a 0.25 second hold, then the key expires. Empty input with nothing held returns no commands.

## Pits and spikes

`v` on the floor row is the pit. Touching the lip used to kill. The lip is now safe: death happens only when the player falls onto the tile below the `v` (`terrain_at(x, y + 1) == "v"` and y decreased). From the lip they can step back onto solid ground. Rising through a pit does not kill. `PlayScene.is_open` stays true one tile under a `v` so the fall can reach that depth.

Spikes (`^`) kill on contact, in any direction.

## Enemies

Enemies were as fast as the player and could only hurt. They now step every other frame (`enemy_pace` is 2, counted in `PlayScene`, not in `Environment.step_enemies`). Landing on an enemy's tile while y decreased removes it. Side contact still costs a life. A removed enemy stays gone until a real life loss or a level restart, which calls `reset()`.

## Damage, shield, and the blink

A real hit returns the player to the origin, drops the key and coins, revives enemies, and loses a life. If lives remain, input is ignored for `respawn_delay` frames (10, half a second). The last life goes straight to game over. Tests that act again after a hit set `scene._respawn_wait = 0`.

The shield is a `+` and exists only on level 2, at tile column 4, row 10. It does not stack. Spending it does not respawn the player and does not cost a life: the shield breaks and `_invincible` is set to 20 frames (1 second). The next hit after that second is a real life loss. The `+` comes back only on that real respawn, because `collected_shields` is cleared in `_suffer_hit`, not when the shield breaks.

If the shield is still held when level 2 ends, it is carried into level 3. Level 3 has no pickup. Invincibility frames do not carry. Beating level 2 without the shield grants nothing on level 3.

While the shield is held, or during that one second, open tiles beside the player are drawn as parentheses, so the figure reads `(@)`. After a hit, the `@` (and the parentheses) is hidden on even remaining frames of invincibility or respawn wait, so the character flashes until control returns.

## Level layout

Levels 2 and 3 still use separate platforms on tile row 6. The player stands at world y 5, which has enough headroom to jump. The gaps are the jumps. The meadow is different on purpose. Its upper route is two steps, not three matching bars.

A running jump moves sideways before it rises. The first new column is entered at the old height, so a brick in that column is hit from the side. The brick has to start on a later column, where the jump is already above it and coming down. A jump from y 0 reaches about y 6 and lands about seven tiles later. A brick you are still rising through cannot be landed on.

The meadow used to be three bars on row 6: columns 20–25, 29–33, and 36–37. That shape was the same idea copied three times. Replacing it took four tries:

- A step in columns 22–25, right after the key ledge. The jump from the end of the ledge is already at y 5 on the first frame, flies over that step, and falls in the pit.
- A longer step covering the pit, including the takeoff column. The sideways move entered that column at y 0, then the rise hit the underside. The lip jump died.
- A step that ended on the tile where the jump landed. The next walk fell onto the spike in column 34.
- The one that stayed. The low step is row 8, columns 27–30. You arrive above it. The higher bridge is row 6, columns 32–37, long enough to walk, and the drop past column 37 is the door rather than the spikes.

From the key ledge, walk to its end, jump, land on the low step, jump again, and you are on the bridge at y 5. From the ground, jump on the last tile before the pit. You land on that same low step. Walking off its right end puts you on the ground in front of the spikes, which you still have to jump.

A solid row-3 bridge was an earlier upper route, before this stair. It does not clip a ground jump, because its brick is at world y 7, above the apex. It also cannot be a platforming path. Standing on it is world y 8, the map top is y 10, and a jump of 3 hits the ceiling and falls through a gap before the next island.

Low ceilings over the pit columns are worse. A solid in world y 1 through 6 above a pit's takeoff blocks the ground jump. A breadth-first search of that layout did not finish, because the ground route was closed and the upper route was not actually reachable. Do not put ceilings over pit columns.

Jumping up through a brick does not land on it. The next platform has to sit under the falling part of the arc, and the jump has to start from the second-to-last tile if takeoff were still checked after the step. With the current takeoff rule, the last tile works when jump and move are the same frame.

Level 3's spike run was reduced to columns 40 and 41 so a miss can land on open ground on either side. The ceiling spikes on row 7, columns 36 through 38, and the spikes at columns 45 and 49, are gone. The spike in front of the door, column 51, stays. Level 3 is no longer required to have more hazards than level 2.

## Checks that lock this in

- `tests/test_keyboard.py` covers hold-until-release, a tap that presses and releases in one chunk, and jump plus move in one read.
- `tests/test_play_scene.py` covers the ground stop, the jump arc, a jump off the last tile of a platform, the shield hit, the respawn pause, and the damage flash.
- `tests/test_environment.py` covers the pit lip, climbing back out, and a scripted jump across the upper platforms.
- `tests/test_level_two.py` and `tests/test_level_three.py` search each level with wait, left, right, jump, and the two diagonals. Deaths are not progress. The search state includes the enemy tick. If a layout blocks the ground route, that search grows without finishing. Stop it and fix the ceilings instead of waiting it out.
