"""An object with a position and a velocity."""

from dataclasses import dataclass, field


@dataclass
class Vec2:
    """A 2D amount. Up is positive y."""

    x: float = 0.0
    y: float = 0.0


@dataclass
class Entity:
    """Something the simulation moves each frame."""

    name: str
    position: Vec2 = field(default_factory=Vec2)
    velocity: Vec2 = field(default_factory=Vec2)

    def update(self, dt: float) -> None:
        """Advance the position by velocity over ``dt``."""
        self.position.x += self.velocity.x * dt
        self.position.y += self.velocity.y * dt
