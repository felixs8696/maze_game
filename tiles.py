import random

from abc import ABC, abstractmethod
from typing import List, Tuple

from items import RustyBullet, FirstAidKit, PileOfJunk
from datatypes import PortalType, Direction, BorderWallType
from actions import AcquireTreasure, Action, DoNothing, LoseTurn, BuyItem, Heal, Teleport, Flush
from location import Location
from datatypes import TileType


class Tile(ABC):

    def __init__(self, location: Location):
        self.location = location
        self._actions = []

    @abstractmethod
    def __str__(self):
        pass

    def get_actions(self) -> List[Action]:
        return self._actions

    @abstractmethod
    def description(self):
        pass


class Safe(Tile):

    def __init__(self, location: Location):
        super().__init__(location)
        self._actions = [DoNothing(is_mandatory=True)]

    def __str__(self):
        return '_'

    def description(self):
        return f"You are safe."


class Marsh(Tile):

    def __init__(self, location: Location):
        super().__init__(location)
        self._actions = [LoseTurn(is_mandatory=True)]

    def __str__(self):
        return 'M'

    def description(self):
        return f"You lose your next turn."


class Shop(Tile):

    def __init__(self, location: Location):
        super().__init__(location)
        self.items = [RustyBullet(), FirstAidKit(), PileOfJunk()]
        self._actions = [DoNothing(), BuyItem(items=self.items)]

    def __str__(self):
        return 'S'

    def description(self):
        return f"You have entered a shop."


class Hospital(Tile):

    def __init__(self, location: Location):
        super().__init__(location)
        self._actions = [DoNothing(), Heal()]

    def __str__(self):
        return 'H'

    def description(self):
        return f"You have entered the hospital."


class Portal(Tile, ABC):

    def __init__(self, location: Location, exit_location: Location, portal_type: PortalType, name: str):
        super().__init__(location)
        self.type = portal_type
        self.name = name
        self.exit_location = exit_location
        self._actions = [Teleport(self.exit_location, is_mandatory=True)]

    def __str__(self):
        return self.name

    def description(self):
        return f"You have landed on a portal tile."


class River(Tile, ABC):

    def __init__(self, location: Location, direction: Direction):
        super().__init__(location)
        self.direction = direction
        self._actions = [Flush(self.direction, is_mandatory=True)]

    def __str__(self):
        if self.direction == Direction.UP:
            return u'\u2191'
        if self.direction == Direction.DOWN:
            return u'\u2193'
        if self.direction == Direction.LEFT:
            return u'\u2190'
        if self.direction == Direction.RIGHT:
            return u'\u2192'

    def description(self):
        return f"You have landed on a river tile."


class Treasure(Tile, ABC):

    def __init__(self, location: Location):
        super().__init__(location)
        self._actions = [DoNothing(), AcquireTreasure()]

    def __str__(self):
        return 'T'

    def description(self):
        return f"You have entered a treasure room."


class TileFactory:

    @staticmethod
    def create_static_tile(tile_type: TileType, location: Location):
        if tile_type == TileType.MARSH:
            return Marsh(location=location)
        if tile_type == TileType.RIVER:
            return River(location=location, direction=direction)
        if tile_type == TileType.HOSPITAL:
            return Hospital(location=location)
        if tile_type == TileType.SHOP:
            return Shop(location=location)
        if tile_type == TileType.TREASURE:
            return Treasure(location=location)

    @staticmethod
    def create_full_river(board_height: int, max_num_turns: int, board_width: int, max_river_length: int):
        possible_river_paths = _get_possible_river_paths(max_river_length=max_river_length, max_num_turns=max_num_turns,
                                                         board_height=board_height, board_width=board_width)
        return random.choice(possible_river_paths)

    @staticmethod
    def create_type_a_portal_tile(location: Location):
        a_portal = Portal(location=location, exit_location=location, portal_type=PortalType.A, name='F')
        return a_portal

    @staticmethod
    def create_type_ab_portal_tiles(locations: Tuple[Location, Location]):
        a_portal = Portal(location=locations[0], exit_location=locations[1], portal_type=PortalType.AB, name='A')
        b_portal = Portal(location=locations[1], exit_location=locations[0], portal_type=PortalType.AB, name='B')
        return a_portal, b_portal

    @staticmethod
    def create_type_abc_portal_tiles(locations: Tuple[Location, Location]):
        a_portal = Portal(location=locations[0], exit_location=locations[1], portal_type=PortalType.ABC, name='1')
        b_portal = Portal(location=locations[1], exit_location=locations[2], portal_type=PortalType.ABC, name='2')
        c_portal = Portal(location=locations[2], exit_location=locations[0], portal_type=PortalType.ABC, name='3')
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
        if y == max_x_coordinate:
            init_direction = Direction.LEFT
        else:
            init_direction = Direction.RIGHT

    return River(location=Location(x=x, y=y), direction=init_direction)


