import numpy as np


class Board:
    def __init__(self, height=8, width=8, num_marshes=8, num_river_tiles=12, num_hospitals=1, num_shops=1,
                 num_aa_portal_sets=1, num_ab_portal_sets=1, num_abc_portal_sets=1):
        self.height = 8
        self.width = 8
        self.num_marshes = num_marshes
        self.num_river_tiles = num_river_tiles
        self.num_hospitals = num_hospitals
        self.num_shops = num_shops
        self.num_aa_portal_sets = num_aa_portal_sets
        self.num_ab_portal_sets = num_ab_portal_sets
        self.num_abc_portal_sets = num_abc_portal_sets
        self.grid = np.zeros(shape=(height, width))
        self.walls = []

    def generate_contents(self):
        shuffled_coordinates = [(x, y) for x in range(self.height) for y in range(self.width)]
        np.random.shuffle(shuffled_coordinates)
        marsh_coordinates = [shuffled_coordinates.pop() for _ in range(self.num_marshes)]
        river_tile_coordinates = [shuffled_coordinates.pop() for _ in range(self.num_river_tiles)]
        hospital_coordinates = [shuffled_coordinates.pop() for _ in range(self.num_hospitals)]
        shop_coordinates = [shuffled_coordinates.pop() for _ in range(self.num_shops)]
        aa_portal_coordinates = [shuffled_coordinates.pop() for _ in range(self.num_aa_portal_sets)]
        ab_portal_coordinates = [shuffled_coordinates.pop() for _ in range(self.num_ab_portal_sets * 2)]
        abs_portal_coordinates = [shuffled_coordinates.pop() for _ in range(self.num_abc_portal_sets * 3)]

        grid = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append()
            grid.append(row)

    def get_tile(self, location):
        return self.grid[location.x][location.y]
