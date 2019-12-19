import random

from datatypes import StatusType, ItemType, TreasureType, PortalType, Direction, MoveType
from move import Move
from movement import Movement
from tiles import Tile
from location import Location
from utils import ask_for_options
from exceptions import MoveBlockedByWall
from actions import Fight, EndTurn

from exceptions import ItemAlreadyHeldError, NoItemHeldError, TreasureAlreadyHeldError, NoTreasureHeldError


class Player:
    def __init__(self, initial_location: Location, name: str, board):
        self.name = name
        self.status = StatusType.HEALTHY
        self.item = None
        self.treasure = None
        self.can_move = True
        self.active = False
        self.location = initial_location
        self.lose_next_turn = False
        self.board = board

    def begin_turn(self):
        if self.lose_next_turn:
            print(f"Sorry {self.name}, you have lost your turn.")
            self.lose_next_turn = False
            self.end_turn()
        else:
            self.active = True

    def is_turn_over(self, other_players):
        if not self.active:
            return True
        possible_actions = self.get_possible_actions(other_players=other_players)
        no_more_actions = len(possible_actions) == 0
        only_end_turn_remaining = len(possible_actions) == 1 and possible_actions[0].move_type == MoveType.END_TURN
        if not self.can_move and (no_more_actions or only_end_turn_remaining):
            print(f"{self.name}'s can't move and his/her only remaining action is to end his/her turn.")
            return True

    def end_turn(self):
        if self.can_move:
            print(f"{self.name} must move at least once this turn.")
        else:
            self.active = False
            self.can_move = True

    def move(self, direction: Direction):
        try:
            self.location.move(direction, self.board.inner_walls)
            self.can_move = False
            print(f'{self.name} moves {direction.name}.')
        except MoveBlockedByWall as e:
            print(f'{self.name} cannot move {direction.name}. Blocked by wall.')
            self.can_move = True

    def execute_mandatory_actions_and_get_remaining(self, game_tile_actions):
        remaining_actions = []
        for action in game_tile_actions:
            if action.is_mandatory:
                action.affect_player(self)
            else:
                remaining_actions.append(action)
        return remaining_actions

    def execute_move(self, move: Move):
        move.affect_player(self)

    def get_colliding_players(self, other_players):
        colliding_players = []
        for player in other_players:
            if self.location == player.location:
                colliding_players.append(player)
        return colliding_players

    def _get_possible_fights(self, other_players):
        possible_fights = []
        if self.status == StatusType.HEALTHY:
            colliding_players = self.get_colliding_players(other_players=other_players)
            if len(colliding_players) > 0:
                for i in range(len(colliding_players)):
                    other_player = colliding_players[i]
                    if not other_player.is_injured():
                        possible_fights.append(Fight(other_player=colliding_players[i]))
        return possible_fights

    def get_possible_actions(self, other_players):
        possible_actions = [EndTurn()]
        if self.item is not None:
            possible_actions.extend(self.item.get_actions())
        possible_fights = self._get_possible_fights(other_players=other_players)
        possible_actions.extend(possible_fights)
        return possible_actions

    def request_move(self, other_players) -> Move:
        possible_movements = []
        if self.can_move:
            possible_movements = [Movement(Direction.UP), Movement(Direction.DOWN),
                                  Movement(Direction.LEFT), Movement(Direction.RIGHT)]
        possible_actions = self.get_possible_actions(other_players=other_players)
        possible_moves = possible_movements + possible_actions

        def get_invalid_move_msg(move_choice, possible_choices):
            return f"{move_choice} is not a valid selection. " \
                   f"Please select one of the following numbers: {possible_choices}"

        move_index = ask_for_options(possible_moves)
        valid_move = False
        range_of_possible_moves = range(len(possible_moves))
        while not valid_move:
            try:
                if int(move_index) in range_of_possible_moves:
                    valid_move = True
                else:
                    print(get_invalid_move_msg(move_index, range_of_possible_moves))
            except ValueError:
                print(get_invalid_move_msg(move_index, range_of_possible_moves))

        return possible_moves[int(move_index)]

    def can_acquire_item(self):
        return self.item is None

    def acquire_item(self, item: ItemType):
        if self.item is None:
            self.item = item
        else:
            raise ItemAlreadyHeldError

    def use_item(self):
        if self.item == ItemType.RUSTY_BULLET:
            actions = self.item.get_actions()
            action_index = ask_for_options(actions)
            actions[action_index].affect_player(self)

    def drop_item(self):
        if self.item is not None:
            self.item = None
            print(f"{self.name} has dropped his/her {self.item}.")
        else:
            print(f"{self.name} has no {item} to drop.")
            raise NoItemHeldError

    def drop_treasure(self):
        if self.treasure is not None:
            self.treasure = None
            print(f"{self.name} has dropped his/her treasure.")
        else:
            print(f"{self.name} has no treasure to drop.")
            raise NoTreasureHeldError

    def teleport_to(self, location: Location):
        self.location.teleport(location)
        print(f"{self.name} has entered and exited a portal.")

    def flush_one_tile(self, direction: Direction):
        try:
            self.location.move(direction, self.board.inner_walls)
            print(f"{self.name} is flushed by the river one tile.")
        except MoveBlockedByWall as e:
            print(f"The river tries to flush {self.name}, but a wall prevents him/her from moving.")

    def get_injured(self):
        print(f"{self.name} has been injured.")
        self.status = StatusType.INJURED

    def is_injured(self):
        return self.status == StatusType.INJURED

    def lose_turn(self):
        self.lose_next_turn = True
        print(f"{self.name} loses his/her turn.")

    def heal(self):
        self.status = StatusType.HEALTHY
        print(f"{self.name} is healed and is now {self.status.name}.")

    def do_nothing(self):
        print(f'{self.name} does nothing')

    def announce_safety(self):
        print(f'{self.name} is safe.')

    def show_colliding_players(self, other_players):
        colliding_players = self.get_colliding_players(other_players=other_players)
        for player in colliding_players:
            status = player.status
            article = 'an' if status.name[0].lower() in 'aeiou' else 'a'
            print(f"{self.name} has stumbled across {article} {status} {player.name}.")

    def fight(self, other_player):
        dice = range(6)
        attacker_roll = random.choice(dice)
        defender_roll = random.choice(dice)

        print(f"{self.name} attacks {other_player.name}.")
        if attacker_roll >= defender_roll:
            print(f"{self.name} takes {other_player.name} by surprise and wins the fight.")
            other_player.get_injured()
        else:
            print(f"{other_player.name} fights back and overcomes {self.name}.")
            self.get_injured()
