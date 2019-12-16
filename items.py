from abc import ABC, abstractmethod

from actions import ShootBullet, Heal, DoNothing
from datatypes import Direction


class Item(ABC):

    @staticmethod
    @abstractmethod
    def get_actions(**args):
        pass


class RustyBullet(Item):

    @staticmethod
    def get_actions():
        return [ShootBullet(Direction.UP), ShootBullet(Direction.DOWN),
                ShootBullet(Direction.LEFT), ShootBullet(Direction.RIGHT)]


class FirstAidKit(Item):

    @staticmethod
    def get_actions():
        return [Heal()]


class PileOfJunk(Item):

    @staticmethod
    def get_actions():
        return [DoNothing()]
