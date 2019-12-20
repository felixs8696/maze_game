class ItemAlreadyHeldError(Exception):
    pass


class NoItemHeldError(Exception):
    pass


class TreasureAlreadyHeldError(Exception):
    pass


class NoTreasureHeldError(Exception):
    pass


class MoveBlockedByWall(Exception):
    pass


class ExitFound(Exception):
    pass


class GameOver(Exception):
    pass
