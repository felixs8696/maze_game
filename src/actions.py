import json
import numpy as np

from abc import abstractmethod

from src.move import Move
from src.utils import get_yes_or_no_response, response_is_yes, prompt_real_dice_roll_result
from src.datatypes import Direction, MoveType, StatusType, TileType, XPExchangeType
from src.location import Location


class Action(Move):

    def __init__(self, is_mandatory=False):
        super().__init__(is_mandatory)
        self.move_type = MoveType.ACTION

    @abstractmethod
    def description(self):
        pass


class BuyItem(Action):

    def __init__(self, items, item_map: dict, is_mandatory=False):
        super().__init__(is_mandatory)
        self.items = items
        self.item_map = item_map

    def affect_player(self, player):
        if player.has_item():
            print(f"You already have an item ({player.item}) and you cannot hold multiple items.")
            return None

        print(f"Random Item Shop Catalog: {json.dumps(self.item_map, default=lambda x: str(x))}")

        if player.auto_rng:
            chosen_item = np.random.choice(self.items)
        else:
            chosen_item = None
            while chosen_item is None:
                try:
                    number = prompt_real_dice_roll_result(player)
                    chosen_item = self.item_map[number]
                except KeyError:
                    print(f"Invalid dice roll. The shop only has the following items: "
                          f"{json.dumps(self.item_map, indent=2)}")
                    print(f"Please enter a dice roll that is one of these values: {self.item_map.keys()}")
        print(f"Thank you for your purchase!")
        player.acquire_item(chosen_item)

    def description(self):
        return f"Buy a randomly chosen item from the shop."


class Teleport(Action):

    def __init__(self, exit_location, is_mandatory=False):
        super().__init__(is_mandatory)
        self.exit_location = exit_location

    def affect_player(self, player):
        player.teleport_to(self.exit_location)

    def description(self):
        return f"You have been teleported by a portal."


class Flush(Action):

    def __init__(self, direction: Direction, is_mandatory=False):
        super().__init__(is_mandatory)
        self.direction = direction

    def affect_player(self, player):
        player.flush_one_tile(self.direction)

    def description(self):
        return f"You have been flushed by the river."


class Heal(Action):

    def __init__(self, source, is_mandatory=False):
        super().__init__(is_mandatory)
        self.source = source

    def affect_player(self, player):
        if not player.is_injured():
            print(f"You are already healthy.")

        if self.source == TileType.HOSPITAL:
            player.lose_turn()
        player.heal()

    def description(self):
        if self.source == TileType.HOSPITAL:
            return f"Spend your next turn in the hospital to heal."
        return f"Heal yourself."


class DropItem(Action):

    def affect_player(self, player):
        player.drop_item()

    def description(self):
        return f"Drop your item."


class AcquireTreasure(Action):

    def affect_player(self, player):
        player.acquire_treasure()

    def description(self):
        return f"Acquire treasure."


class DropTreasure(Action):

    def affect_player(self, player):
        player.drop_treasure()

    def description(self):
        return f"Drop your treasure."


class LoseTurn(Action):

    def affect_player(self, player):
        player.lose_turn()

    def description(self):
        return f"You lose your next turn."


class ShootBullet(Action):

    def __init__(self, direction: Direction, other_players, board, is_mandatory=False):
        super().__init__(is_mandatory)
        self.direction = direction
        self.other_players = other_players
        self.board = board

    def _get_shot_destination(self, current_player, direction):
        if direction == Direction.UP:
            shot_destination = Location(x=current_player.location.x, y=current_player.location.y + 3)
        elif direction == Direction.DOWN:
            shot_destination = Location(x=current_player.location.x, y=current_player.location.y - 3)
        elif direction == Direction.LEFT:
            shot_destination = Location(x=current_player.location.x - 3, y=current_player.location.y)
        elif direction == Direction.RIGHT:
            shot_destination = Location(x=current_player.location.x + 3, y=current_player.location.y)
        else:
            raise Exception(f"Shooting in invalid direction: {self.direction}")

        first_player_hit = None
        for other_player in self.other_players:
            if first_player_hit is None:
                if direction == Direction.UP:
                    if current_player.location.x == other_player.location.x and \
                            0 < (other_player.location.y - current_player.location.y) <= 3:
                        shot_destination = other_player.location
                        first_player_hit = other_player
                elif direction == Direction.DOWN:
                    if current_player.location.x == other_player.location.x and \
                            0 < (current_player.location.y - other_player.location.y) <= 3:
                        shot_destination = other_player.location
                        first_player_hit = other_player
                elif direction == Direction.LEFT:
                    if 0 < (current_player.location.x - other_player.location.x) <= 3 and \
                            other_player.location.y == current_player.location.y:
                        shot_destination = other_player.location
                        first_player_hit = other_player
                elif direction == Direction.RIGHT:
                    if 0 < (other_player.location.x - current_player.location.x) <= 3 and \
                            other_player.location.y == current_player.location.y:
                        shot_destination = other_player.location
                        first_player_hit = other_player
                else:
                    raise Exception(f"Shooting in invalid direction: {self.direction}")
        return shot_destination, first_player_hit

    def affect_player(self, player):
        shot_destination, first_player_hit = self._get_shot_destination(player, self.direction)
        if player.location.no_walls_block_straight_line_location(location=shot_destination,
                                                                 walls=self.board.inner_walls,
                                                                 board_height=self.board.height,
                                                                 board_width=self.board.width):
            if first_player_hit is not None:
                if first_player_hit.status != StatusType.INJURED:
                    print(f"{player.name} successfully shoots and injures {first_player_hit.name}.")
                    first_player_hit.get_injured()
                else:
                    print(f"{player.name} shoots {first_player_hit.name}, but {first_player_hit.name} "
                          f"is already injured.")
            else:
                print(f"{player.name} shoots 3 spaces {self.direction.name}, but hits nothing.")
        else:
            print(f"{player.name} shoots {self.direction.name}, but hits a wall.")
        print(f"{player.name} has lost his/her Rusty Bullet.")
        player.lose_item()

    def description(self):
        return f"Shoot up to 3 spaces in the {self.direction.name} direction (not including your current location)."


