from abc import ABC, abstractmethod


class Move(ABC):

    def __init__(self, is_mandatory=False):
        self.is_mandatory = is_mandatory

    @abstractmethod
    def affect_player(self, player):
        pass

    @abstractmethod
    def description(self) -> str:
        pass
