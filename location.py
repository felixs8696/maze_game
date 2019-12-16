import random

from datatypes import Direction


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

    def get_coordinates(self):
        return self.x, self.y

    def teleport(self, location):
        self.x = location.x
        self.y = location.y

    def move(self, direction: Direction):
        self.teleport(self.next_location(direction))

    def in_bounds(self, board_height: int, board_width: int):
        return 0 < self.x < board_width and 0 < self.y < board_height

    def next_location(self, direction: Direction):
        if direction == Direction.UP:
            y = self.y + 1
            x = self.x
        elif direction == Direction.DOWN:
            y = self.y - 1
            x = self.x
        elif direction == Direction.RIGHT:
            x = self.x + 1
            y = self.y
        elif direction == Direction.LEFT:
            x = self.x - 1
            y = self.y
        else:
            raise ValueError(f"Invalid direction: {direction}")
        return Location(x, y)

    def neighbors(self, board_height: int, board_width: int):
        candidate_neighbors = [Location(self.x + 1, self.y),
                               Location(self.x - 1, self.y),
                               Location(self.x, self.y + 1),
                               Location(self.x, self.y - 1)]
        random.shuffle(candidate_neighbors)
        for candidate_neighbor in candidate_neighbors:
            if candidate_neighbor.in_bounds(board_height=board_height, board_width=board_width):
                yield candidate_neighbor
