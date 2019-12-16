import numpy as np
import random

from datatypes import TileType, TileCategories
from tiles import TileFactory, Tile
from location import Location
from utils import create_placeholder_matrix


class Board:
    def __init__(self, height=8, width=8, river_max_num_turns=2, num_marshes=8, num_river_tiles=12, num_hospitals=1, num_shops=1,
                 num_aa_portal_sets=1, num_ab_portal_sets=1, num_abc_portal_sets=1, num_treasures=2):
        self.height = 8
        self.width = 8

        self.num_tiles = {
            TileCategories.STATIC: {
                TileType.MARSH: num_marshes,
                TileType.HOSPITAL: num_hospitals,
                TileType.SHOP: num_shops,
                TileType.TREASURE: num_treasures
            },
            TileCategories.DYNAMIC: {
                TileType.RIVER: num_river_tiles,
                TileType.A_PORTAL: num_aa_portal_sets,
                TileType.AB_PORTAL: num_ab_portal_sets,
                TileType.ABC_PORTAL: num_abc_portal_sets
            }
        }

        self.river_max_num_turns = river_max_num_turns
        self.walls = []
        self.safe_locations = self.generate_contents()

    def _assign_tile_to_grid(self, tile: Tile, remaining_locations: set):
        x, y = tile.location
        self.grid[x][y] = tile
        remaining_locations.remove(tile.location)
        return remaining_locations

    def generate_contents(self):
        print('Generating board...')
        safe_locations = set(Location(x=x, y=y) for x in range(self.height) for y in range(self.width))
        self.grid = create_placeholder_matrix(width=self.width, height=self.height, placeholder=TileType.SAFE)

        print('Generating river tiles...')
        river_tiles = TileFactory.create_full_river(
            max_river_length=self.num_tiles[TileCategories.DYNAMIC][TileType.RIVER],
            max_num_turns=self.river_max_num_turns,
            board_height=self.height,
            board_width=self.width)

        for river_tile in river_tiles:
            safe_locations = self._assign_tile_to_grid(tile=river_tile, remaining_locations=safe_locations)

        print('Generating portal tiles...')
        for _ in range(self.num_tiles[TileCategories.DYNAMIC][TileType.A_PORTAL]):
            aa_portal = TileFactory.create_type_a_portal_tile(location=random.choice(safe_locations))
            safe_locations = self._assign_tile_to_grid(tile=aa_portal, remaining_locations=safe_locations)

        for _ in range(self.num_tiles[TileCategories.DYNAMIC][TileType.AB_PORTAL]):
            locations = random.choices(safe_locations, 2)
            ab_portal, ba_portal = TileFactory.create_type_ab_portal_tiles(locations=locations)
            safe_locations = self._assign_tile_to_grid(tile=ab_portal, remaining_locations=safe_locations)
            safe_locations = self._assign_tile_to_grid(tile=ba_portal, remaining_locations=safe_locations)

        for _ in range(self.num_tiles[TileCategories.DYNAMIC][TileType.ABC_PORTAL]):
            locations = random.choices(safe_locations, 3)
            ab_portal, bc_portal, ca_portal = TileFactory.create_type_abc_portal_tiles(locations=locations)
            safe_locations = self._assign_tile_to_grid(tile=ab_portal, remaining_locations=safe_locations)
            safe_locations = self._assign_tile_to_grid(tile=bc_portal, remaining_locations=safe_locations)
            safe_locations = self._assign_tile_to_grid(tile=ca_portal, remaining_locations=safe_locations)

        print('Generating static tiles...')
        shuffled_safe_locations = list(safe_locations)
        random.shuffle(shuffled_safe_locations)
        for tile_type, num_tiles in self.num_tiles[TileCategories.STATIC].items():
            for _ in range(num_tiles):
                location = shuffled_safe_locations.pop()
                static_tile = TileFactory.create_static_tile(tile_type, location)
                shuffled_safe_locations = self._assign_tile_to_grid(tile=static_tile,
                                                                    remaining_locations=shuffled_safe_locations)

        print('Done.')
        return shuffled_safe_locations

    def get_tile(self, location):
        return self.grid[location.x][location.y]
