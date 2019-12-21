from move import Move
from datatypes import Direction, MoveType


class Movement(Move):
    def __init__(self, direction: Direction, is_mandatory=False):
        super().__init__(is_mandatory)
        self.direction = direction
        self.move_type = MoveType.MOVEMENT

    def affect_player(self, player):
        player.move(self.direction)

    def description(self):
        return f"Move 1 space in the {self.direction.name} direction."
