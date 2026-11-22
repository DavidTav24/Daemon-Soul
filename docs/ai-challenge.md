# The AI challenge: collision

The function I can explain without the editor is `Environment.is_open`, together with the few lines in `PlayScene` that act on its answer. Cursor wrote the first version. I changed it after playing, because the first version killed me for touching a pit and let a sideways step cancel a jump.

## What it does

`is_open` answers one question: can the player occupy this point? It turns world coordinates into a tile, then looks at that one character in the level. A brick (`#`) is closed. A locked door is closed until the player has the key. Air, coins, the key, spikes, pits, and enemies are open. Standing on a brick works because the check looks at the tile under the player's feet, not at the player's own tile.

`PlayScene._is_open` adds one exception. The tile directly under a pit (`v`) is also open, so the player can fall through the lip to the depth that actually kills.

## Why it is needed

The picture of the level is only text. Nothing stops the `@` from being drawn on top of a wall unless some function refuses the move. `is_open` is that function. Hazard checks are separate on purpose: the player has to be allowed to enter a spike or a pit, or the game could never notice the overlap.

## Inputs

- `x` and `y`: world position. The start tile is `(0, 0)`. Up is positive `y`.
- `door_unlocked`: true after the key is collected. `PlayScene` passes `self.has_key`.

`tile_for` does `start_x + int(x)` and `start_y - int(y)`. `int` cuts toward zero.

## What state it changes

`is_open` changes nothing. It only returns true or false.

The caller changes state. In `PlayScene.update`, a blocked horizontal step puts `x` back. Gravity then steps `y` one tile at a time and stops on the first closed tile. If the tile where the frame ends is a spike, or the player fell onto the tile below a pit, `_take_hit` runs. With a shield, that sets about one second of invincibility and leaves the player in place. Without a shield, it moves the player back to the start, drops the key and coins, revives enemies, and loses a life.

## Assumptions

- The player is one tile wide and tall, so one cell is the whole collision.
- A frame moves at most a few tiles, and vertical motion checks each tile. Horizontal motion checks only the destination.
- Bricks are the only solid terrain. Spikes and pits are open tiles with a later rule.
- The door is closed until the key flag is true. The flag is not the same thing as standing on the key tile.
- World `y` lines up with rows: row 10 is `y` 0 on these maps.

## What could go wrong

- A horizontal move that passes through a spike and lands on an empty tile is not a hit, because only the end tile is checked.
- Negative world coordinates truncate toward zero, so they do not mirror the positive side.
- A ceiling in world `y` 1 through 6, directly above a ground jump, eats the jump. That is not a bug in `is_open`. It is `is_open` correctly calling the brick solid.
- If the pit exception is removed, the lip becomes a floor and the deep-fall death never happens. If the exception is too wide, the player falls through real ground.
- `PlayScene(1)` does not build level 1. The number is taken as the environment.

## How I tested it

`tests/test_environment.py` stands on the pit lip for one frame and expects the player to live, then falls one more tile and expects a death. Another test steps back off the lip onto solid ground. `tests/test_play_scene.py` checks the jump arc, a jump off the last tile of a platform, shield hits, and the respawn pause. `tests/test_level_two.py` and `tests/test_level_three.py` search every level with wait, left, right, and jump. I also played in a real terminal, which is the only check that tells me a jump feels possible.

## Whether I modified it, and why

Yes. The generated rule killed the player for touching the `v` tile. I now require the player to be on the tile below the pit and to be moving down. I also decide the jump from the ground occupied at the start of the frame, so pressing jump and a direction on the last tile still jumps. I tried an upper path made of low bricks and took it out: those bricks were solid to `is_open`, so the ground jump hit them and the level could not be finished.
