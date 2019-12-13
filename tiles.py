from abc import ABC, abstractmethod
from typing import List, Tuple

from .items import RustyBullet, FirstAidKit, PileOfJunk
from .datatypes import PortalType, Direction
from .actions import Action, DoNothing, LoseTurn, BuyItem, Heal, Teleport, Flush
from .location import Location


class Tile(ABC):

    def __init__(self, location: Location):
        self.location = location

    @abstractmethod
    def get_actions(self):
        pass

    @abstractmethod
    def description(self):
        pass


class Safe(Tile):

    def get_actions(self) -> List[Action]:
        return [DoNothing(is_mandatory=True)]

    def description(self):
        return f"You are safe."


class Marsh(Tile):

    def get_actions(self) -> List[Action]:
        return [LoseTurn(is_mandatory=True)]

    def description(self):
        return f"You lose your next turn."


class Shop(Tile):

    def __init__(self, location: Location):
        super().__init__(location)
        self.items = [RustyBullet(), FirstAidKit(), PileOfJunk()]

    def get_actions(self) -> List[Action]:
        return [DoNothing(), BuyItem(items=self.items)]

    def description(self):
        return f"You have entered a shop."


class Hospital(Tile):

    def get_actions(self) -> List[Action]:
        return [DoNothing(), Heal()]

    def description(self):
        return f"You have entered the hospital."


class Portal(Tile, ABC):

    def __init__(self, location: Location, exit_portal, portal_type: PortalType):
        super().__init__(location)
        self.type = portal_type
        self.exit_portal = exit_portal

    def get_actions(self) -> List[Action]:
        return [Teleport(self.exit_portal, is_mandatory=True)]

    def description(self):
        return f"You have landed on a portal tile."


class River(Tile, ABC):

    def __init__(self, location: Location, direction: Direction):
        super().__init__(location)
        self.direction = direction

    def get_actions(self) -> List[Action]:
        return [Flush(self.direction, is_mandatory=True)]

    def description(self):
        return f"You have landed on a river tile."
