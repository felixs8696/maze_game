import random

from abc import ABC, abstractmethod
from typing import List, Tuple

from src.items import RustyBullet, FirstAidKit, PileOfJunk
from src.datatypes import PortalType, Direction
from src.actions import AcquireTreasure, Action, LoseTurn, BuyItem, Heal, Teleport, Flush
from src.location import Location
from src.datatypes import TileType
from src.symbols import *
from src.exceptions import NoTreasureOnTile, InvalidDirection
from src.utils import generate_dice_roll_map


class Tile(ABC):

    def __init__(self, location: Location):
        self.location = location
        self._actions = []
        self.num_treasure = 0
        self.symbol = EMPTY

    def __str__(self):
        if self.has_treasure():
            return symbol_with_treasure(self.symbol)
        else:
            return self.symbol

    @abstractmethod
    def announce_tile(self, player):
        pass

    def has_treasure(self):
        return self.num_treasure > 0

    def add_treasure(self):
        self.num_treasure += 1

    def remove_treasure(self):
        if self.has_treasure():
            self.num_treasure -= 1
        else:
            raise NoTreasureOnTile(f"There is no treasure on this tile.")

    def get_optional_actions(self, player):
        optional_actions = []
        for action in self.get_actions(player):
            if not action.is_mandatory:
                optional_actions.append(action)
        return optional_actions

    def get_actions(self, player) -> List[Action]:
        if self.has_treasure():
            return self._actions + [AcquireTreasure()]
        return self._actions

    @abstractmethod
    def description(self):
        pass


class Safe(Tile):

    def __init__(self, location: Location):
        super().__init__(location)
        self._actions = []
        self.symbol = SAFE_SYMBOL
        self.type = TileType.SAFE

    def announce_tile(self, player):
        print(f"{player.name} walks into a {TileType.SAFE.name} clearing.")
        if self.has_treasure():
            print(f"{player.name} also stumbles across a pile of {TileType.TREASURE.name}")

    def description(self):
        return f"You are safe."


class Marsh(Tile):

    def __init__(self, location: Location):
        super().__init__(location)
        self._actions = [LoseTurn(is_mandatory=True)]
        self.symbol = MARSH_SYMBOL
        self.type = TileType.MARSH

    def announce_tile(self, player):
        print(f"{player.name} sinks into a {TileType.MARSH.name}.")
        if self.has_treasure():
            print(f"{player.name} also stumbles across a pile of {TileType.TREASURE.name}")

    def description(self):
        return f"You lose your next turn."


class Shop(Tile):

    def __init__(self, location: Location, auto_rng: bool=False):
        super().__init__(location)
        rusty_bullet = RustyBullet()
        first_aid_kit = FirstAidKit()
        pile_of_junk = PileOfJunk()
        self.items = [rusty_bullet, first_aid_kit, pile_of_junk]
        self.item_map = generate_dice_roll_map(one=rusty_bullet, two=rusty_bullet,
                                               three=first_aid_kit, four=first_aid_kit,
                                               five=pile_of_junk, six=pile_of_junk)
        self.auto_rng = auto_rng
        self._actions = [BuyItem(items=self.items, item_map=self.item_map, auto_rng=self.auto_rng)]
        self.symbol = SHOP_SYMBOL
        self.type = TileType.SHOP

    def announce_tile(self, player):
        print(f"{player.name} enters a RANDOM ITEM {TileType.SHOP.name}.")
        if self.has_treasure():
            print(f"{player.name} also stumbles across a pile of {TileType.TREASURE.name}")

    def get_actions(self, player) -> List[Action]:
        actions = []
        if not player.has_item():
            actions.extend(self._actions)

        if self.has_treasure():
            actions.extend([AcquireTreasure()])

        return actions

    def description(self):
        return f"You have entered a shop."


class Hospital(Tile):

    def __init__(self, location: Location):
        super().__init__(location)
        self.symbol = HOSPITAL_SYMBOL
        self.type = TileType.HOSPITAL
        self._actions = [Heal(source=self.type)]

    def announce_tile(self, player):
        print(f"{player.name} enters a {TileType.HOSPITAL.name}.")
        if self.has_treasure():
            print(f"{player.name} also stumbles across a pile of {TileType.TREASURE.name}")

    def get_actions(self, player) -> List[Action]:
        actions = []
        if player.is_injured():
            actions.extend(self._actions)

        if self.has_treasure():
            actions.extend([AcquireTreasure()])

        return actions

    def description(self):
        return f"You have entered the hospital."


class Portal(Tile, ABC):

    def __init__(self, location: Location, exit_location: Location, portal_type: PortalType, name: str):
        super().__init__(location)
        self.type = portal_type
        self.symbol = name
        self.exit_location = exit_location
        self._actions = [Teleport(self.exit_location, is_mandatory=True)]
        self.type = TileType.PORTAL

    def announce_tile(self, player):
        print(f"{player.name} enters and exits a portal.")
        if self.has_treasure():
            print(f"{player.name} also stumbles across a pile of {TileType.TREASURE.name}")

    def description(self):
        return f"You have landed on a portal tile."


class River(Tile, ABC):

    def __init__(self, location: Location, direction: Direction):
        super().__init__(location)
        self.direction = direction
        self._actions = [Flush(self.direction, is_mandatory=True)]
        if self.direction == Direction.UP:
            self.symbol = RIVER_U_SYMBOL
        elif self.direction == Direction.DOWN:
            self.symbol = RIVER_D_SYMBOL
        elif self.direction == Direction.LEFT:
            self.symbol = RIVER_L_SYMBOL
        elif self.direction == Direction.RIGHT:
            self.symbol = RIVER_R_SYMBOL
        else:
            raise InvalidDirection(f"Invalid direction {direction.name} for river tile.")
        self.type = TileType.RIVER

    def announce_tile(self, player):
        print(f"{player.name} swims into the {TileType.RIVER.name}.")
        if self.has_treasure():
            print(f"{player.name} also stumbles across a pile of {TileType.TREASURE.name}")

    def description(self):
        return f"You have landed on a river tile."


