# Security baseline

Recorded before the Part 2 changes. The saved copy is git branch `part1-baseline` and the folder `/Users/davidtavares/Projects/ashgate-part1-backup`.

## Stack

| Item | Value |
| --- | --- |
| Python | 3.9.6 |
| Web framework | None. There is no Flask, Django, or other server. |
| Browser runtime | Pyodide 0.27.0, loaded from jsDelivr |
| Third-party Python packages in the game | None |
| Test package | pytest 8.4.2, development only |
| Entry point, terminal | `python -m game` → `game.__main__.main` → `game.session.run_game` |
| Entry point, browser | `index.html` |
| Routes | None. GitHub Pages serves files. The page fetches a fixed list under `src/game/`. |
| Client JavaScript | The script in `index.html` |
| Data stored | Score, lives, level, key, coins, and shield live in memory in `GameSession`. Nothing is written to disk or a database. |
| Configuration files | `pyproject.toml`, `requirements.txt` |
| Environment variables | None read by the game |
| Files written | The terminal does not save a game. The browser writes the fetched Python into Pyodide's in-memory filesystem. |
| External services | jsDelivr, to download Pyodide. No game API. |
| Authentication | None |

## Architecture

```
Browser
   |
   v
index.html  (keyboard events, Content-Security-Policy)
   |
   v
Pyodide, running the same Python package
   |
   +---- GameSession / PlayScene   (score, lives, level, in memory)
   |
   +---- fetched files under src/game/   (read-only game code)
   |
   +---- Pyodide, from jsDelivr
```

There is no second arrow to a server. Two players do not share state.

## What an attacker can control

On the published page, a person can control only the keyboard events in their own browser. Those events become command names such as `RIGHT` or `UP`. They can also edit the page in their own developer tools, which changes only their own game.

They cannot send a URL parameter, form field, JSON body, cookie, or filename that this application reads. The page does not look at `location.search`. Score and level are not accepted from the address bar. There is no account to break into and no other player's score to change.
