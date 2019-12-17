from typing import List

from location import Location
from datatypes import Direction

class Wall:
    def __init__(self, adjacent_locations: List[Location]):
        self.adjacent_locations = adjacent_locations

class Exit:
    def __init__(self, location: Location, direction: Direction):
        self.location = location
        self.direction = direction

    def __str__(self):
        return f"({str(self.location)}, {self.direction.name})"
