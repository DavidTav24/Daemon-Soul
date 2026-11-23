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

const TILE = 22;
const SVG = "http://www.w3.org/2000/svg";

function ns(tag, attrs) {
  const node = document.createElementNS(SVG, tag);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  return node;
}

function tileSvg(parts) {
  const root = ns("svg", { width: TILE, height: TILE, viewBox: "0 0 22 22" });
  root.style.display = "block";
  for (const [tag, attrs] of parts) root.append(ns(tag, attrs));
  return root;
}

function sky(theme) {
  const width = 21 * TILE;
  const height = 12 * TILE;
  const root = ns("svg", { class: "sky", width, height, viewBox: `0 0 ${width} ${height}` });
  const sun = theme !== "night";
  const radius = Math.min(width, height) * 0.13;
  if (theme === "grass") {
    root.append(
      ns("rect", { width, height, fill: "skyblue" }),
      ns("rect", { y: height * 0.62, width, height: height * 0.38, fill: "olivedrab" }),
      ns("ellipse", { cx: width * 0.2, cy: height * 0.74, rx: width * 0.28, ry: height * 0.1, fill: "forestgreen" }),
      ns("ellipse", { cx: width * 0.55, cy: height * 0.8, rx: width * 0.34, ry: height * 0.12, fill: "darkgreen" }),
      ns("ellipse", { cx: width * 0.86, cy: height * 0.76, rx: width * 0.24, ry: height * 0.1, fill: "yellowgreen" }),
      ns("ellipse", { cx: width * 0.24, cy: height * 0.16, rx: width * 0.14, ry: height * 0.05, fill: "white" }),
      ns("ellipse", { cx: width * 0.32, cy: height * 0.14, rx: width * 0.08, ry: height * 0.04, fill: "white" }),
    );
  } else if (theme === "night") {
    root.append(
      ns("rect", { width, height, fill: "midnightblue" }),
      ns("rect", { y: height * 0.5, width, height: height * 0.22, fill: "darkcyan" }),
      ns("rect", { y: height * 0.68, width, height: height * 0.32, fill: "darkkhaki" }),
      ns("ellipse", { cx: width * 0.18, cy: height * 0.84, rx: width * 0.26, ry: height * 0.08, fill: "tan" }),
      ns("ellipse", { cx: width * 0.58, cy: height * 0.88, rx: width * 0.32, ry: height * 0.09, fill: "burlywood" }),
      ns("circle", { cx: width * 0.16, cy: height * 0.12, r: 2, fill: "white" }),
      ns("circle", { cx: width * 0.42, cy: height * 0.1, r: 2, fill: "white" }),
      ns("circle", { cx: width * 0.74, cy: height * 0.08, r: 1.5, fill: "white" }),
    );
  } else {
    root.append(
      ns("rect", { width, height, fill: "moccasin" }),
      ns("rect", { y: height * 0.62, width, height: height * 0.38, fill: "tan" }),
      ns("ellipse", { cx: width * 0.22, cy: height * 0.78, rx: width * 0.28, ry: height * 0.1, fill: "burlywood" }),
      ns("ellipse", { cx: width * 0.55, cy: height * 0.84, rx: width * 0.34, ry: height * 0.12, fill: "sandybrown" }),
      ns("ellipse", { cx: width * 0.86, cy: height * 0.8, rx: width * 0.24, ry: height * 0.1, fill: "wheat" }),
    );
  }
  if (sun && theme !== "night") {
    const fill = theme === "grass" ? "gold" : "orangered";
    root.append(ns("circle", { cx: width - radius * 0.72, cy: radius * 0.72, r: radius, fill }));
  }
  if (theme === "night") {
    root.append(ns("circle", { cx: width - radius * 0.72, cy: radius * 0.72, r: radius, fill: "lightyellow" }));
    root.append(ns("circle", { cx: width - radius * 0.45, cy: radius * 0.55, r: radius * 0.82, fill: "midnightblue" }));
  }
  return root;
}

function playerSprite(mouth, facing) {
  const root = ns("svg", { width: TILE, height: TILE, viewBox: "0 0 100 100" });
  root.style.display = "block";
  root.style.transform = facing === "left" ? "scale(1.05) scaleX(-1)" : "scale(1.05)";
  root.style.transformOrigin = "center bottom";
  root.append(
    ns("rect", { x: 32, y: 6, width: 36, height: 26, rx: 3, fill: "aqua" }),
    ns("polygon", { points: "50,18 72,8 72,28", fill: mouth }),
    ns("circle", { cx: 42, cy: 16, r: 3.5, fill: "white" }),
    ns("rect", { x: 46, y: 30, width: 10, height: 8, fill: "aqua" }),
    ns("rect", { x: 32, y: 36, width: 36, height: 24, fill: "black" }),
    ns("rect", { x: 36, y: 58, width: 10, height: 18, fill: "black" }),
    ns("rect", { x: 54, y: 58, width: 10, height: 18, fill: "black" }),
    ns("rect", { x: 32, y: 74, width: 14, height: 18, fill: "saddlebrown" }),
    ns("rect", { x: 54, y: 74, width: 14, height: 18, fill: "saddlebrown" }),
  );
  return root;
}

