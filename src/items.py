from abc import ABC, abstractmethod

from src.actions import ShootBullet, Heal, DropItem
from src.datatypes import Direction, ItemType


class Item(ABC):

    def __init__(self):
        self.drop_item_action = DropItem()

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def get_actions(self, player, other_players, board):
        pass


class RustyBullet(Item):

    def __init__(self):
        self.type = ItemType.RUSTY_BULLET
        super().__init__()

    def __str__(self):
        return "Rusty Bullet"

    def get_actions(self, player, other_players, board):
        actions = [ShootBullet(direction=Direction.UP, other_players=other_players, board=board),
                   ShootBullet(direction=Direction.DOWN, other_players=other_players, board=board),
                   ShootBullet(direction=Direction.LEFT, other_players=other_players, board=board),
                   ShootBullet(direction=Direction.RIGHT, other_players=other_players, board=board)]
        if not player.acquired_item_this_turn:
            actions.append(self.drop_item_action)
        return actions


class FirstAidKit(Item):

    def __init__(self):
        self.type = ItemType.FIRST_AID_KIT
        super().__init__()

    def __str__(self):
        return "First Aid Kit"

    def get_actions(self, player, other_players, board):
        actions = [Heal(source=self.type)]
        if not player.acquired_item_this_turn:
            actions.append(self.drop_item_action)
        return actions


class PileOfJunk(Item):

    def __init__(self):
        self.type = ItemType.PILE_OF_JUNK
        super().__init__()

    def __str__(self):
        return "Pile of Junk"

    def get_actions(self, player, other_players, board):
        actions = []
        if not player.acquired_item_this_turn:
            actions.append(self.drop_item_action)
        return actions
