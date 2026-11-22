# Vulnerability reports

## Finding SEC-01: Game text inserted as HTML

Severity: Low

Location: `index.html` (`frame.innerHTML`) and `game.markup.ansi_to_html`

Description: The frame was built by assigning a string to `innerHTML`. The old script escaped `<`, `>`, and `&`, but the encoder lived only in the page and had no test. Any later change that skipped it would run markup inside the player's browser.

Security impact: A script in the frame could run as the site, in that browser. It could not reach another player, because there is no shared session.

Root cause: The page treated the colored frame as HTML instead of text, and the escape step was not covered by the test suite.

Evidence: `ansi_to_html('<img src=x onerror="alert(1)">')` used to be a JavaScript function. The same payload now goes through `game.markup`, and `tests/test_security.py` asserts the result contains `&lt;img` and does not contain `<img`. A color code that tries to set `background:url(javascript:...)` is dropped.

AI assistance: The review flagged `innerHTML` as a sink. Reading the old `escapeText` showed the current map data did not include `<`, so this was not a live cross-user bug. The missing test was the real gap.

Remediation: `ansi_to_html` escapes text and applies a style only for a color number in a fixed table.

Verification: `test_markup_is_shown_as_text_not_html` and `test_a_hostile_color_code_cannot_set_a_style`.

Regression impact: Movement, jump, and the colored frame still run. The browser check starts the meadow and walks right.

## Finding SEC-02: Exception text on the page

Severity: Low

Location: `index.html`, `main().catch`

Description: The load failure message was `"The gates did not load. " + error.message`.

Security impact: A failure could show a Pyodide path or a Python exception in the page. That helps someone mapping the client. It is not a password.

Root cause: The error handler was written for debugging and left in the published page.

Evidence: The Part 1 `index.html` concatenated `error.message`. The hardened page does not contain that expression. `test_the_page_does_not_print_exception_text_and_pins_the_loader` checks the source.

AI assistance: The review listed debug leakage. The page has no server traceback, so the only leak was this string. That matched the code.

Remediation: The page shows "The gates did not load. Reload the page." The exception goes to `console.error`.

Verification: Source test above. A normal load does not hit the handler.

Regression impact: The published flow still reaches the title screen.

## Finding SEC-03: Unchecked command names

Severity: Low

Location: `index.html` `tick`, now `commands_from_names`

Description: `Command[name]` raises `KeyError` when `name` is not a command. The keyboard map only emits known names, but `tick` accepted whatever array it was given.

Security impact: Unexpected names stopped the frame loop. They did not become code. There is no eval of the name.

Root cause: The bridge from JavaScript to Python trusted the shape of the array.

Evidence: `commands_from_names(["RIGHT", "banana", "<script>", 12])` returns only `RIGHT`. `commands_from_names("RIGHT")` returns an empty list, so a string is not walked character by character into commands.

AI assistance: Input validation was the assigned category. The suggested "reject level = banana" does not apply to an HTTP parameter. It does apply to this function, which is the value the page actually passes in.

Remediation: Unknown names are dropped. Known names become commands.

Verification: `test_command_names_keep_only_known_controls` and the movement test that still jumps with `RIGHT` and `UP`.

Regression impact: A, D, and W still move the player in the browser.

## Finding SEC-04: Loader without an integrity check

Severity: Medium

Location: `index.html` script tag for Pyodide

Description: The page loaded `https://cdn.jsdelivr.net/pyodide/v0.27.0/full/pyodide.js` with no hash. A substituted file would run with the page's privileges.

Security impact: That script can read the page and change the game in the browser that loaded it. It cannot, by itself, sign in as the player anywhere else. There is no account.

Root cause: The CDN URL was pinned by version, which is not the same as pinning the bytes.

Evidence: The Part 1 tag had no `integrity` attribute. The hardened tag has `integrity="sha384-Jbsp01bfi5QMUu9TQeO+5kXvBTqk5CQkcSgbSP9rSEDuQnaamwBF7YDKrSsBmfXw"`, the hash of that file, plus a Content-Security-Policy that allows script only from this origin and that CDN.

AI assistance: The review named the third-party script as supply chain risk. The hash was computed locally with OpenSSL, not taken from the model.

Remediation: Subresource Integrity on the loader, a Content-Security-Policy, and the game script moved to `play.js`. An inline script cannot run under that policy, which is why the first browser check sat on "Loading the gates…" until the script was a file from the same origin. Pyodide still downloads its WebAssembly from the same CDN after the loader starts. Those later files are not covered by this hash.

Verification: The page loads, shows the title, accepts Enter, and shows `MEADOW` with three lives.

Regression impact: Movement still works under the policy. `unsafe-eval` and `wasm-unsafe-eval` stay because Pyodide needs them. Removing them stops the game, which was checked while tightening the policy.

## Finding SEC-05: pytest temporary directory advisory

Severity: Low

Location: development dependency pytest 8.4.2

Description: `pip-audit` reports PYSEC-2026-1845. pytest through 9.0.2 used a predictable `/tmp/pytest-of-{user}` directory. A local user could interfere with it.

Security impact: This does not run when a player opens the site. It matters on a shared machine while running the test suite.

Root cause: The newest installable pytest on Python 3.9 is 8.4.2. pytest 9.0.3 requires Python 3.10.

Evidence: `pip-audit` printed the advisory. `pip install pytest==9.0.3` refused to install on Python 3.9.6.

AI assistance: The dependency pass was the assigned scan, not a guess. The tool's result was checked against pip's own error.

Remediation: `requirements.txt` pins `pytest==8.4.2` and states why the fixed release is not installed. The game's runtime dependencies remain empty.

Verification: The audit output and the failed install of 9.0.3. The test suite still passes on 8.4.2.

Regression impact: None for play. Tests still run.

## Finding SEC-06: The browser is the authority for the score

Severity: Informational

Location: `GameSession`

Description: Score, lives, and the current gate exist only in the page's memory. There is no request a modified client could send to inflate a public scoreboard, because there is no scoreboard.

Security impact: A player can edit their own memory and give themselves lives. That changes their own screen. It does not change anyone else's.

Root cause: Part 1 built a single-player game and then ran that same Python in the browser. No server was added.

Evidence: `index.html` never reads a score from the URL. `GameSession.step` accepts commands, not a score field. Searching the package finds no HTTP route.

AI assistance: A review that assumes every web game has a `/score` endpoint would call this a high authorization bug. That endpoint is not in the tree. Adding a fake server so the report has an authorization fix would invent a product. The code now rejects a direct `_begin_level` call with a bad level, a negative score, or a non-boolean shield, which protects the function if something else starts calling it.

Verification: `test_a_level_outside_the_three_gates_is_rejected`, `test_score_lives_and_shield_outside_range_are_rejected`, and `test_a_normal_level_start_still_works`.

Regression impact: Finishing a gate still carries a normal score and life count. Those values are inside the allowed range.