class Fight(Action):

    def __init__(self, other_player, auto_play=False, is_mandatory=False):
        super().__init__(is_mandatory)
        self.auto_play = auto_play
        self.other_player = other_player

    def affect_player(self, player):
        player.fight(self.other_player, auto_play=self.auto_play)

    def description(self):
        return f"Fight {self.other_player.name}."


class EndTurn(Action):

    def __init__(self):
        super().__init__(is_mandatory=False)
        self.move_type = MoveType.END_TURN

    def affect_player(self, player):
        player.end_turn()

    def description(self):
        return f"You end your turn."


class AddPlayerXP(Action):

    def __init__(self, amount: int = 0, is_mandatory=True):
        super().__init__(is_mandatory)
        self.amount = amount

    def affect_player(self, player):
        player.add_xp(self.amount)

    def description(self):
        return f"You have been teleported by a portal."


class XPExchange(Action):

    def __init__(self, is_mandatory=False):
        super().__init__(is_mandatory)
        self.xp_cost = 0
        self.move_type = MoveType.XP_EXCHANGE
        self.exchange_type = None

    @abstractmethod
    def description(self):
        pass


class RevealClosestHospital(XPExchange):

    def __init__(self, is_mandatory=False):
        super().__init__(is_mandatory)
        self.xp_cost = 3
        self.exchange_type = XPExchangeType.REVEAL_HOSPITAL

    def affect_player(self, player):
        player.spend_xp(self.xp_cost)
        player.reveal_closest_hospital()

    def description(self):
        return f"Spend {self.xp_cost} XP to reveal the relative location of the nearest hospital. " \
            f"(WARNING: You can only do this during the entire game)"


class RevealClosestShop(XPExchange):

    def __init__(self, is_mandatory=False):
        super().__init__(is_mandatory)
        self.xp_cost = 3
        self.exchange_type = XPExchangeType.REVEAL_SHOP

    def affect_player(self, player):
        player.spend_xp(self.xp_cost)
        player.reveal_closest_shop()

    def description(self):
        return f"Spend {self.xp_cost} XP to reveal the relative location of the nearest shop " \
            f"(WARNING: You can only do this during the entire game)."


class RevealObstacle(XPExchange):

    def __init__(self, is_mandatory=False):
        super().__init__(is_mandatory)
        self.xp_cost = 5
        self.exchange_type = XPExchangeType.REVEAL_OBSTACLE

    def affect_player(self, player):
        player.spend_xp(self.xp_cost)
        player.reveal_obstacle()

    def description(self):
        return f"Spend {self.xp_cost} XP to reveal all information about a tile you most recently encountered."


class HealInstantlyWithXP(XPExchange):

    def __init__(self, is_mandatory=False):
        super().__init__(is_mandatory)
        self.xp_cost = 7
        self.exchange_type = XPExchangeType.HEAL_INSTANTLY

    def affect_player(self, player):
        player.spend_xp(self.xp_cost)
        player.heal()

    def description(self):
        return f"Spend {self.xp_cost} XP to heal instantly."


def ask_for_options(actions):
    actions_options = ""
    range_of_actions = range(len(actions))
    for i in range_of_actions:
        actions_options += f"({i}) {actions[i].description()}\n"
    print(f"{actions_options}")