def _get_possible_river_paths(max_river_length: int, max_num_turns: int, board_height: int, board_width: int):
    valid_river_paths = []
    queue = []
    possible_directions = [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]

    river_start_tile = _get_river_start_tile(board_height=board_height, board_width=board_width)
    queue.append(([river_start_tile], max_num_turns))

    while len(queue) != 0:
        river_path, remaining_num_turns = queue.pop(0)
        print(f"Remaining num turns: {remaining_num_turns}")
        print(f"Investigating river_path ({len(river_path)}) ({river_path[0].location}): {[str(river_tile) for river_tile in river_path]}")
        if len(river_path) == max_river_length:
            if _river_tile_exits_wall(river_path[-1], board_height=board_height, board_width=board_width):
                print(f"Found river.")
                return [river_path]
                # valid_river_paths.append(river_path)
        else:
            last_river_tile = river_path[-1]
            next_river_tile_location = last_river_tile.location.next_location(last_river_tile.direction)

            for neighbor_tile_location in next_river_tile_location.neighbors(board_height=board_height,
                                                                             board_width=board_width):
                river_tile_locations = [river_tile.location for river_tile in river_path]
                if neighbor_tile_location not in river_tile_locations:
                    change_direction = True
                    if remaining_num_turns <= 0 or random.random() < 0.5:
                        change_direction = False

                    if not change_direction:
                        if _can_add_river_tile_in_this_direction(location=neighbor_tile_location,
                                                                 direction=last_river_tile.direction,
                                                                 river_tiles=river_path, board_height=board_width,
                                                                 board_width=board_width):
                            neighbor_river_tile = River(location=neighbor_tile_location,
                                                        direction=last_river_tile.direction)
                            new_river_path = river_path.copy()
                            new_river_path.append(neighbor_river_tile)
                            queue.append((new_river_path, remaining_num_turns))
                    else:
                        for direction in possible_directions:
                            if direction != last_river_tile.direction:
                                if _can_add_river_tile_in_this_direction(location=neighbor_tile_location,
                                                                         direction=direction,
                                                                         river_tiles=river_path,
                                                                         board_height=board_width,
                                                                         board_width=board_width):
                                    neighbor_river_tile = River(location=neighbor_tile_location, direction=direction)
                                    new_river_path = river_path.copy()
                                    new_river_path.append(neighbor_river_tile)
                                    queue.append((new_river_path, remaining_num_turns - 1))

    print(f"Did not find river.")
    return valid_river_paths


def _can_add_river_tile_in_this_direction(location: Location, direction: Direction, river_tiles: List[River],
                                          board_height: int, board_width: int):
    river_tile_locations = [river_tile.location for river_tile in river_tiles]
    candidate_next_river_tile_location = location.next_location(direction=direction)
    if candidate_next_river_tile_location.in_bounds(board_height=board_height, board_width=board_width):
        if candidate_next_river_tile_location not in river_tile_locations:
            return True
    return False


def _river_tile_exits_wall(river_tile: River, board_height: int, board_width: int):
    return not river_tile.location.next_location(direction=river_tile.direction).in_bounds(board_height=board_height,
                                                                                           board_width=board_width)
