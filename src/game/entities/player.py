"""The character the player controls."""

from game.entities.entity import Entity


class Player(Entity):
    """A side-view runner. Faces the last direction they walked."""

    def __init__(self) -> None:
        super().__init__(name="player")
        self.facing = "right"

    def turn(self) -> None:
        """Face left or right when the current step has horizontal speed."""
        if self.velocity.x > 0:
            self.facing = "right"
        elif self.velocity.x < 0:
            self.facing = "left"
