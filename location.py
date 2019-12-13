from .datatypes import Direction


class Location:

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def teleport(self, location):
        self.x = location.x
        self.y = location.y

    def move(self, direction: Direction):
        if direction == Direction.UP:
            self.y += 1
        elif direction == Direction.DOWN:
            self.y -= 1
        elif direction == Direction.RIGHT:
            self.x += 1
        elif direction == Direction.LEFT:
            self.x -= 1
