from game.entities import Entity, Vec2


def test_entity_moves_by_velocity_times_step() -> None:
    entity = Entity(name="player", velocity=Vec2(2, -1))

    entity.update(0.5)

    assert entity.position.x == 1
    assert entity.position.y == -0.5


def test_entity_stays_put_when_velocity_is_zero() -> None:
    entity = Entity(name="player", position=Vec2(3, 4))

    entity.update(1)

    assert entity.position.x == 3
    assert entity.position.y == 4
