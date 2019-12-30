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
    FAKE = 1
    AB = 2
    ABC = 3


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class MoveType(Enum):
    ACTION = 1
    MOVEMENT = 2
    END_TURN = 3
    XP_EXCHANGE = 4


class TileCategories(Enum):
    STATIC = 1
    DYNAMIC = 2


class TileType(Enum):
    SAFE = 1
    MARSH = 2
    RIVER = 3
    HOSPITAL = 4
    SHOP = 5
    PORTAL = 6
    TREASURE = 7


class BorderWallType(Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


class XPExchangeType(Enum):
    REVEAL_HOSPITAL = 1
    REVEAL_SHOP = 2
    REVEAL_OBSTACLE = 3
    HEAL_INSTANTLY = 4
