import random

from datatypes import Direction
from exceptions import MoveBlockedByWall


class Location:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self):
        return f'({self.x}, {self.y})'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def copy(self):
        return Location(x=self.x, y=self.y)

    def get_coordinates(self):
        return self.x, self.y

    def teleport(self, location):
        self.x = location.x
        self.y = location.y

    def no_walls_block_straight_line_location(self, location, walls):
        assert self != location, f"Cannot ask for blockers between the same locations."
        assert self.x == location.x or self.y == location.y, \
            f"There is no straight path between this location {self} and {location}"
        wall_adj_locations = [wall.adjacent_locations for wall in walls]
        if self.x == location.x:
            higher_loc_y = max(self.y, location.y)
            lower_loc_y = min(self.y, location.y)
            for i in range(1, higher_loc_y - lower_loc_y + 1):
                loc_1 = Location(self.x, lower_loc_y)
                loc_2 = Location(location.x, lower_loc_y + i)
                adj_locations = (loc_1, loc_2)
                rev_adj_locations = (loc_2, loc_1)
                if adj_locations in wall_adj_locations or rev_adj_locations in wall_adj_locations:
                    return False
        if self.y == location.y:
            higher_loc_x = max(self.x, location.x)
            lower_loc_x = min(self.x, location.x)
            for i in range(1, higher_loc_x - lower_loc_x + 1):
                loc_1 = Location(lower_loc_x, self.y)
                loc_2 = Location(lower_loc_x + i, location.y)
                adj_locations = (loc_1, loc_2)
                rev_adj_locations = (loc_2, loc_1)
                if adj_locations in wall_adj_locations or rev_adj_locations in wall_adj_locations:
                    return False
        return True

    def move(self, direction: Direction, walls):
        next_location = self.next_location(direction=direction)
        if self.no_walls_block_straight_line_location(next_location, walls):
            self.teleport(self.next_location(direction))
        else:
            raise MoveBlockedByWall(f'Cannot move {direction.name}. Blocked by wall.')

    def in_bounds(self, board_height: int, board_width: int):
        return 0 <= self.x < board_width and 0 <= self.y < board_height

    def next_location(self, direction: Direction):
        if direction == Direction.UP:
            x_delta = 0
            y_delta = 1
        elif direction == Direction.DOWN:
            x_delta = 0
            y_delta = -1
        elif direction == Direction.RIGHT:
            x_delta = 1
            y_delta = 0
        elif direction == Direction.LEFT:
            x_delta = -1
            y_delta = 0
        else:
            raise ValueError(f"Invalid direction: {direction}")
        return Location(self.x + x_delta, self.y + y_delta)

    def neighbors(self, board_height: int, board_width: int):
        candidate_neighbors = [Location(self.x + 1, self.y),
                               Location(self.x - 1, self.y),
                               Location(self.x, self.y + 1),
                               Location(self.x, self.y - 1)]
        random.shuffle(candidate_neighbors)

        valid_neighbors = []
        for candidate_neighbor in candidate_neighbors:
            if candidate_neighbor.in_bounds(board_height=board_height, board_width=board_width):
                valid_neighbors.append(candidate_neighbor)
        return valid_neighbors
