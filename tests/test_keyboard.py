from game.input.command import Command
from game.input.keyboard import KeyboardInput


def test_letters_and_arrows_become_commands() -> None:
    assert KeyboardInput().commands_from("d") == [Command.RIGHT]
    assert KeyboardInput().commands_from("") == []
    assert KeyboardInput().commands_from("w") == [Command.UP]
    assert KeyboardInput().commands_from("\x1b[D") == [Command.LEFT]
    assert KeyboardInput().commands_from(" ") == [Command.UP]
    assert KeyboardInput().commands_from("\r") == [Command.START]
    assert KeyboardInput().commands_from("p") == [Command.PAUSE]
    assert KeyboardInput().commands_from("r") == [Command.RESTART]
    assert KeyboardInput().commands_from("q") == [Command.QUIT]


def test_holding_a_direction_keeps_it_until_the_key_is_released() -> None:
    keyboard = KeyboardInput()

    assert keyboard.commands_from("d") == [Command.RIGHT]
    assert keyboard.commands_from("") == [Command.RIGHT]

    assert keyboard.commands_from("\x1b[100;1:3u") == []
    assert keyboard.commands_from("") == []


def test_a_tap_moves_on_the_frame_the_key_goes_down_and_up() -> None:
    keyboard = KeyboardInput()

    assert keyboard.commands_from("\x1b[100u\x1b[100;1:3u") == [Command.RIGHT]
    assert keyboard.commands_from("") == []


def test_holding_an_arrow_keeps_it_until_release() -> None:
    keyboard = KeyboardInput()

    assert keyboard.commands_from("\x1b[C") == [Command.RIGHT]
    assert keyboard.commands_from("") == [Command.RIGHT]
    assert keyboard.commands_from("\x1b[1;1:3C") == []


def test_jump_and_move_in_one_read_are_both_commands() -> None:
    assert KeyboardInput().commands_from("dw") == [Command.RIGHT, Command.UP]
    assert KeyboardInput().commands_from("\x1b[100u\x1b[119u") == [Command.RIGHT, Command.UP]
    assert KeyboardInput().commands_from("\x1b[C ") == [Command.RIGHT, Command.UP]


def test_holding_jump_stays_until_release() -> None:
    keyboard = KeyboardInput()

    keyboard.commands_from("\x1b[119u")

    assert keyboard.commands_from("") == [Command.UP]
    assert keyboard.commands_from("\x1b[119;1:3u") == []


def test_pause_is_not_repeated_by_holding_the_key() -> None:
    keyboard = KeyboardInput()

    assert keyboard.commands_from("\x1b[112u") == [Command.PAUSE]
    assert keyboard.commands_from("\x1b[112;1:2u") == []
    assert keyboard.commands_from("") == []
