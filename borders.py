from typing import Tuple

from location import Location
from datatypes import Direction

class Wall:
    def __init__(self, adjacent_locations: Tuple[Location, Location]):
        self.adjacent_locations = adjacent_locations

    def __eq__(self, other):
        exactly_equal = self.adjacent_locations == other.adjacent_locations
        reverse_equal = self.adjacent_locations == other.adjacent_locations[::-1]
        return exactly_equal or reverse_equal

    def __hash__(self):
        loc_1, loc_2 = self.adjacent_locations
        loc_r1, loc_r2 = self.adjacent_locations[::-1]
        return hash((loc_1.x^loc_r1.x, loc_2.y^loc_r2.y))

    def __str__(self):
        return f'({str(self.adjacent_locations[0])}, {str(self.adjacent_locations[1])})'

class Exit:
    def __init__(self, location: Location, direction: Direction):
        self.location = location
        self.direction = direction

    def __str__(self):
        return f"({str(self.location)}, {self.direction.name})"
