import numpy as np
import uuid
import random
import time

from src.datatypes import StatusType, ItemType, Direction, MoveType
from src.move import Move
from src.movement import Movement
from src.location import Location
from src.utils import ask_for_options, display_options, get_yes_or_no_response, response_is_yes, \
    prompt_real_dice_roll_result
from src.exceptions import MoveBlockedByWall, ExitFound, GameOver
from src.actions import Fight, EndTurn, AcquireTreasure, DropTreasure

from src.exceptions import ItemAlreadyHeldError, NoItemHeldError, TreasureAlreadyHeldError, NoTreasureHeldError


class Player:
    def __init__(self, name: str = '', location: Location = None, board=None, item=None, has_treasure=False,
                 can_move=True, active=False, lose_next_turn=False, player_id=None, status=StatusType.HEALTHY,
                 auto_rng: bool = False):
        self.name = name
        self.location = location
        self.board = board
        self.item = item
        self.has_treasure = has_treasure
        self.can_move = can_move
        self.active = active
        self.lose_next_turn = lose_next_turn
        if player_id is None:
            self.player_id = uuid.uuid4()
        else:
            self.player_id = player_id
        self.status = status
        self.auto_rng = auto_rng

    def __eq__(self, other):
        return self.player_id == other.player_id

    @staticmethod
    def copy_from(player):
        return Player(name=player.name, location=player.location, board=player.board, item=player.item,
                      has_treasure=player.has_treasure, can_move=player.can_move, active=player.active,
                      lose_next_turn=player.lose_next_turn, player_id=player.player_id, status=player.status,
                      auto_rng=player.auto_rng)

    def begin_turn(self):
        if self.lose_next_turn:
            print(f"Sorry {self.name}, you have lost your turn.")
            self.can_move = False
            self.lose_next_turn = False
            self.end_turn()
        else:
            self.active = True
            self.can_move = True

    def is_turn_over(self, other_players, board, available_tile_actions):
        if not self.active:
            return True
        possible_actions = self.get_possible_actions(other_players=other_players,
                                                     board=board,
                                                     available_tile_actions=available_tile_actions)
        no_more_actions = len(possible_actions) == 0
        only_end_turn_remaining = len(possible_actions) == 1 and possible_actions[0].move_type == MoveType.END_TURN
        if not self.can_move and (no_more_actions or only_end_turn_remaining):
            # print(f"{self.name}'s can't move and his/her only remaining action is to end his/her turn.")
            return True

    def end_turn(self):
        if self.can_move:
            print(f"{self.name} must move at least once this turn.")
        else:
            self.active = False

    def move(self, direction: Direction):
        try:
            self.location.move(direction, self.board)
            self.can_move = False
            print(f'{self.name} moves {direction.name}.')
        except ExitFound as e:
            if self.has_treasure:
                raise GameOver(f"{self.name} has exited the maze with the treasure and won the game.")
            else:
                print(f"{self.name} has found an exit, but has no treasure.")
        except MoveBlockedByWall as e:
            print(f'{self.name} cannot move {direction.name}. Blocked by wall.')
            self.can_move = True

    def execute_mandatory_actions(self):
        tile = self.board.get_tile(self.location)
        game_tile_actions = tile.get_actions(self)
        for action in game_tile_actions:
            if action.is_mandatory:
                self.execute_move(action)

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

    def get_possible_actions(self, other_players, board, available_tile_actions):
        possible_actions = [EndTurn()]
        if self.item is not None:
            possible_actions.extend(self.item.get_actions(self, other_players, board))
        possible_actions.extend(self._get_possible_fights(other_players=other_players))
        possible_actions.extend(available_tile_actions)

        if self.has_treasure:
            possible_actions.extend([DropTreasure()])

        valid_possible_actions = []
        for i in range(len(possible_actions)):
            if not (self.has_treasure and isinstance(possible_actions[i], AcquireTreasure)):
                valid_possible_actions.append(possible_actions[i])
        return valid_possible_actions

    def request_move(self, other_players, board, available_tile_actions, auto_play=False, auto_turn_time_secs=1) -> Move:
        possible_movements = []
        if self.can_move:
            possible_movements = [Movement(Direction.UP), Movement(Direction.DOWN),
                                  Movement(Direction.LEFT), Movement(Direction.RIGHT)]
        possible_actions = self.get_possible_actions(other_players=other_players,
                                                     board=board,
                                                     available_tile_actions=available_tile_actions)
        possible_moves = possible_movements + possible_actions

        def get_invalid_move_msg(move_choice, possible_choices):
            return f"{move_choice} is not a valid selection. " \
                f"Please select one of the following numbers: {possible_choices}"

        valid_move = False
        range_of_possible_moves = range(len(possible_moves))
        move_index = None

        if not auto_play:
            while not valid_move:
                print(f"\n{self.name} may choose one of the following moves.")
                move_index = ask_for_options(possible_moves)
                try:
                    if int(move_index) in range_of_possible_moves:
                        valid_move = True
                    else:
                        print(get_invalid_move_msg(move_index, tuple(range_of_possible_moves)))
                except ValueError:
                    print(get_invalid_move_msg(move_index, tuple(range_of_possible_moves)))
        else:
            display_options(possible_moves)

            invalid_move = True
            while invalid_move:
                move_index = random.choice(range(len(possible_moves)))
                chosen_move = possible_moves[move_index]
                if not isinstance(chosen_move, DropTreasure):
                    invalid_move = False
                if not (isinstance(chosen_move, EndTurn) and self.can_move):
                    invalid_move = False
            time.sleep(auto_turn_time_secs)
            print(f"Move chosen: {move_index}")

        return possible_moves[int(move_index)]

    def has_item(self):
        return self.item is not None

    def acquire_treasure(self):
        x, y = self.location.get_coordinates()
        tile = self.board.grid[x][y]
        assert tile.has_treasure()
        if not self.has_treasure:
            print(f"{self.name} has acquired a pile of treasure.")
            self.has_treasure = True
            tile.remove_treasure()
        else:
            raise TreasureAlreadyHeldError

    def acquire_item(self, item: ItemType):
        if not self.has_item():
            print(f"{self.name} has acquired a {str(item)}.")
            self.item = item
        else:
            raise ItemAlreadyHeldError

    def lose_item(self):
        self.item = None

    def drop_item(self):
        if self.item is not None:
            print(f"{self.name} has dropped his/her {self.item}.")
            self.lose_item()
        else:
            print(f"{self.name} has no {item} to drop.")
            raise NoItemHeldError

    def drop_treasure(self):
        x, y = self.location.get_coordinates()
        tile = self.board.grid[x][y]
        if self.has_treasure:
            self.has_treasure = False
            tile.add_treasure()
            print(f"{self.name} has dropped his/her pile of treasure.")
        else:
            print(f"{self.name} has no treasure to drop.")
            raise NoTreasureHeldError

    def teleport_to(self, location: Location):
        self.location.teleport(location)

    def flush_one_tile(self, direction: Direction):
        try:
            self.location.move(direction, self.board)
            print(f"{self.name} is flushed by the river one tile.")
        except ExitFound as e:
            if self.has_treasure:
                raise GameOver(f"{self.name} has been flushed out of the maze with the treasure and won the game.")
            else:
                print(f"{self.name} has been flushed into an exit, but has no treasure, so does not move farther.")
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

    def show_colliding_players(self, other_players):
        colliding_players = self.get_colliding_players(other_players=other_players)
        for player in colliding_players:
            status = player.status
            article = 'an' if status.name[0].lower() in 'aeiou' else 'a'
            print(f"{self.name} has stumbled across {article} {status.name} {player.name}.")

    def fight(self, other_player, auto_play=False):
        print(f"{self.name} surprises {other_player.name}, so {self.name} has attacker's advantage.")
        if self.has_item() and self.item.type == ItemType.RUSTY_BULLET:
            if not auto_play:
                prompt = f"Would you like to use your {str(self.item)} to automatically win the fight " \
                    f"(Choose 'n' to take a chance with hand to hand combat)? (y/n): "
                choose_to_act = get_yes_or_no_response(prompt)
                use_bullet = response_is_yes(choose_to_act)
            else:
                use_bullet = random.choice([True, False])
            if use_bullet:
                print(f"{self.name} shoots and injures {other_player.name}.")
                if other_player.has_item() and other_player.item.type == ItemType.RUSTY_BULLET:
                    print(f"{other_player.name} has a {str(other_player.item)}, but is taken by surprise, "
                          f"so cannot use it.")
                other_player.get_injured()
                return None
        if self.auto_rng:
            dice = range(6)
            attacker_roll = np.random.choice(dice) + 1
            defender_roll = np.random.choice(dice) + 1
        else:
            attacker_roll = prompt_real_dice_roll_result(self)
            defender_roll = prompt_real_dice_roll_result(other_player)

        print(
            f"{self.name} attacks {other_player.name}. {self.name} attacks with a power level of ({attacker_roll}/6). "
            f"{other_player.name} defends with a power level of ({defender_roll}/6).")
        if attacker_roll >= defender_roll:
            print(f"{self.name} overpowers {other_player.name} and wins the fight.")
            if other_player.has_item() and other_player.item.type == ItemType.RUSTY_BULLET:
                print(f"{other_player.name} has a {str(other_player.item)}, but is taken by surprise, "
                      f"so cannot use it.")
            other_player.get_injured()
        else:
            print(f"{other_player.name} fights back and overcomes {self.name}.")
            self.get_injured()
