from game.render import FrameRenderer
from game.scenes import PlayScene
from game.input import Command


def test_renderer_keeps_each_presented_frame() -> None:
    renderer = FrameRenderer()

    renderer.draw("Play")
    renderer.draw("player @ (0, 0)")
    renderer.present()
    renderer.clear()
    renderer.draw("discarded")
    renderer.clear()
    renderer.draw("Play")
    renderer.present()

    assert renderer.frames == [
        ("Play", "player @ (0, 0)"),
        ("Play",),
    ]


def test_play_scene_draws_the_player_in_the_room() -> None:
    scene = PlayScene()
    renderer = FrameRenderer()

    scene.render(renderer)
    renderer.present()
    scene.handle_input([Command.RIGHT, Command.UP])
    scene.update(1)
    renderer.clear()
    scene.render(renderer)
    renderer.present()

    start, moved = renderer.frames
    assert len(start) == 12
    assert len(start[0]) == 21
    assert start[0] == "#" + " " * 20
    assert start[11] == "#" * 21
    assert _player_at(start) == (2, 10)
    assert _player_at(moved) == (3, 7)


def _player_at(frame: tuple[str, ...]) -> tuple[int, int]:
    for y, row in enumerate(frame):
        x = row.find("@")
        if x != -1:
            return (x, y)
    raise AssertionError("player is missing from the frame")
