import random

from datatypes import TileType, TileCategories, Direction
from tiles import TileFactory, Tile, Safe
from location import Location
from borders import Wall, Exit


class Board:
    def __init__(self, height=8, width=8, river_max_num_turns=2, num_marshes=8, num_river_tiles=12, num_hospitals=1,
                 num_shops=1, num_aa_portal_sets=1, num_ab_portal_sets=1, num_abc_portal_sets=1, num_treasures=2,
                 num_inner_walls=32, num_exits=2):
        self.height = height
        self.width = width

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
        self.num_exits = num_exits
        self.num_inner_walls = num_inner_walls
        self.inner_walls = None
        self.exits = None
        self.grid = None
        self.border_locations = self._get_border_locations()
        self.all_locations = [Location(x=x, y=y) for x in range(self.width) for y in range(self.height)]
        self.safe_locations = self.generate_contents()

    def get_untraversable_locations_from_origin(self, inner_walls):
        queue = [self.all_locations[0]]
        visited = {}
        for location in self.all_locations:
            visited[location] = False
        while len(queue) != 0:
            location = queue.pop()
            visited[location] = True
            for neighbor in location.neighbors(board_height=self.height, board_width=self.width):
                if not visited[neighbor] and location.no_walls_block_straight_line_location(location=neighbor,
                                                                                            walls=inner_walls):
                    queue.append(neighbor)

        untraversed_locations = []
        for k, v in visited.items():
            if not visited[k]:
                untraversed_locations.append(k)
        return untraversed_locations

    # def fix_walls_to_prevent_untraversable_locations(self):
    #     untraversed_locations = self.all_locations
    #     while len(untraversed_locations) != 0:
    #         untraversed_locations = self._get_untraversable_locations_from_origin()
    #
    #     return untraversed_locations


    def _get_border_locations(self):
        top_border = [Location(x=x, y=self.height - 1) for x in range(self.width)]
        bottom_border = [Location(x=x, y=0) for x in range(self.width)]
        left_border = [Location(x=0, y=y) for y in range(1, self.height)]
        right_border = [Location(x=self.width - 1, y=y) for y in range(1, self.height)]
        return top_border + bottom_border + left_border + right_border

    def _assign_tile_to_grid(self, tile: Tile, remaining_locations: set):
        x, y = tile.location.get_coordinates()
        self.grid[x][y] = tile
        remaining_locations.remove(tile.location)
        return remaining_locations

    def generate_contents(self):
        print('Generating board...')
        self.grid = _create_safe_tile_matrix(width=self.width, height=self.height)
        safe_locations = set(self.grid[x][y].location for x in range(self.width) for y in range(self.height))

        print(f'Generating {self.num_tiles[TileCategories.DYNAMIC][TileType.RIVER]} river tiles...')
        river_tiles = TileFactory.create_full_river(
            max_river_length=self.num_tiles[TileCategories.DYNAMIC][TileType.RIVER],
            max_num_turns=self.river_max_num_turns,
            board_height=self.height,
            board_width=self.width)

        for river_tile in river_tiles:
            safe_locations = self._assign_tile_to_grid(tile=river_tile, remaining_locations=safe_locations)

        for _ in range(self.num_tiles[TileCategories.DYNAMIC][TileType.A_PORTAL]):
            print(f'Generating {self.num_tiles[TileCategories.DYNAMIC][TileType.A_PORTAL]} AA portal sets...')
            aa_portal = TileFactory.create_type_a_portal_tile(location=random.choice(list(safe_locations)))
            safe_locations = self._assign_tile_to_grid(tile=aa_portal, remaining_locations=safe_locations)

        for _ in range(self.num_tiles[TileCategories.DYNAMIC][TileType.AB_PORTAL]):
            print(f'Generating {self.num_tiles[TileCategories.DYNAMIC][TileType.AB_PORTAL]} AB portal sets...')
            locations = random.sample(list(safe_locations), k=2)
            ab_portal, ba_portal = TileFactory.create_type_ab_portal_tiles(locations=locations)
            safe_locations = self._assign_tile_to_grid(tile=ab_portal, remaining_locations=safe_locations)
            safe_locations = self._assign_tile_to_grid(tile=ba_portal, remaining_locations=safe_locations)

        for _ in range(self.num_tiles[TileCategories.DYNAMIC][TileType.ABC_PORTAL]):
            print(f'Generating {self.num_tiles[TileCategories.DYNAMIC][TileType.ABC_PORTAL]} ABC portal sets...')
            locations = random.sample(list(safe_locations), k=3)
            ab_portal, bc_portal, ca_portal = TileFactory.create_type_abc_portal_tiles(locations=locations)
            safe_locations = self._assign_tile_to_grid(tile=ab_portal, remaining_locations=safe_locations)
            safe_locations = self._assign_tile_to_grid(tile=bc_portal, remaining_locations=safe_locations)
            safe_locations = self._assign_tile_to_grid(tile=ca_portal, remaining_locations=safe_locations)

        for tile_type, num_tiles in self.num_tiles[TileCategories.STATIC].items():
            print(f'Generating {num_tiles} {tile_type.name.lower()}{"s" if num_tiles > 1 else ""}...')
            for _ in range(num_tiles):
                location = random.choice(list(safe_locations))
                static_tile = TileFactory.create_static_tile(tile_type=tile_type, location=location)
                safe_locations = self._assign_tile_to_grid(tile=static_tile, remaining_locations=safe_locations)

        print(f'Generating {self.num_inner_walls} inner walls...')
        inner_walls = set()
        river_locations = [river_tile.location for river_tile in river_tiles]
        while len(inner_walls) < self.num_inner_walls:
            valid_wall = False
            while not valid_wall:
                first_loc = random.choice(self.all_locations)
                second_loc = random.choice(first_loc.neighbors(board_height=self.height, board_width=self.width))
                while first_loc in river_locations and second_loc in river_locations:
                    first_loc = random.choice(self.all_locations)
                    second_loc = random.choice(first_loc.neighbors(board_height=self.height, board_width=self.width))
                location_pair = (first_loc, second_loc)
                wall = Wall(adjacent_locations=tuple(location_pair))
                if wall not in inner_walls:
                    inner_walls.add(wall)
                    valid_wall = True
                    untraversable_walls = self.get_untraversable_locations_from_origin(list(inner_walls))
                    if len(untraversable_walls) != 0:
                        inner_walls.remove(wall)
                        valid_wall = False
        self.inner_walls = list(inner_walls)

        print(f'Generating {self.num_exits} exits...')
        self.exits = []
        exit_locations = random.sample(self.border_locations, k=self.num_exits)
        while not _exit_location_compatible_with_river(exit_locations=exit_locations, river_tiles=river_tiles,
                                                       board_height=self.height, board_width=self.width):
            exit_locations = random.sample(self.border_locations, k=self.num_exits)
        for location in exit_locations:
            x, y = location.get_coordinates()
            direction = None
            if x == 0:
                if y == 0:
                    direction = random.choice([Direction.LEFT, Direction.DOWN])
                elif y == self.width - 1:
                    direction = random.choice([Direction.LEFT, Direction.UP])
                else:
                    direction = Direction.LEFT
            elif x == self.width - 1:
                if y == 0:
                    direction = random.choice([Direction.RIGHT, Direction.DOWN])
                elif y == self.width - 1:
                    direction = random.choice([Direction.RIGHT, Direction.UP])
                else:
                    direction = Direction.RIGHT
            else:
                if y == 0:
                    direction = Direction.DOWN
                elif y == self.height - 1:
                    direction = Direction.UP

            self.exits.append(Exit(location=location, direction=direction))

        print('Done.')
        return random.sample(safe_locations, k=len(safe_locations))

    def get_tile(self, location):
        return self.grid[location.x][location.y]

def _exit_location_compatible_with_river(exit_locations, river_tiles, board_height, board_width):
    river_tile_locations = [river_tile.location for river_tile in river_tiles]
    loc_to_river_tile_map = {}
    for river_tile in river_tiles:
        loc_to_river_tile_map[river_tile.location] = river_tile
    for exit_location in exit_locations:
        if exit_location in river_tile_locations:
            river_tile = loc_to_river_tile_map[exit_location]
            if river_tile.location.next_location(direction=river_tile.direction).in_bounds(board_height=board_height,
                                                                                           board_width=board_width):
                return False
    return True

def _create_safe_tile_matrix(width: int, height: int):
    matrix = []
    for x in range(width):
        matrix_row = []
        for y in range(height):
            matrix_row.append(Safe(Location(x=x, y=y)))
        matrix.append(matrix_row)
    return matrix