function brick(theme) {
  const mortar = theme === "grass" ? "darkolivegreen" : theme === "night" ? "midnightblue" : "tan";
  const faces = theme === "grass"
    ? ["olivedrab", "forestgreen", "darkgreen", "saddlebrown"]
    : theme === "night"
      ? ["slategray", "dimgray", "darkslategray", "cadetblue"]
      : ["sandybrown", "peru", "burlywood", "sienna"];
  const courses = [
    { y: 0, h: 6, bricks: [[0, 10], [11, 11]] },
    { y: 7, h: 7, bricks: [[0, 5], [6, 10], [17, 5]] },
    { y: 15, h: 7, bricks: [[0, 10], [11, 11]] },
  ];
  const parts = [["rect", { width: 22, height: 22, fill: mortar }]];
  courses.forEach((course, row) => {
    course.bricks.forEach(([x, w], index) => {
      parts.push(["rect", { x, y: course.y, width: w, height: course.h, fill: faces[(row + index) % faces.length] }]);
    });
  });
  return tileSvg(parts);
}

function floor(theme) {
  const patches = theme === "grass"
    ? ["forestgreen", "olivedrab", "sienna", "saddlebrown"]
    : theme === "night"
      ? ["darkkhaki", "tan", "burlywood", "peru"]
      : ["wheat", "tan", "burlywood", "sandybrown"];
  const box = document.createElement("div");
  box.className = "tile";
  box.style.display = "grid";
  box.style.gridTemplateColumns = "1fr 1fr";
  for (const fill of patches) {
    const patch = document.createElement("div");
    patch.style.background = fill;
    box.append(patch);
  }
  return box;
}

function cellNode(cell, theme, floorRow, hanging, doorTop, facing) {
  if (cell === "@") {
    const mouth = theme === "grass" ? "skyblue" : theme === "night" ? "midnightblue" : "moccasin";
    return playerSprite(mouth, facing);
  }
  if (cell === "#") return floorRow ? floor(theme) : brick(theme);
  if (cell === "o") return tileSvg([["circle", { cx: 11, cy: 11, r: 6, fill: "peru" }], ["circle", { cx: 11, cy: 11, r: 3.4, fill: "none", stroke: "saddlebrown", "stroke-width": 1.1 }]]);
  if (cell === "K") return tileSvg([["circle", { cx: 7, cy: 11, r: 3.2, fill: "none", stroke: "gold", "stroke-width": 1.7 }], ["rect", { x: 10, y: 10, width: 8, height: 2, fill: "gold" }], ["rect", { x: 15, y: 12, width: 2, height: 3, fill: "gold" }]]);
  if (cell === "^") {
    const points = hanging ? ["1,1 4.5,30 8,1", "8,1 11.5,30 15,1", "15,1 18.5,30 21,1"] : ["1,21 4.5,-8 8,21", "8,21 11.5,-8 15,21", "15,21 18.5,-8 21,21"];
    return tileSvg(points.map((shape) => ["polygon", { points: shape, fill: "silver" }]));
  }
  if (cell === "v") {
    const lip = theme === "grass" ? "olivedrab" : theme === "night" ? "cadetblue" : "sandybrown";
    const deep = theme === "grass" ? "darkgreen" : theme === "night" ? "darkslateblue" : "saddlebrown";
    return tileSvg([["rect", { width: 22, height: 22, fill: lip }], ["polygon", { points: "1,8 21,8 14,22 8,22", fill: deep }], ["polygon", { points: "3,11 19,11 13,22 9,22", fill: "black" }]]);
  }
  if (cell === "E") return tileSvg([["rect", { x: 5, y: 8, width: 12, height: 7, fill: "silver" }], ["rect", { x: 7, y: 10, width: 8, height: 2.4, fill: "orangered" }], ["circle", { cx: 11, cy: 4.5, r: 1.3, fill: "orangered" }], ["rect", { x: 6, y: 15, width: 4, height: 5, fill: "dimgray" }], ["rect", { x: 12, y: 15, width: 4, height: 5, fill: "dimgray" }]]);
  if (cell === "F") {
    const parts = [["rect", { width: 22, height: 22, fill: "saddlebrown" }], ["rect", { x: 3, y: 0, width: 16, height: doorTop ? 22 : 19, fill: "sienna" }]];
    if (!doorTop) parts.push(["circle", { cx: 11, cy: 9, r: 3.2, fill: "gold" }]);
    return tileSvg(parts);
  }
  if (cell === "(" || cell === ")") return tileSvg([["circle", { cx: 11, cy: 11, r: 8, fill: "none", stroke: "aqua", "stroke-width": 2 }]]);
  if (cell === "+") return tileSvg([["rect", { x: 9, y: 3, width: 4, height: 16, fill: "gold" }], ["rect", { x: 3, y: 9, width: 16, height: 4, fill: "gold" }]]);
  const empty = document.createElement("div");
  empty.className = "tile";
  return empty;
}

