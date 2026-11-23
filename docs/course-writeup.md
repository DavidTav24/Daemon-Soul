# Daemon soul: journal, collision, and reflection

I did not keep this journal while I was building. I wrote it on November 22 from the Cursor chat and from the commits. The prompts below are the ones I actually typed.

The commits are `6d934d0` on November 16, `a1d6064` and `cb057fb` on November 21, and `6bd23c3` on November 22.

---

# Vibe coding journal

## Session 1. November 15–16. A project I could add to one piece at a time

**Goal.** Get a Python game folder, not a blank web app, and put the first controls in it.

**Prompts I used.** "Create a new project." Then "delete this project." Then "Make me a new project with an architecture used for simple game design" and "Use different folder." On the 16th: "build each feature one at a time and stop for feedback between each build." "add start, quit and four directions." "Why does it print 4 dots?" "the terminal failed to launch."

**What Cursor generated.** A package under `src/game` with scenes, a command list, and pytest. Start, quit, and the four directions were commands, not a moving character yet.

**What I tested.** I asked where pytest was and ran the tests. I tried to open the game in the terminal.

**What worked.** The tests for the commands passed once I was in the right folder and the virtualenv.

**What failed.** The first project was the wrong kind, so I deleted it. The terminal did not launch. The "4 dots" were pytest's passing tests, which I read as the game drawing something.

**What I changed.** I stopped asking for a finished game. I made Cursor stop after each feature so I could ask what it was before the next one.

**What I learned.** A green test is not the game. I have to know what the test is counting.

## Session 2. November 16, afternoon. Gravity, a key, and a body

**Goal.** A side-view floor, a way to finish the level, and a character that was mine.

**Prompts I used.** "We will need gravity for the player." "for the level to be completed a key must be collected and the player must reach the end." "I like the two shoes. Can we change the face and make it kind of look like pacman with the shape, but make the skin aqua blue with white eyes." "Instead of copying the pacman look give him a human body." "make the head a bit rectangular." "make the mouth a bit bigger." "Now explain the collision algorithm in plain language."

**What Cursor generated.** Gravity, a key and a finish, and a canvas drawing: aqua head, black body, brown shoes. It also wrote the first explanation of standing on a tile. I committed this as `6d934d0`, "Add the side-view level and the rules that make it playable."

**What I tested.** "Test the build so far." I looked at the canvas after every face change. I asked "has the work been saved?" and then "put the work in a git snapshot."

**What worked.** The head stopped reading as a copied Pac-Man once it was a rectangle on a human body. The collision explanation was simple enough: you are standing when the tile under your feet is a brick.

**What failed.** The first face was too close to Pac-Man. The round head and the long neck looked wrong, so I kept sending small corrections instead of one "make a character" prompt.

**What I changed.** Shoes stayed. Body became human. Head became a short rectangle with a bigger mouth. Skin stayed aqua, eyes stayed white.

**What I learned.** The drawing lived on the canvas. The game I would later run was still text. I did not catch that on this day.

## Session 3. November 18. Three places, and no way to play them

**Goal.** A beginner level, a harder second level, and a last level, each with its own background.

**Prompts I used.** "Make the lower portion of the background green to represent grass lands." "undo that." "Now on to the second level." "Make the background a desert." "Add an enemy that is a walkable hazard." "Make the enemy look like a robot." "For this level make the environment a beach nightime setting." "Nooo what about the grasslands first easy level." "Put back the grasslands color and background for only that level." "Simplify the first level so it can be for beginners" and, right after, "not too simple though."

**What Cursor generated.** Grass, desert, and night backgrounds, coins, a gold key, a locked door, silver spikes, pits, a robot, a start screen, and a game over screen. A lot of that was still the canvas.

**What I tested.** "Is this level completable." "Test the entire build." Then "Is there a way for me to test the game and play it" and "How can we get the game playable."

**What worked.** Asking for the grasslands back by name got level 1 its own set. The robot was readable as an enemy. Making level 1 simpler, but not empty, gave me a first stage I could describe.

**What failed.** Building the desert replaced the grass until I complained. One UI move shoved the score too far right, so I said "Undo the change only move it a little bit to the right." The big failure was at the end of the night: I still could not play. The pictures were not the running game.

**What I changed.** I told Cursor to build the game so I could test it, instead of adding more art.

**What I learned.** I should have asked "can I play this" on day one. A canvas can look finished while the program you launch does nothing you can control.

## Session 4. November 18 night through November 20. The part I can feel

**Goal.** Make `python -m game` move like a platformer, then make the hits fair.

**Prompts I used.** "Have the player stand still if theres no input." "fix the air momentum so that the player can do an arc if they jump while moving." "Have the player die to the pitfall if he falls in it not touch it." "lower the pitfalls hitbox so it doesnt kill the player wiith an accidental touch." "Have the player respond to holding the input keys." "if the player dies or take damage add a lil delay before the next life." "have the enemy walk in a slower manner and if the player jumps or lands on him the enemy gets elimated." "add a shield powerup which gives the player an extra hit" and "Have it only available in the second level." "make the spike jump easier on the third level." "Instead of basic bridge make it a platforming path." "if the player takes damage have character flash like mario." "have the movement control be able to work when inputted at the same time when it comes to jumping and moving."

