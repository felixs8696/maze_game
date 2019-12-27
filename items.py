from abc import ABC, abstractmethod

from actions import ShootBullet, Heal, DropItem
from datatypes import Direction, ItemType


class Item(ABC):

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def get_actions(self, player, other_players, board):
        pass


class RustyBullet(Item):

    def __init__(self):
        self.type = ItemType.RUSTY_BULLET

    def __str__(self):
        return "Rusty Bullet"

    def get_actions(self, player, other_players, board):
        return [DropItem(),
                ShootBullet(direction=Direction.UP, other_players=other_players, board=board),
                ShootBullet(direction=Direction.DOWN, other_players=other_players, board=board),
                ShootBullet(direction=Direction.LEFT, other_players=other_players, board=board),
                ShootBullet(direction=Direction.RIGHT, other_players=other_players, board=board)]


class FirstAidKit(Item):

    def __init__(self):
        self.type = ItemType.FIRST_AID_KIT

    def __str__(self):
        return "First Aid Kit"

    def get_actions(self, player, other_players, board):
        return [DropItem(), Heal(source=self.type)]


class PileOfJunk(Item):

    def __init__(self):
        self.type = ItemType.PILE_OF_JUNK

    def __str__(self):
        return "Pile of Junk"

    def get_actions(self, player, other_players, board):
        return [DropItem()]
