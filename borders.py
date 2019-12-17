from typing import Tuple

from location import Location
from datatypes import Direction

class Wall:
    def __init__(self, adjacent_locations: Tuple[Location]):
        self.adjacent_locations = adjacent_locations

    def __eq__(self, other):
        return self.adjacent_locations == other.adjacent_locations

    def __hash__(self):
        return hash(self.adjacent_locations)

    def __str__(self):
        return f'({str(self.adjacent_locations[0])}, {str(self.adjacent_locations[1])})'

class Exit:
    def __init__(self, location: Location, direction: Direction):
        self.location = location
        self.direction = direction

    def __str__(self):
        return f"({str(self.location)}, {self.direction.name})"
