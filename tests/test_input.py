from game.input import Command, ScriptedInput, parse_command


def test_parse_command_accepts_the_actions() -> None:
    assert parse_command("start") is Command.START
    assert parse_command("QUIT") is Command.QUIT
    assert parse_command(" up ") is Command.UP
    assert parse_command("down") is Command.DOWN
    assert parse_command("left") is Command.LEFT
    assert parse_command("right") is Command.RIGHT
    assert parse_command("pause") is Command.PAUSE
    assert parse_command("restart") is Command.RESTART


def test_parse_command_rejects_unknown_text() -> None:
    assert parse_command("jump") is None
    assert parse_command("") is None


def test_scripted_input_returns_one_frame_at_a_time() -> None:
    source = ScriptedInput(
        [
            [Command.START],
            [Command.RIGHT, Command.UP],
        ]
    )

    assert source.poll() == [Command.START]
    assert source.poll() == [Command.RIGHT, Command.UP]
    assert source.poll() == []