**What Cursor generated.** Ground stop, an arc in the air, a pit rule, a respawn pause, a slower robot you can stomp, a shield only on level 2, a flash, and a second route of platforms. This is the playtesting that later went into `docs/debugging.md` and into commit `a1d6064`.

**What I tested.** I played in the terminal after each change. I also had Cursor run pytest. For the upper path I watched a search of the level. When the search never finished, the level was blocked.

**What worked.** Letting go of the key stops you on the ground. Holding jump and a direction in the air keeps the arc. The shield breaks in place and lasts about a second. Landing on the robot removes it. The flash hides the character on every other frame after a hit.

**What failed.** Touching the pit lip killed me. A first "lower the hitbox" pass was not enough, so I said it again. Jump was checked after the sideways step, so the last tile of a platform walked off and the jump never happened. A solid upper bridge could not be jumped along, because the jump hit the ceiling. Bricks placed low over the pit blocked the ground jump, and the level search hung.

**What I changed.** Death only happens once I have fallen onto the tile under the `v` and I am moving down. Takeoff is decided from the tile I was already standing on. The upper route became separate platforms with room to jump, not one bar. Level 3 lost the spikes that made one miss the end of the run.

**What I learned.** I have to say which tiles must stay empty. "Add a path" gives me bricks. Bricks are solid. Solid bricks eat the jump.

## Session 5. November 21. A name, a page, and the wrong reflection questions

**Goal.** Give the terminal game a theme, explain collision, put it on GitHub Pages, and write the README.

**Prompts I used.** "Document the debugging phase that has been happening." "Give the game a unique Ui giving it a theme." Then the assignment steps for the AI challenge, GitHub Pages, the README, and a 500–750 word reflection.

**What Cursor generated.** The Ashgate colors (meadow, kiln, night), `docs/debugging.md`, `docs/ai-challenge.md`, a README, and a reflection. The site went up as `davidtav24.github.io/ashgate/`. Commits `a1d6064` and `cb057fb`.

**What I tested.** I opened the published URL. I pressed Enter and got the meadow with 3 lives. I held a direction long enough to see `@` move one tile.

**What worked.** The same Python runs in the terminal and in the browser. Publishing from the repository root mattered, because the page loads `src/game` next to `index.html`.

**What failed.** Plain `git push` could not log in. An inline script was blocked by the page's security policy, so the loader sat on "Loading the gates…" until the game script moved into `play.js`. The browser also reused an old Python file until the fetch stopped caching. The reflection answered ten questions I had guessed. The handout's ten questions are different. This page replaces that reflection.

**What I changed.** The game script is a separate file. Python files are fetched with the cache bypassed. I signed in with `gh` and pushed without changing my git config.

**What I learned.** The page is not the terminal. The terminal sees key presses and releases. The page holds a set of keys and steps the game on a timer. A short tap can end before the slow frame notices it.

## Session 6. November 22. The drawing, the name, and my meadow

**Goal.** Play the character I had designed, name the game, and make level 1 look like a choice I can explain.

**Prompts I used.** "when playing the game does the designed map and character also be seen." "add the earlier design and illustrated map and character into the playable game and change the name from ASHGATE to Daemon soulz." "take out the z in demon soulz." "have the illistruation playable." Then the note that the meadow had to be mine, with the failures written down.

**What Cursor generated.** A browser picture built from the live level: grass, desert, or night, bricks, the aqua character, coins, the key, the door, spikes, pits, and the robot. The title became Daemon soul. The meadow's three matching bars became a low step over the pit and a higher bridge over the spikes.

**What I tested.** I reloaded the local page, pressed Enter, held D, and watched the character walk and pick up a coin. I jumped. I also ran pytest. For the stair I tried four layouts and kept the one a jump could land on.

**What worked.** Enter starts the meadow. A and D walk. W jumps. The mouth is the sky color, the same way the canvas worked. The low step is columns 27–30. The bridge is columns 32–37. Jump from the end of the key ledge, then jump again, and you are on the bridge.

**What failed.** The first illustrated page rebuilt every tile every frame, so holding right barely moved me. "Daemon soulz" had a z I did not want. A step glued to the key ledge was jumped over. A step on the takeoff column was hit from the side. A step that ended on the landing tile dropped the next walk onto the spike in column 34.

**What I changed.** The page only redraws a tile when that cell changes, and it waits for the frame to finish before the next one. The name is Daemon soul. The meadow keeps the two steps that sit where the jump is already falling.

**What I learned.** The terminal is still the `@` map. The illustrated game is the browser page. I should say that out loud if someone asks me to play it.

---

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
