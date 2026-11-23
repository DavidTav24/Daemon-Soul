# AI challenge: landing
The code I can explain without Cursor is the landing check in `PlayScene.update`, the fall in `PlayScene._apply_gravity`, and `Environment.is_open`. Cursor wrote the first version. I changed it after the pit and the last-tile jump felt wrong.

## What does this code do?

`is_open` answers one question: can the player be in this spot? It turns a world position into one tile. A brick is closed. A locked door is closed until I have the key. Air, coins, the key, spikes, pits, and the robot are open.

Standing is not "am I inside a brick." Standing is "the tile under my feet is closed." Before the sideways step, the game looks at that lower tile. If I pressed jump and that tile is solid, this frame is a takeoff and my upward speed becomes 3. If I am not taking off, gravity pulls the vertical speed down by 1, and it will not fall faster than 3.

The body then moves up or down one tile at a time. The first closed tile stops it. If I am moving down and the tile under me is closed, my vertical speed becomes 0. That is the landing.

## Why is it necessary?

The level is a grid of characters. Nothing stops `@` from being drawn on a wall unless some function refuses the move. Hazards have to stay open. If a spike were solid, I would bounce off it and the game would never see me touch it.

## What inputs does it use?

`is_open` takes `x`, `y`, and whether the door is unlocked. Play passes `has_key` for that last one. The start tile is world `(0, 0)`. Up is positive `y`.

`update` also uses the jump button, the position at the start of the frame, and the vertical speed left over from the last frame. `tile_for` does `start_x + int(x)` and `start_y - int(y)`. `int` cuts toward zero. On these maps the floor row is y 0.

## What output or state does it change?

`is_open` changes nothing. It returns true or false.

The caller changes the player. A blocked sideways step puts `x` back. Gravity changes `y` and the vertical speed. If the tile where I end is a spike, or I fell onto the tile under a pit, I take a hit. With the shield, I stay there and I am safe for about a second. Without it, I go back to the start, I drop the key and the coins, the robots come back, and I lose a life.

## What assumptions does it make?

I am one tile wide and one tile tall. Bricks are the only solid ground. The door stays shut until the key flag is true, which is not the same thing as standing on the key tile this frame. Vertical movement checks every tile. Horizontal movement checks only the tile I arrive on. A frame does not move me very far.

## What could go wrong?

A sideways move that passes through a spike and ends on an empty tile is not a hit. Negative coordinates do not mirror the positive side, because of `int`. A brick in the air above a ground jump is "correctly" solid, and it eats the jump. That is how the low bridge made a level impossible. If the pit exception is removed, the lip becomes a floor and I can never fall deep enough to die. If it is too wide, I fall through real ground.

## How did you test it?

`tests/test_environment.py` stands on the pit lip for one frame and expects me to live, then falls one more tile and expects a death. Another test steps back onto solid ground. `tests/test_play_scene.py` checks the jump arc and a jump off the last tile of a platform. I also played in the terminal. The test that convinced me the last-tile jump was real was the one where I held right and jump together and still left the ground.

## Did you modify the AI-generated version? Why?

Yes. The first rule killed me for touching the `v`. I now have to be on the tile below the pit and moving down. I also moved the takeoff check to the tile I occupied before the sideways step, because jump-plus-move on the last tile was walking off and then refusing to jump. I tried an upper path made of low bricks and took it out. Those bricks were solid, the ground jump hit them, and the level could not be finished.

---