class TileFactory:

    @staticmethod
    def create_static_tile(tile_type: TileType, location: Location, auto_rng: bool):
        if tile_type == TileType.SAFE:
            return Safe(location=location)
        if tile_type == TileType.MARSH:
            return Marsh(location=location)
        if tile_type == TileType.HOSPITAL:
            return Hospital(location=location)
        if tile_type == TileType.SHOP:
            return Shop(location=location, auto_rng=auto_rng)
        if tile_type == TileType.TREASURE:
            treasure_tile = Safe(location=location)
            treasure_tile.add_treasure()
            return treasure_tile

    @staticmethod
    def create_full_river(board_height: int, max_num_turns: int, board_width: int, max_river_length: int):
        possible_river_paths = _get_possible_river_paths(max_river_length=max_river_length, max_num_turns=max_num_turns,
                                                         board_height=board_height, board_width=board_width)
        return random.choice(possible_river_paths)

    @staticmethod
    def create_type_a_portal_tile(location: Location):
        a_portal = Portal(location=location, exit_location=location, portal_type=PortalType.A, name=PORTAL_F_SYMBOL)
        return a_portal

    @staticmethod
    def create_type_ab_portal_tiles(locations: Tuple[Location, Location]):
        a_portal = Portal(location=locations[0], exit_location=locations[1], portal_type=PortalType.AB,
                          name=PORTAL_A_SYMBOL)
        b_portal = Portal(location=locations[1], exit_location=locations[0], portal_type=PortalType.AB,
                          name=PORTAL_B_SYMBOL)
        return a_portal, b_portal

    @staticmethod
    def create_type_abc_portal_tiles(locations: Tuple[Location, Location]):
        a_portal = Portal(location=locations[0], exit_location=locations[1], portal_type=PortalType.ABC,
                          name=PORTAL_1_SYMBOL)
        b_portal = Portal(location=locations[1], exit_location=locations[2], portal_type=PortalType.ABC,
                          name=PORTAL_2_SYMBOL)
        c_portal = Portal(location=locations[2], exit_location=locations[0], portal_type=PortalType.ABC,
                          name=PORTAL_3_SYMBOL)
        return a_portal, b_portal, c_portal


def _get_river_start_tile(board_height: int, board_width: int):
    use_x_axis_edge = random.random() < 0.5
    max_x_coordinate, max_y_coordinate = board_width - 1, board_height - 1

    if use_x_axis_edge:
        x = random.choice(range(board_width))
        y = random.choice([0, max_y_coordinate])
        if y == max_y_coordinate:
            init_direction = Direction.DOWN
        else:
            init_direction = Direction.UP
    else:
        x = random.choice([0, max_x_coordinate])
        y = random.choice(range(board_height))
        if x == max_x_coordinate:
            init_direction = Direction.LEFT
        else:
            init_direction = Direction.RIGHT

    return River(location=Location(x=x, y=y), direction=init_direction)


def _get_possible_river_paths(max_river_length: int, max_num_turns: int, board_height: int, board_width: int):
    valid_river_paths = []
    queue = []
    possible_directions = [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]

    river_start_tile = _get_river_start_tile(board_height=board_height, board_width=board_width)
    # print(f"river_start_tile: {river_start_tile}")
    queue.append(([river_start_tile], max_num_turns))

    while len(queue) != 0:
        river_path, remaining_num_turns = queue.pop(0)
        # print(f"Investigating river_path ({len(river_path)}) ({river_path[0].location}): {[str(river_tile)
        # for river_tile in river_path]}")
        if len(river_path) == max_river_length:
            if _river_tile_exits_wall(river_path[-1], board_height=board_height, board_width=board_width):
                return [river_path]
        else:
            last_river_tile = river_path[-1]
            next_river_tile_location = last_river_tile.location.next_location(last_river_tile.direction)

            if next_river_tile_location.in_bounds(board_height=board_height, board_width=board_width):
                for direction in random.sample(possible_directions, len(possible_directions)):
                    if _can_add_river_tile_in_this_direction(location=next_river_tile_location,
                                                             direction=direction,
                                                             river_tiles=river_path,
                                                             board_height=board_width,
                                                             board_width=board_width):
                        neighbor_river_tile = River(location=next_river_tile_location, direction=direction)
                        new_river_path = river_path + [neighbor_river_tile]
                        if max_num_turns >= 0:
                            if direction == last_river_tile.direction:
                                queue.append((new_river_path, remaining_num_turns))
                            else:
                                if not remaining_num_turns <= 0:
                                    queue.append((new_river_path, remaining_num_turns - 1))
                        else:
                            queue.append((new_river_path, remaining_num_turns))

    print(f"Did not find valid river.")
    return valid_river_paths


def _can_add_river_tile_in_this_direction(location: Location, direction: Direction, river_tiles: List[River],
                                          board_height: int, board_width: int):
    river_tile_locations = [river_tile.location for river_tile in river_tiles]
    candidate_next_river_tile_location = location.next_location(direction=direction)
    # if candidate_next_river_tile_location.in_bounds(board_height=board_height, board_width=board_width):
    if candidate_next_river_tile_location not in river_tile_locations:
        return True
    return False


def _river_tile_exits_wall(river_tile: River, board_height: int, board_width: int):
    return not river_tile.location.next_location(direction=river_tile.direction).in_bounds(board_height=board_height,
                                                                                           board_width=board_width)
