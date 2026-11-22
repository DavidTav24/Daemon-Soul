# Vibe security journal

## 1. Broad review

Security objective: Find issues in the Python game as it is published, without editing yet.

Prompt: Act as a security code reviewer. Review this Python web application for security vulnerabilities. Do not modify the code yet. Identify potential vulnerabilities, explain why each might be dangerous, identify the relevant files and lines, assign a severity, and recommend a remediation.

AI assessment: The first pass looked for a server: routes, SQL, cookies, and a score POST. Those are the usual web findings.

Your assessment: I did not agree that those were bugs here. `index.html` and `game.session` show no HTTP handlers. Treating a missing login page as a broken login would invent a feature.

Action: Wrote the baseline and the "not present" rows before changing code.

Verification: Grep for routes, cookies, SQL, and secrets. None in the game.

Result: The review scope matches the program that ships.

## 2. HTML sink

Security objective: See whether untrusted text can become HTML.

Prompt: Identify every location where untrusted data can reach HTML, JavaScript, or the DOM. Determine whether the data is safely encoded.

AI assessment: `frame.innerHTML = ansiToHtml(draw())` is a sink. The encoder escaped `<`, `>`, and `&`.

Your assessment: I agreed it was a sink. I did not call it a high severity cross-site scripting bug, because the current level text is authored, not typed by another user. I did agree the encoder was untested and lived in the wrong layer.

Action: Moved encoding into `game.markup` and covered it with a payload test.

Verification: The payload `<img src=x onerror="alert(1)">` renders as text. The meadow still loads in the browser.

Result: The encoding is now the tested path. Residual risk is a future edit that assigns `innerHTML` again without `ansi_to_html`.

## 3. Injection

Security objective: Find input concatenated into a query, a shell command, a path, or `eval`.

Prompt: Find every location where external input is combined with an interpreter, database query, command, file path, or template.

AI assessment: A scanner-style pass would flag `keyboard.py` for reading the terminal, and the fetch list for path joins.

Your assessment: The fetch list is a constant. `keyboard.py` is not downloaded by the page. There is no SQL and no `eval` of player input. I agreed those are out of scope, not hidden bugs.

Action: Left the terminal keyboard module out of the page's file list. Added a test that every fetched path stays under `src/game/` and that `keyboard.py` is not fetched.

Verification: `test_the_page_does_not_fetch_outside_the_game_package`.

Result: No injection sink was found to close. The file list cannot silently grow a `..` path without failing the test.

## 4. Secrets

Security objective: See whether a credential was committed.

Prompt: Search this project for hard-coded credentials, API keys, tokens, passwords, or other sensitive configuration. Report potential findings without repeating the values.

AI assessment: No secret material in the tree.

Your assessment: I agreed. The search hits are the word "token" in comments and documentation, not a credential. GitHub login for publishing was done with the GitHub CLI and was not written into the repo.

Action: None in the source. No rotation, because nothing secret was stored.

Verification: Search of `src/`, `index.html`, and `pyproject.toml`.

Result: No committed secret to remove.

## 5. Client authority

Security objective: Decide whether the browser being able to change its own score is an authorization bug.

Prompt: Should the server trust a client that reports score = 5000000 or level = 3?

AI assessment: A client-supplied score should be rejected by the server.

Your assessment: I agreed with the rule and disagreed that this codebase has that request. There is no server receiving the number. The honest finding is the limitation, plus a guard on `_begin_level` so a bad call does not start a gate.

Action: Validate level, score, lives, and the shield flag in `_begin_level`. Do not add a login system for the assignment.

Verification: Tests reject `-100`, `"banana"`, a huge score, and a non-boolean shield. A normal start with score 100 and 2 lives still works. Browser play still starts the meadow.

Result: The function is stricter. The architectural limit is documented instead of papered over.

## 6. Dependencies

Security objective: See whether the pinned tools have a known vulnerability.

Prompt: Review the dependencies. Identify packages, versions, and known security concerns.

AI assessment: The game has no runtime requirements. pytest might be old.

Your assessment: `pip-audit` confirmed PYSEC-2026-1845 in pytest 8.4.2. I checked the fix myself. pytest 9.0.3 will not install on Python 3.9. Bandit reported nothing in `src/game`. I did not treat Bandit's clean run as proof the page was safe. SEC-01 is in the HTML path Bandit does not execute.

Action: Pin pytest and write down the Python version block. Leave Bandit and pip-audit as review tools, not as game dependencies.

Verification: Audit output and the pip error for pytest 9.0.3. The suite still passes.

Result: The advisory is recorded. It is not fixed on this interpreter, and it is not in the player-facing program.
