# Final reflection

## 1. How did using Cursor change the way you approached programming?

I stopped trying to hold the whole program in my head before I typed. I described one behavior, ran it, and only then asked for the next one. On November 16 I had Cursor build one feature and stop. That was how I knew what had been added.

## 2. Which prompts produced the most useful results?

The useful prompts named a bad feeling I had just played. "Have the player die to the pitfall if he falls in it not touch it." "fix the air momentum so that the player can do an arc if they jump while moving." "have the movement control be able to work when inputted at the same time when it comes to jumping and moving." Each one pointed at a single frame.

## 3. Which prompts produced poor or incorrect results?

The wide prompts did. "Make the level a bit more complex" and "add a path" both came back as more bricks. Bricks are solid. The new bricks blocked a jump I already needed. A step glued to the key ledge was jumped over. A step on the takeoff column was hit from the side.

## 4. How did you determine whether AI-generated code was correct?

I did not treat a passing test as proof. Pytest told me a function returned the value I asked for. It did not tell me a jump was fair. I ran `python -m game` in a real terminal after movement changes. On November 22 I opened the browser, pressed Enter, held D until the drawn character picked up a coin, and jumped. When a level search ran forever, I treated that as a closed path.

## 5. Describe a significant bug and how you diagnosed it.

The pit lasted the longest. I wanted the edge safe and the hole deadly. Touching the lip killed me. I asked for a lower hitbox, and the first result was still too harsh, so I said it again. The rule that stayed: I die only if I am on the tile under the `v` and I am moving down. From the lip I can step back. A test stands on that lip for one frame and expects me to live.

## 6. Which parts of the program do you understand most confidently?

Landing. `is_open` says whether one tile is free. A brick and a locked door are closed. A spike and a pit are open, so a later check can see that I touched them. `PlayScene.update` looks under my feet before the sideways step. If that tile is solid and I pressed jump, my upward speed becomes 3. Gravity walks me one tile at a time and stops on the first closed tile. That stop is standing.

## 7. Which parts still require additional study?

Two edges I found by reading, not by dying to them. A horizontal move checks the tile I land on, not every tile I cross, so a long step could skip a spike. `int()` cuts toward zero, so negative coordinates are not a mirror of the positive side. I am also less sure about the browser loop. The same Python runs there, but the keys are a set in JavaScript and the picture is rebuilt on a timer. A tap shorter than a slow frame never arrives.

## 8. What are the advantages of vibe coding for a beginning programmer?

I got three levels moving while I was still learning how high a jump goes. I could describe a bad landing in one sentence and have a change the same hour.

## 9. What are the risks of relying too heavily on AI-generated code?

A tidy explanation can be about the wrong problem. Cursor once put a low ceiling over the pit. `is_open` was right to call those bricks solid, the ground route died, and a search of the level never finished. If I had only read the function, I would have said collision worked. The level was still impossible.

## 10. If you redesigned the game, what would you change?

I would draw the three levels on paper before I asked for any bricks, and I would leave the first level boring until jump and move felt right. I would also put the illustrated character in the page I actually play, instead of designing him on a canvas and finding out later that the running game was still an `@`.
