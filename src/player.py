import numpy as np
import uuid
import time

from src.datatypes import StatusType, ItemType, Direction, MoveType, TileType, XPExchangeType
from src.move import Move
from src.movement import Movement
from src.location import Location
from src.utils import ask_for_options, display_options, get_yes_or_no_response, response_is_yes, \
    prompt_real_dice_roll_result, manhattan_distance
from src.exceptions import MoveBlockedByWall, ExitFound, GameOver
from src.actions import Fight, EndTurn, AcquireTreasure, DropTreasure, RevealClosestHospital, RevealClosestShop, \
    RevealObstacle, HealInstantlyWithXP

from src.exceptions import ItemAlreadyHeldError, NoItemHeldError, TreasureAlreadyHeldError, NoTreasureHeldError


class Player:
    def __init__(self, name: str = '', location: Location = None, board=None, item=None, has_treasure=False,
                 can_move=True, active=False, lose_next_turn=False, player_id=None, status=StatusType.HEALTHY,
                 acquired_item_this_turn=False, xp: int = 0, tile_most_recently_encountered=None,
                 can_request_hospital_location=True, can_request_shop_location=True, auto_rng: bool = False):
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
        self.acquired_item_this_turn = acquired_item_this_turn
        self.xp = xp
        self.tile_most_recently_encountered = tile_most_recently_encountered
        self.xp_exchange_options = [RevealClosestHospital(), RevealClosestShop(), RevealObstacle(), HealInstantlyWithXP()]
        self.can_request_hospital_location = can_request_hospital_location
        self.can_request_shop_location = can_request_shop_location

    def __eq__(self, other):
        return self.player_id == other.player_id

    @staticmethod
    def copy_from(player, auto_rng: bool = False):
        return Player(name=player.name, location=player.location, board=player.board,
                      item=player.item, has_treasure=player.has_treasure, can_move=player.can_move,
                      active=player.active, lose_next_turn=player.lose_next_turn, player_id=player.player_id,
                      status=player.status, acquired_item_this_turn=player.acquired_item_this_turn, xp=player.xp,
                      tile_most_recently_encountered=player.tile_most_recently_encountered,
                      can_request_hospital_location=player.can_request_hospital_location,
                      can_request_shop_location=player.can_request_shop_location, auto_rng=auto_rng)

    def begin_turn(self):
        if self.lose_next_turn:
            print(f"Sorry {self.name}, you have lost your turn.")
            self.can_move = False
            self.lose_next_turn = False
            self.end_turn()
        else:
            self.active = True

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
            self.acquired_item_this_turn = False
            self.active = False
            self.can_move = True

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

    def _get_possible_xp_exchange_options(self):
        possible_xp_exchange_options = []
        for xp_exchange_option in self.xp_exchange_options:
            if self.xp >= xp_exchange_option.xp_cost:
                if xp_exchange_option.exchange_type == XPExchangeType.REVEAL_HOSPITAL and \
                        not self.can_request_hospital_location:
                    continue
                if xp_exchange_option.exchange_type == XPExchangeType.REVEAL_SHOP and \
                        not self.can_request_shop_location:
                    continue
                if xp_exchange_option.exchange_type == XPExchangeType.HEAL_INSTANTLY and \
                        not self.is_injured():
                    continue
                possible_xp_exchange_options.append(xp_exchange_option)
        return possible_xp_exchange_options

    def get_possible_actions(self, other_players, board, available_tile_actions):
        possible_actions = [EndTurn()]
        if self.item is not None:
            possible_actions.extend(self.item.get_actions(self, other_players, board))
        possible_actions.extend(self._get_possible_fights(other_players=other_players))
        possible_actions.extend(available_tile_actions)
        possible_actions.extend(self._get_possible_xp_exchange_options())

        if self.has_treasure:
            possible_actions.extend([DropTreasure()])

        valid_possible_actions = []
        for i in range(len(possible_actions)):
            if not ((self.has_treasure or self.is_injured()) and isinstance(possible_actions[i], AcquireTreasure)):
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

        def get_invalid_move_msg(name, move_choice, possible_choices):
            return f"Sorry {name}, '{move_choice}' is not a valid selection. " \
                f"Please select one of the following numbers: {possible_choices}"

        valid_move = False
        range_of_possible_moves = range(len(possible_moves))
        move_index = None

        if not auto_play:
            while not valid_move:
                move_index = ask_for_options(possible_moves)
                try:
                    if int(move_index) in range_of_possible_moves:
                        valid_move = True
                    else:
                        print(get_invalid_move_msg(self.name, move_index, tuple(range_of_possible_moves)))
                except ValueError:
                    print(get_invalid_move_msg(self.name, move_index, tuple(range_of_possible_moves)))
        else:
            display_options(possible_moves)

            invalid_move = True
            while invalid_move:
                move_index = np.random.choice(range(len(possible_moves)))
                chosen_move = possible_moves[move_index]
                invalid_move = False
                if isinstance(chosen_move, AcquireTreasure):
                    break

                acquire_treasure_option_exists = False
                for move in possible_moves:
                    if isinstance(move, AcquireTreasure):
                        acquire_treasure_option_exists = True
                if acquire_treasure_option_exists:
                    if not isinstance(chosen_move, AcquireTreasure):
                        invalid_move = True
                        continue
                if isinstance(chosen_move, DropTreasure):
                    invalid_move = True
                    continue
                if isinstance(chosen_move, EndTurn) and self.can_move:
                    invalid_move = True
                    continue

            time.sleep(auto_turn_time_secs)
            print(f"Move chosen: {move_index}")

        return possible_moves[int(move_index)]

    def has_item(self):
        return self.item is not None

    def acquire_treasure(self):
        x, y = self.location.get_coordinates()
        tile = self.board.grid[x][y]
        print(f"tile.num_treasure: {tile.num_treasure}")
        assert tile.has_treasure()
        assert not self.is_injured()
        assert not self.has_treasure
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
            self.acquired_item_this_turn = True
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
                use_bullet = np.random.choice([True, False])
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

    def add_xp(self, amount):
        self.xp += amount
        print(f"{self.name} has gained {amount} XP for a total of {self.xp}.")

    def spend_xp(self, amount):
        assert amount <= self.xp
        self.xp -= amount
        print(f"{self.name} has spent {amount} XP and now has {self.xp} XP.")

    def _reveal_closest_building(self, tile_type: TileType):
        assert tile_type == TileType.HOSPITAL or tile_type == TileType.SHOP

        tile_type_locations = []
        for location in self.board.all_locations:
            tile = self.board.get_tile(location=location)
            if tile.type == tile_type:
                tile_type_locations.append(location)

        shortest_manhattan_distance = self.board.height + self.board.width
        shortest_tile_type_location = None
        for tile_type_location in tile_type_locations:
            manhattan_distance_to_tile_type = manhattan_distance(self.location, tile_type_location)
            if manhattan_distance_to_tile_type <= shortest_manhattan_distance:
                shortest_manhattan_distance = manhattan_distance_to_tile_type
                shortest_tile_type_location = tile_type_location

        x1, y1 = self.location.get_coordinates()
        x2, y2 = shortest_tile_type_location.get_coordinates()

        x_distance = x2 - x1
        y_distance = y2 - y1

        print(f"{tile_type.name} location: {shortest_tile_type_location.get_coordinates()}")

        full_distance_phrase = '0 spaces'
        if x_distance != 0 or y_distance != 0:
            horizontal_distance_phrase = ''
            if x_distance < 0:
                horizontal_distance_phrase = f'LEFT {-x_distance}'
            elif x_distance > 0:
                horizontal_distance_phrase = f'RIGHT {x_distance}'

            conjunction = ''
            if x_distance != 0 and y_distance != 0:
                conjunction = ' and '

            vertical_distance_phrase = ''
            if y_distance < 0:
                vertical_distance_phrase = f'DOWN {-y_distance}'
            elif y_distance > 0:
                vertical_distance_phrase = f'UP {y_distance}'

            full_distance_phrase = f'{horizontal_distance_phrase}{conjunction}{vertical_distance_phrase}'

        print(f"The closest {tile_type.name} to {self.name} is "
              f"{full_distance_phrase} spaces "
              f"from {self.name}'s current location.\n")

    def reveal_closest_hospital(self):
        self._reveal_closest_building(tile_type=TileType.HOSPITAL)
        self.can_request_hospital_location = False

    def reveal_closest_shop(self):
        self._reveal_closest_building(tile_type=TileType.SHOP)
        self.can_request_shop_location = False

    def reveal_obstacle(self):
        most_recent_tile = self.tile_most_recently_encountered
        print(f"The tile {self.name} most recently encountered was a {most_recent_tile.type.name} tile.")
        if most_recent_tile.type == TileType.PORTAL:
            print(f"That portal was a {most_recent_tile.portal_type.name} portal.")
        elif most_recent_tile.type == TileType.RIVER:
            print(f"That river tile was pointing {most_recent_tile.direction.name}.")

    def assign_most_recently_encountered_tile(self, tile):
        self.tile_most_recently_encountered = tile
