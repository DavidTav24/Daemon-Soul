# Before and after

| Area | Original | Security issue | Remediation | Result |
| --- | --- | --- | --- | --- |
| HTML output | `innerHTML` plus an untested escape in the page | Markup in the frame would run | `game.markup.ansi_to_html` escapes text and ignores unknown color codes | A harmless `<img onerror>` payload stays text |
| Errors | `error.message` shown in the status line | Extra detail on failure | Fixed sentence, detail only in the console | The page source no longer appends the exception |
| Commands | Any name was looked up on the enum | A bad name raised and stopped the loop | `commands_from_names` keeps known names | `banana` and `<script>` are dropped; jump still works |
| Third-party script | Versioned CDN URL, no hash | A swapped loader would run | sha384 integrity and a Content-Security-Policy | The site still boots; later Pyodide files are not hashed |
| Dependencies | pytest 8.4.2, unpinned | PYSEC-2026-1845, test tool only | Pinned, and the Python 3.10 fix is documented | The game still has no runtime packages |
| Score and level | Client memory only | No shared scoreboard to protect | Documented; `_begin_level` rejects out-of-range values | Normal play is unchanged |
| SQL, shell, cookies, secrets | Not in the application | None found | No decoy controls added | Those surfaces stay absent |
