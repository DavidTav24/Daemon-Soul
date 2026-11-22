# Security findings

Reviewed against the Part 1 code, then checked in the source. A row is verified only when the behavior was reproduced or the absence of the sink was confirmed by reading the call path.

| ID | Finding | Location | Severity | Verified? | Remediation |
| --- | --- | --- | --- | --- | --- |
| SEC-01 | Game text was inserted with `innerHTML`. A `<` in that text would have been markup. | `index.html`, `game.markup` | Low | Yes | Escape text, then allow only palette colors as styles. |
| SEC-02 | A failed load printed `error.message` into the page. | `index.html` | Low | Yes | Show a fixed sentence. Leave the detail in the console. |
| SEC-03 | Command names were looked up with `Command[name]`, so an unexpected name raised `KeyError`. | `index.html`, `game.input.command` | Low | Yes | Accept only names of real commands. |
| SEC-04 | The Pyodide loader had no integrity check. | `index.html` | Medium | Yes | Pin `pyodide.js` with a sha384 hash and a Content-Security-Policy. |
| SEC-05 | pytest 8.4.2 matches PYSEC-2026-1845. The game does not import pytest. The fix, pytest 9.0.3, requires Python 3.10. | `requirements.txt` | Low | Yes | Pin 8.4.2 and record why it cannot be upgraded here. |
| SEC-06 | Score, lives, and level live entirely in the browser. | `game.session` | Informational | Yes | Document it. Do not pretend there is an account system. Reject out-of-range values if code calls `_begin_level` directly. |

## Checked, and not present

| Area | Result |
| --- | --- |
| SQL | No database and no query strings. |
| Shell commands | The web page never builds a shell command. `keyboard.py` is terminal-only and is not in the page's file list. |
| Path input | The page fetches a fixed list. A user does not supply a filename. The list is tested so it cannot contain `..`. |
| Secrets | Search of the project found no passwords, tokens, or API keys. |
| Cookies and sessions | No cookies and no session secret. `Secure`, `HttpOnly`, and `SameSite` do not apply. |
| CSRF | No state-changing HTTP request. |
| Debug mode | No web framework debug flag and no stack trace in the page after SEC-02. |
| Authorization | No accounts. One player's browser cannot submit a score for anyone else, because the server never receives a score. |

## Dependency scan

Bandit 1.8.6 on `src/game` reported no issues (1350 lines, 2026-11-22).

`pip-audit` on `pytest==8.4.2` reported PYSEC-2026-1845 / CVE-2025-71176: on UNIX, pytest used a predictable temporary directory. It is a local issue in the test tool, not in the game players download. `pip install pytest==9.0.3` fails on Python 3.9 because that release requires Python 3.10.
