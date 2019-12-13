from enum import Enum


class StatusType(Enum):
    HEALTHY = 1
    INJURED = 2


class ItemType(Enum):
    RUSTY_BULLET = 1
    FIRST_AID_KIT = 2
    PILE_OF_JUNK = 3
    TREASURE_SCOPE = 4


class TreasureType(Enum):
    REAL = 1
    FAKE = 2
    EXPLOSIVE = 3


class PortalType(Enum):
    A = 1
    AB = 2
    ABC = 3


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    def __str__(self):
        if self.UP:
            return 'UP'
        if self.DOWN:
            return 'DOWN'
        if self.LEFT:
            return 'LEFT'
        if self.RIGHT:
            return 'RIGHT'


class MoveType(Enum):
    ACTION = 1
    MOVEMENT = 2
