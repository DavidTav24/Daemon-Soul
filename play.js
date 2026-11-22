const FILES = [
  "src/game/__init__.py",
  "src/game/py.typed",
  "src/game/environment.py",
  "src/game/session.py",
  "src/game/theme.py",
  "src/game/markup.py",
  "src/game/entities/__init__.py",
  "src/game/entities/entity.py",
  "src/game/entities/player.py",
  "src/game/entities/enemy.py",
  "src/game/input/__init__.py",
  "src/game/input/command.py",
  "src/game/input/source.py",
  "src/game/render/__init__.py",
  "src/game/render/renderer.py",
  "src/game/render/screen.py",
  "src/game/scenes/__init__.py",
  "src/game/scenes/play.py",
  "src/game/scenes/start.py",
  "src/game/scenes/game_over.py"
];

const frame = document.querySelector("#frame");
const status = document.querySelector("#status");
const held = new Set();
const once = [];

const KEYS = {
  ArrowLeft: "LEFT", ArrowRight: "RIGHT", ArrowUp: "UP",
  KeyA: "LEFT", KeyD: "RIGHT", KeyW: "UP", Space: "UP",
  KeyP: "PAUSE", KeyR: "RESTART", Enter: "START", KeyQ: "QUIT"
};
const CONTINUOUS = new Set(["LEFT", "RIGHT", "UP"]);

function onKey(event, down) {
  const command = KEYS[event.code];
  if (!command) return;
  event.preventDefault();
  if (CONTINUOUS.has(command)) {
    if (down) held.add(command);
    else held.delete(command);
  } else if (down) {
    once.push(command);
  }
}
frame.addEventListener("keydown", (event) => onKey(event, true));
frame.addEventListener("keyup", (event) => onKey(event, false));
window.addEventListener("keydown", (event) => onKey(event, true));
window.addEventListener("keyup", (event) => onKey(event, false));

async function main() {
  const pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.27.0/full/",
  });
  pyodide.FS.mkdirTree("/ashgate/src/game/entities");
  pyodide.FS.mkdirTree("/ashgate/src/game/input");
  pyodide.FS.mkdirTree("/ashgate/src/game/render");
  pyodide.FS.mkdirTree("/ashgate/src/game/scenes");
  for (const path of FILES) {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) throw new Error("Missing " + path);
    pyodide.FS.writeFile("/ashgate/" + path, await response.text());
  }
  pyodide.runPython(`
import sys
sys.path.insert(0, "/ashgate/src")
from game.input.command import commands_from_names
from game.markup import ansi_to_html
from game.render.renderer import FrameRenderer
from game.render.screen import Screen
from game.session import GameSession, _CONTROLS
from game.theme import paint, paint_line, palette_for

session = GameSession()
renderer = FrameRenderer()
screen = Screen(width=23, height=14)

def tick(names):
    if not session.running:
        return False
    session.step(commands_from_names(names))
    return session.running

def draw():
    renderer.clear()
    session.render(renderer)
    renderer.present()
    picture = screen.show(renderer.frames[-1])
    palette = palette_for(session.mode, session.level)
    text = "\\n\\n".join([
        paint_line(session.status_line(), palette),
        paint(picture, palette),
        paint_line(_CONTROLS, palette),
    ])
    return ansi_to_html(text)
`);
  const tick = pyodide.globals.get("tick");
  const draw = pyodide.globals.get("draw");
  status.textContent = "Click the frame. A and D walk, W jumps, Enter begins.";
  frame.focus();
  frame.innerHTML = draw();
  window.setInterval(() => {
    const names = [...held, ...once];
    once.length = 0;
    try {
      const running = tick(names);
      frame.innerHTML = draw();
      if (!running) status.textContent = "You left the gate.";
    } catch (error) {
      console.error(error);
      status.textContent = "The gate could not update. Reload the page.";
    }
  }, 50);
}

main().catch((error) => {
  console.error(error);
  status.textContent = "The gates did not load. Reload the page.";
});
