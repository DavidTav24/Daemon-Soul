# Final reflection

The handout's reflection questions were not stored in this project. These ten are the ones this writeup answers: the game I shipped, who made which decisions, the collision function, the bug that took longest, a fix the model got wrong, how I tested, what I still do not trust, what deployment changed, which AI tools I used, and what I would change next.

I set out to make a side-view platformer I could play in a terminal. The shipped game is Ashgate: three gates, a key and a door on each, coins, pits, spikes, and, on the second gate, a shield. The meadow is the beginner gate, the kiln is the shield gate, and the night gate is the long one. That shape came from playing. The first builds were either too empty or so tight that one missed jump ended the run.

I decided the rules. Cursor, using Grok, wrote almost all of the Python, the tests, and the browser page. My part was to play each build, reject the ones that felt wrong, and read the function I would have to explain. I did not treat a green test run as proof that a jump was fair. The terminal is where that showed up.

The collision function I understand is `Environment.is_open`. It takes a world position and whether the door is unlocked, converts that position to one tile, and returns whether the player may stand there. Bricks and a locked door are closed. Everything else is open, including hazards, so a later check can see the overlap. The function itself changes no state. `PlayScene.update` does: it puts back a blocked step, stops a fall on the first solid tile, and on a real hit either spends the shield or restarts the life.

The bug that took longest was the pit. Touching the lip killed me, including a brush that should have been recoverable. The fix was to kill only after falling onto the tile below the `v`, and only while moving down. From the lip I can still step back. That rule is easy to get backward, which is why a test stands on the lip for one frame and expects me to live.

One generated "fix" was a second path made of bricks low over the pits. It looked like a bridge and made the ground route impossible, because a jump rises through those tiles and `is_open` correctly called them solid. A search of the level never finished. I removed that ceiling. The upper route is now separate platforms with room to jump, and the ground route is still open.

I tested with pytest, about seventy tests, and by playing `python -m game` in a real terminal. The tests lock the lip, the jump off a platform edge, the shield, and that each level can be completed. They cannot tell me that a jump feels tight. Holding jump and move at once was one of those feelings: the code jumped only after the sideways step, so the last tile walked off the edge. Takeoff is now decided from the tile I was already on.

I still do not trust two assumptions. Horizontal motion checks the destination tile, not every tile crossed, so a fast step could skip a spike. And `int()` cuts toward zero, so negative coordinates are not a mirror of positive ones. I know those limits because I read the function, not because a test failed.

Local play and the Pages build are the same `GameSession`, but the keyboard is not. The terminal uses key press and release. The browser holds a set of keys and steps the session on a timer. The page loads `src/game` by relative paths. Publishing from the `/docs` folder would break that, because the Python would no longer sit next to `index.html`.

The AI tool was Cursor, with Grok writing the code I then played and edited. I kept `docs/debugging.md` so a later change would not undo the pit, the shield, or the jump. I would not ask the model to "add a path" again without saying which tiles the ground jump needs empty.

Next time I would write the collision tests before adding a level, and I would keep one level boring until the controls felt right. The night gate's spacing changed several times because I was still learning the jump while I was designing it.
