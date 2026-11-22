"""Keyboard commands for a terminal frame."""

from __future__ import annotations

import os
import select
import sys
import termios
import time
import tty

from game.input.command import Command

_ARROWS = {
    "A": Command.UP,
    "B": Command.DOWN,
    "C": Command.RIGHT,
    "D": Command.LEFT,
}
_LETTERS = {
    "a": Command.LEFT,
    "d": Command.RIGHT,
    "w": Command.UP,
    " ": Command.UP,
    "\r": Command.START,
    "\n": Command.START,
    "p": Command.PAUSE,
    "r": Command.RESTART,
    "q": Command.QUIT,
}
_CODES = {
    97: Command.LEFT,
    100: Command.RIGHT,
    119: Command.UP,
    32: Command.UP,
    13: Command.START,
    112: Command.PAUSE,
    114: Command.RESTART,
    113: Command.QUIT,
}
_CONTINUOUS = {Command.LEFT, Command.RIGHT, Command.UP}
_HOLD_ORDER = (Command.LEFT, Command.RIGHT, Command.UP)
# Bridges the gap between key repeats when a terminal cannot report key-up.
_HOLD_SECONDS = 0.25
# Disambiguate keys, report press/repeat/release, and report letter keys too.
_ENABLE_KEY_EVENTS = "\x1b[>11u"
_DISABLE_KEY_EVENTS = "\x1b[<u"


class KeyboardInput:
    """Turns keypresses into commands, and keeps held keys going."""

    def __init__(self) -> None:
        self._fd: int | None = None
        self._previous: list | None = None
        self._pending = ""
        self._held: set[Command] = set()
        self._pulsed: set[Command] = set()
        self._until: dict[Command, float] = {}

    def commands_from(self, text: str) -> list[Command]:
        """Translate ``text`` and any keys that are still held down."""
        one_shots: list[Command] = []
        self._pulsed.clear()
        self._consume(text, one_shots)
        self._expire()
        commands = [
            command
            for command in _HOLD_ORDER
            if command in self._held or command in self._pulsed
        ]
        commands.extend(one_shots)
        return commands

    def open(self) -> None:
        """Read keys as they arrive, including key release when the terminal can send it."""
        self._fd = sys.stdin.fileno()
        self._previous = termios.tcgetattr(self._fd)
        tty.setcbreak(self._fd)
        sys.stdout.write(_ENABLE_KEY_EVENTS)
        sys.stdout.flush()

    def close(self) -> None:
        """Restore the terminal."""
        sys.stdout.write(_DISABLE_KEY_EVENTS)
        sys.stdout.flush()
        if self._fd is not None and self._previous is not None:
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._previous)
        self._fd = None
        self._previous = None

    def read_available(self) -> str:
        """Return keys already typed, without waiting."""
        if self._fd is None:
            return ""
        chunks = []
        while select.select([self._fd], [], [], 0)[0]:
            piece = os.read(self._fd, 32)
            if not piece:
                break
            chunks.append(piece.decode("utf-8", "ignore"))
        return "".join(chunks)

    def wait(self, timeout: float) -> None:
        """Wait until a key arrives or ``timeout`` seconds pass."""
        if self._fd is None or timeout <= 0:
            return
        select.select([self._fd], [], [], timeout)

    def _consume(self, text: str, one_shots: list[Command]) -> None:
        data = self._pending + text
        self._pending = ""
        index = 0
        while index < len(data):
            if data[index] != "\x1b":
                self._legacy(data[index], one_shots)
                index += 1
                continue
            if index + 1 >= len(data):
                self._pending = data[index:]
                return
            if data[index + 1] == "[":
                end = _csi_end(data, index)
                if end is None:
                    self._pending = data[index:]
                    return
                self._csi(data[index:end], one_shots)
                index = end
                continue
            if data[index + 1] == "O":
                if index + 2 >= len(data):
                    self._pending = data[index:]
                    return
                command = _ARROWS.get(data[index + 2])
                if command is not None:
                    self._event(command, "press", one_shots)
                index += 3
                continue
            index += 1

    def _legacy(self, char: str, one_shots: list[Command]) -> None:
        command = _LETTERS.get(char.lower())
        if command is not None:
            self._event(command, "legacy", one_shots)

    def _csi(self, sequence: str, one_shots: list[Command]) -> None:
        final = sequence[-1]
        body = sequence[2:-1]
        if final == "u":
            self._coded_key(body, one_shots)
            return
        command = _ARROWS.get(final)
        if command is not None:
            self._event(command, _event_type(body), one_shots)

    def _coded_key(self, body: str, one_shots: list[Command]) -> None:
        fields = body.split(";")
        key_text = fields[0].split(":")[0] if fields else ""
        if not key_text.isdigit():
            return
        command = _CODES.get(int(key_text))
        if command is None:
            return
        event = _event_type(fields[1]) if len(fields) > 1 else "press"
        self._event(command, event, one_shots)

    def _event(self, command: Command, event: str, one_shots: list[Command]) -> None:
        if command is Command.DOWN:
            return
        if command in _CONTINUOUS:
            if event == "release":
                self._held.discard(command)
                self._until.pop(command, None)
                return
            self._pulsed.add(command)
            self._held.add(command)
            if event == "legacy":
                self._until[command] = time.monotonic() + _HOLD_SECONDS
            else:
                self._until.pop(command, None)
            return
        if event in {"press", "legacy"}:
            one_shots.append(command)

    def _expire(self) -> None:
        now = time.monotonic()
        for command, deadline in list(self._until.items()):
            if now >= deadline:
                self._held.discard(command)
                del self._until[command]


def _csi_end(data: str, start: int) -> int | None:
    index = start + 2
    while index < len(data):
        if 0x40 <= ord(data[index]) <= 0x7E:
            return index + 1
        index += 1
    return None


def _event_type(field: str) -> str:
    parts = field.split(":")
    if len(parts) < 2 or parts[1] == "":
        return "press"
    if parts[-1] == "2":
        return "repeat"
    if parts[-1] == "3":
        return "release"
    return "press"