function themeFor(mode, level) {
  if (mode === "gameover" || (mode === "play" && level === 3)) return "night";
  if (mode === "play" && level === 2) return "desert";
  return "grass";
}

function cellSig(cell, hanging, doorTop, facing) {
  return cell + (hanging ? "h" : "") + (doorTop ? "t" : "") + (cell === "@" ? facing : "");
}

function playStage(rows, theme, facing) {
  const stage = document.createElement("div");
  stage.append(sky(theme));
  const grid = document.createElement("div");
  grid.className = "grid";
  rows.forEach((row, y) => {
    const line = document.createElement("div");
    line.className = "row";
    [...row].forEach((cell, x) => {
      const hanging = cell === "^" && rows[y - 1]?.[x] === "#";
      const doorTop = cell === "F" && rows[y + 1]?.[x] === "F";
      const node = cellNode(cell, theme, y === rows.length - 1, hanging, doorTop, facing);
      node.classList.add("tile");
      node.dataset.sig = cellSig(cell, hanging, doorTop, facing);
      line.append(node);
    });
    grid.append(line);
  });
  stage.append(grid);
  return stage;
}

function paintGrid(grid, rows, theme, facing) {
  rows.forEach((row, y) => {
    const line = grid.children[y];
    [...row].forEach((cell, x) => {
      const hanging = cell === "^" && rows[y - 1]?.[x] === "#";
      const doorTop = cell === "F" && rows[y + 1]?.[x] === "F";
      const sig = cellSig(cell, hanging, doorTop, facing);
      const current = line.children[x];
      if (current.dataset.sig === sig) return;
      const node = cellNode(cell, theme, y === rows.length - 1, hanging, doorTop, facing);
      node.classList.add("tile");
      node.dataset.sig = sig;
      current.replaceWith(node);
    });
  });
}

let board = null;

function present(payload) {
  const [meta, statusLine, ...rows] = String(payload).split("\n");
  const [mode, levelText, facing] = meta.split("|");
  status.textContent = statusLine;
  const theme = themeFor(mode, Number(levelText));
  const kind = mode === "play" ? "play" : "title";
  const shown = kind === "play"
    ? rows
    : rows.map((row, y) => (y === rows.length - 1 ? "#".repeat(row.length || 21) : " ".repeat(row.length || 21)));
  if (!board || board.kind !== kind || board.theme !== theme) {
    const stage = playStage(shown, theme, facing || "right");
    if (kind === "title") {
      const caption = document.createElement("p");
      caption.className = "caption";
      caption.textContent = rows.map((row) => row.trim()).filter(Boolean).join("\n");
      stage.append(caption);
      const actor = playerSprite(theme === "night" ? "midnightblue" : "skyblue", "right");
      actor.style.position = "absolute";
      actor.style.left = `${10 * TILE}px`;
      actor.style.bottom = `${TILE}px`;
      stage.append(actor);
    }
    frame.replaceChildren(stage);
    board = { kind, theme, grid: stage.querySelector(".grid"), caption: stage.querySelector(".caption") };
    return;
  }
  if (kind === "play") paintGrid(board.grid, shown, theme, facing || "right");
  else if (board.caption) board.caption.textContent = rows.map((row) => row.trim()).filter(Boolean).join("\n");
}

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
from game.render.renderer import FrameRenderer
from game.session import GameSession

session = GameSession()
renderer = FrameRenderer()

def tick(names):
    if not session.running:
        return False
    session.step(commands_from_names(names))
    return session.running

def draw():
    renderer.clear()
    session.render(renderer)
    renderer.present()
    facing = "right"
    if session.mode == "play" and session.play is not None:
        facing = session.play.player.facing
    rows = "\\n".join(renderer.frames[-1])
    return session.mode + "|" + str(session.level) + "|" + facing + "\\n" + session.status_line() + "\\n" + rows
`);
  const tick = pyodide.globals.get("tick");
  const draw = pyodide.globals.get("draw");
  status.textContent = "Click the picture. A and D walk, W jumps, Enter begins.";
  frame.focus();
  present(draw());
  let playing = true;
  while (playing) {
    const started = performance.now();
    const names = [...held, ...once];
    once.length = 0;
    try {
      playing = Boolean(tick(names));
      present(draw());
      if (!playing) status.textContent = "You left Daemon soul.";
    } catch (error) {
      console.error(error);
      status.textContent = "The gate could not update. Reload the page.";
      playing = false;
    }
    const wait = Math.max(0, 50 - (performance.now() - started));
    await new Promise((resolve) => window.setTimeout(resolve, wait));
  }
}

main().catch((error) => {
  console.error(error);
  status.textContent = "The gates did not load. Reload the page.";
});
