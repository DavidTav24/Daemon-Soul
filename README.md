# Ashgate

Ashgate is a three-level side-view platformer. You play `@`. Each gate has a key, a locked door, coins, pits, and spikes. The kiln, the second gate, also has a shield. The same Python rules run in a terminal and, through this repository's GitHub Pages site, in the browser.

## Install the software

Install Python 3.9 or newer. On macOS the system Python is enough:

```bash
python3 --version
```

The browser build needs no install. It loads the Python files from this repository.

## Install the Python dependencies

The game itself depends only on the standard library. Tests use pytest.

```bash
cd game
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Start the app

In a real terminal:

```bash
source .venv/bin/activate
python -m game
```

Restart that process after any code change. A terminal that is not interactive prints a three-frame demo instead of starting play.

Run the tests with:

```bash
.venv/bin/pytest
```

## URL to open

The game is published from the `main` branch, root folder:

https://davidtav24.github.io/ashgate/

Use the root folder. The page loads `src/game` by a relative path. Choosing `/docs` as the Pages folder hides those files and the game cannot start.

Click the page once so the keys go to the game.

## Controls

| Key | Action |
| --- | --- |
| A or Left | Walk left |
| D or Right | Walk right |
| W, Up, or Space | Jump |
| P | Pause |
| R | Restart the gate |
| Enter | Begin, or try again |
| Q | Leave |

Hold a direction to keep walking. Jump and a direction can be pressed on the same frame, including from the last tile of a platform.

## How to play

Enter begins the meadow. Walk and jump to the key, marked `K`, then step into the door, marked `F`. Coins (`o`) add 100 points each. Spikes (`^`) cost a life on contact. A pit (`v`) kills only after you fall through the lip. Landing on an enemy (`E`) removes it. Touching one from the side costs a life.

You have three lives. A real hit pauses briefly, then puts you back at the start of the gate without the key or the coins. The last life opens the game-over screen. Enter starts over.

The `+` on the kiln absorbs one hit. You stay where you are and flash for about a second. If you still have the shield when you clear the kiln, it comes with you into the night gate. The night gate has no pickup of its own.

## How levels work

There are three gates. The status line names the one you are in.

1. **Meadow.** The beginner gate. Cross the pit on the ground, or jump the platforms above it.
2. **Kiln.** The shield is just to the right of the start. The ground has pits, spikes, and an enemy. The upper platforms are the other route.
3. **Night.** Two enemies, a wider pit, and a short spike jump. The upper platforms lead toward the door.

Clearing a gate keeps your score and lives and opens the next one. Clearing the night gate wins.

## What Python does

Python is the game, not a side script. `PlayScene.update` moves the player one frame: walk, jump, gravity, hazards, enemies, then pickups. `Environment.is_open` decides which tiles block that move. `GameSession` switches among the title, the three gates, game over, and the win screen. In the terminal, `run_game` reads the keyboard. On the Pages site, the page sends the same commands into `GameSession.step` and prints the frame Python returns.

## AI tools

The game was built in Cursor with Grok. The assistant wrote the Python, the tests, and this site from play notes. The collision rules, the pit, the shield, and the level layouts were changed after playing them. Notes from that work are in [docs/debugging.md](docs/debugging.md). The collision writeup is [docs/ai-challenge.md](docs/ai-challenge.md). The Part 1 reflection is [docs/reflection.md](docs/reflection.md).

The Part 1 snapshot, taken before the security changes, is the git branch `part1-baseline`. A folder copy is `/Users/davidtavares/Projects/ashgate-part1-backup`.

## Security review

Part 2 reviewed this same game before changing it. The notes are:

- [Baseline and diagram](docs/security/baseline.md)
- [Findings table and scans](docs/security/findings.md)
- [Vulnerability reports](docs/security/reports.md)
- [Before and after](docs/security/before-after.md)
- [Review journal](docs/security/journal.md)
- [Security reflection](docs/security/reflection.md)

The page escapes game text before inserting it, ignores unknown command names, hides raw exception text, and pins the Pyodide loader with a hash and a Content-Security-Policy. There is no server, database, cookie, or secret. pytest is a test tool only. Its known advisory cannot be patched on Python 3.9, and that limit is written down in [requirements.txt](requirements.txt).
