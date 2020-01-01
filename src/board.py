import random
import timeout_decorator
import numpy as np
from typing import List

from src.datatypes import TileType, TileCategories, Direction
from src.tiles import TileFactory, Tile, Safe, PortalType
from src.location import Location
from src.borders import Wall, Exit
from src.player import Player
from src.exceptions import ZeroRemainingSafeTiles
from src.utils import create_placeholder_matrix, manhattan_distance


class Board:
    def __init__(self, height=8, width=8, river_max_num_turns=2, num_marshes=8, num_river_tiles=12, num_hospitals=1,
                 num_shops=1, num_aa_portal_sets=1, num_ab_portal_sets=1, num_abc_portal_sets=1, num_treasures=2,
                 num_inner_walls=20, num_exits=2, inner_walls=None, exits=None, grid=None, generate_contents=True,
                 border_locations=None, all_locations=None, safe_locations=None, auto_rng=False):
        self.auto_rng = auto_rng
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
                TileType.PORTAL: {
                    PortalType.FAKE: num_aa_portal_sets,
                    PortalType.AB: num_ab_portal_sets,
                    PortalType.ABC: num_abc_portal_sets
                }
            }
        }

        self.river_max_num_turns = river_max_num_turns
        self.num_exits = num_exits
        self.num_inner_walls = num_inner_walls
        self.inner_walls = inner_walls
        self.exits = exits
        self.grid = grid
        if generate_contents:
            self.border_locations = self._get_border_locations()
            self.all_locations = [Location(x=x, y=y) for x in range(self.width) for y in range(self.height)]
            self.safe_locations = self.generate_contents()
        else:
            self.border_locations = border_locations
            self.all_locations = all_locations
            self.safe_locations = safe_locations

    @staticmethod
    def copy_from(board, auto_rng: bool = False):
        return Board(height=board.height, width=board.width, river_max_num_turns=board.river_max_num_turns,
                     num_marshes=board.num_tiles[TileCategories.STATIC][TileType.MARSH],
                     num_river_tiles=board.num_tiles[TileCategories.DYNAMIC][TileType.RIVER],
                     num_hospitals=board.num_tiles[TileCategories.STATIC][TileType.HOSPITAL],
                     num_shops=board.num_tiles[TileCategories.STATIC][TileType.SHOP],
                     num_aa_portal_sets=board.num_tiles[TileCategories.DYNAMIC][TileType.PORTAL][PortalType.FAKE],
                     num_ab_portal_sets=board.num_tiles[TileCategories.DYNAMIC][TileType.PORTAL][PortalType.AB],
                     num_abc_portal_sets=board.num_tiles[TileCategories.DYNAMIC][TileType.PORTAL][PortalType.ABC],
                     num_treasures=board.num_tiles[TileCategories.STATIC][TileType.TREASURE],
                     num_inner_walls=board.num_inner_walls, num_exits=board.num_exits,
                     inner_walls=board.inner_walls, exits=board.exits, grid=board.grid, generate_contents=False,
                     border_locations=board.border_locations, all_locations=board.all_locations,
                     safe_locations=board.safe_locations, auto_rng=auto_rng)

    def get_heat_map(self):
        heat_map = create_placeholder_matrix(height=self.height, width=self.width, placeholder=0)
        for location in self.all_locations:
            neighbors = location.neighbors(board_height=self.height, board_width=self.width)
            for neighbor_location in neighbors:
                if location.no_walls_block_straight_line_location(location=neighbor_location, walls=self.inner_walls,
                                                                  board_height=self.height, board_width=self.width):
                    resting_location = neighbor_location
                    x, y = neighbor_location.get_coordinates()
                    tile = self.grid[x][y]
                    if tile.type == TileType.RIVER:
                        resting_location = neighbor_location.next_location(direction=tile.direction)
                        if not resting_location.in_bounds(board_height=self.height, board_width=self.width):
                            resting_location = neighbor_location
                    if tile.type == TileType.PORTAL:
                        resting_location = tile.exit_location

                    final_x, final_y = resting_location.get_coordinates()
                    heat_map[final_x][final_y] += 1
        return np.flipud(np.array(heat_map).transpose())

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
                                                                                            walls=inner_walls,
                                                                                            board_height=self.height,
                                                                                            board_width=self.width):
                    queue.append(neighbor)

        untraversed_locations = []
        for k, v in visited.items():
            if not visited[k]:
                untraversed_locations.append(k)
        return untraversed_locations

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

    def _assign_river_tiles(self, river_tiles, safe_locations):
        if len(safe_locations) < len(river_tiles):
            raise ZeroRemainingSafeTiles(f"Not enough safe tiles remaining for {len(river_tiles)} {TileType.RIVER.name} tiles.")
        for river_tile in river_tiles:
            safe_locations = self._assign_tile_to_grid(tile=river_tile, remaining_locations=safe_locations)
        return safe_locations

    def _assign_portal_tiles(self, safe_locations):
        num_fake_portals = self.num_tiles[TileCategories.DYNAMIC][TileType.PORTAL][PortalType.FAKE]
        if len(safe_locations) < num_fake_portals:
            raise ZeroRemainingSafeTiles(f"Not enough safe tiles remaining for {len(num_fake_portals)} fake portal tiles.")
        for _ in range(num_fake_portals):
            aa_portal = TileFactory.create_type_a_portal_tile(location=random.choice(list(safe_locations)))
            safe_locations = self._assign_tile_to_grid(tile=aa_portal, remaining_locations=safe_locations)

        num_ab_portal_sets = self.num_tiles[TileCategories.DYNAMIC][TileType.PORTAL][PortalType.AB]
        if len(safe_locations) < num_ab_portal_sets * 2:
            raise ZeroRemainingSafeTiles(f"Not enough safe tiles remaining for {len(num_ab_portal_sets)} AB portal sets.")
        for _ in range(num_ab_portal_sets):
            locations = random.sample(list(safe_locations), k=2)
            ab_portal, ba_portal = TileFactory.create_type_ab_portal_tiles(locations=locations)
            safe_locations = self._assign_tile_to_grid(tile=ab_portal, remaining_locations=safe_locations)
            safe_locations = self._assign_tile_to_grid(tile=ba_portal, remaining_locations=safe_locations)

        num_abc_portal_sets = self.num_tiles[TileCategories.DYNAMIC][TileType.PORTAL][PortalType.ABC]
        if len(safe_locations) < num_abc_portal_sets * 3:
            raise ZeroRemainingSafeTiles(f"Not enough safe tiles remaining for {len(num_abc_portal_sets)} AB portal sets.")
        for _ in range(self.num_tiles[TileCategories.DYNAMIC][TileType.PORTAL][PortalType.ABC]):
            locations = random.sample(list(safe_locations), k=3)
            ab_portal, bc_portal, ca_portal = TileFactory.create_type_abc_portal_tiles(locations=locations)
            safe_locations = self._assign_tile_to_grid(tile=ab_portal, remaining_locations=safe_locations)
            safe_locations = self._assign_tile_to_grid(tile=bc_portal, remaining_locations=safe_locations)
            safe_locations = self._assign_tile_to_grid(tile=ca_portal, remaining_locations=safe_locations)
        return safe_locations

    def _assign_static_tiles(self, safe_locations):
        for tile_type, num_tiles in self.num_tiles[TileCategories.STATIC].items():
            if len(safe_locations) < num_tiles:
                raise ZeroRemainingSafeTiles(f"Not enough safe tiles remaining for {num_tiles} {tile_type.name} tiles.")
            for _ in range(num_tiles):
                location = random.choice(list(safe_locations))
                static_tile = TileFactory.create_static_tile(tile_type=tile_type, location=location)
                safe_locations = self._assign_tile_to_grid(tile=static_tile, remaining_locations=safe_locations)
        return safe_locations

    def _generate_inner_walls(self, river_tiles):
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
                    valid_wall = True
                    inner_walls.add(wall)

                    if any([loc == river_tiles[-1].location for loc in wall.adjacent_locations]):
                        valid_wall = False
                        inner_walls.remove(wall)
                    elif any([loc == river_tiles[0].location for loc in wall.adjacent_locations]):
                        valid_wall = False
                        inner_walls.remove(wall)
                    elif self._wall_forms_tunnel_next_to_river(wall, inner_walls):
                        valid_wall = False
                        inner_walls.remove(wall)
                    elif len(self.get_untraversable_locations_from_origin(list(inner_walls))) != 0:
                        valid_wall = False
                        inner_walls.remove(wall)

        return tuple(inner_walls)

    def _wall_forms_tunnel_next_to_river(self, wall, inner_walls):
        for other_wall in inner_walls:
            loc_a1, loc_b1 = wall.adjacent_locations
            loc_a2, loc_b2 = other_wall.adjacent_locations
            x_a1, y_a1 = loc_a1.get_coordinates()
            x_b1, y_b1 = loc_b1.get_coordinates()
            x_a2, y_a2 = loc_a2.get_coordinates()
            x_b2, y_b2 = loc_b2.get_coordinates()
            if x_a1 == x_b1 == x_a2 == x_b2:
                if y_a1 == y_a2 or y_a1 == y_b2:
                    if x_a1 - 1 >= 0 and self.grid[x_a1 - 1][y_a1].type == TileType.RIVER:
                        return True
                    if x_a1 + 1 < self.width and self.grid[x_a1 + 1][y_a1].type == TileType.RIVER:
                        return True
                if y_a2 == y_b1 or y_a2 == y_b2:
                    if x_a1 - 1 >= 0 and self.grid[x_a1 - 1][y_a2].type == TileType.RIVER:
                        return True
                    if x_a1 + 1 < self.width and self.grid[x_a1 + 1][y_a2].type == TileType.RIVER:
                        return True
            if y_a1 == y_b1 == y_a2 == y_b2:
                if x_a1 == x_a2 or x_a1 == x_b2:
                    if y_a1 - 1 >= 0 and self.grid[x_a1][y_a1 - 1].type == TileType.RIVER:
                        return True
                    if y_a1 + 1 < self.height and self.grid[x_a1][y_a1 + 1].type == TileType.RIVER:
                        return True
                if x_a2 == x_b1 or x_a2 == x_b2:
                    if y_a1 - 1 >= 0 and self.grid[x_a2][y_a1 - 1].type == TileType.RIVER:
                        return True
                    if y_a1 + 1 < self.height and self.grid[x_a2][y_a2 + 1].type == TileType.RIVER:
                        return True
        return False

    def _get_furthest_exits_from_treasure(self, river_tiles) -> List[Location]:
        treasure_locations = []
        for location in self.all_locations:
            tile = self.get_tile(location=location)
            if tile.has_treasure():
                treasure_locations.append(location)

        potential_exit_location_to_treasure_dists_map = {}
        for potential_exit_location in self.border_locations:
            distance_to_treasures = []
            for treasure_location in treasure_locations:
                distance_to_treasures.append(manhattan_distance(potential_exit_location, treasure_location))
            potential_exit_location_to_treasure_dists_map[potential_exit_location] = tuple(distance_to_treasures)

        potential_exit_locations = []
        for potential_exit_location, treasure_distances in potential_exit_location_to_treasure_dists_map.items():
            if min(treasure_distances) >= 3:
                potential_exit_locations.append(potential_exit_location)

        valid_exit_locations = []
        river_tile_locations = [river_tile.location for river_tile in river_tiles]
        for potential_exit_location in potential_exit_locations:
            if potential_exit_location not in river_tile_locations:
                valid_exit_locations.append(potential_exit_location)

        min_manhattan_dist_between_exits = 5
        distance_between_exits = 0
        final_exit_locations = None
        while final_exit_locations is None or distance_between_exits < min_manhattan_dist_between_exits:
            final_exit_locations = random.sample(valid_exit_locations, k=self.num_exits)
            exit_location_1, exit_location_2 = final_exit_locations
            distance_between_exits = manhattan_distance(exit_location_1, exit_location_2)

        return final_exit_locations

    def _generate_exits(self, river_tiles):
        exits = []
        exit_locations = self._get_furthest_exits_from_treasure(river_tiles=river_tiles)
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

            exits.append(Exit(location=location, direction=direction))
        return exits

    @timeout_decorator.timeout(15)
    def generate_contents(self):
        self.grid = _create_safe_tile_matrix(width=self.width, height=self.height)
        safe_locations = set(self.grid[x][y].location for x in range(self.width) for y in range(self.height))

        river_tiles = TileFactory.create_full_river(
            max_river_length=self.num_tiles[TileCategories.DYNAMIC][TileType.RIVER],
            max_num_turns=self.river_max_num_turns,
            board_height=self.height,
            board_width=self.width)

        print(f"Generating river")
        safe_locations = self._assign_river_tiles(river_tiles, safe_locations)
        print(f"Generating portals")
        safe_locations = self._assign_portal_tiles(safe_locations)
        print(f"Generating static tiles")
        safe_locations = self._assign_static_tiles(safe_locations)
        print(f"Generating inner walls")
        self.inner_walls = self._generate_inner_walls(river_tiles=river_tiles)
        print(f"Generating exits")
        self.exits = self._generate_exits(river_tiles=river_tiles)
        return random.sample(safe_locations, k=len(safe_locations))

    def get_tile(self, location):
        x, y = location.get_coordinates()
        return self.grid[x][y]

    def generate_safe_players(self, player_names):
        num_players = len(player_names)
        if num_players > len(self.safe_locations):
            raise ZeroRemainingSafeTiles("Insufficient safe locations to spawn players on.")
        player_locations = random.sample(self.safe_locations, k=num_players)
        players = []
        for i in range(num_players):
            players.append(Player(name=player_names[i], location=player_locations[i].copy(), board=self,
                                  tile_most_recently_encountered=self.get_tile(location=player_locations[i]),
                                  auto_rng=self.auto_rng))
        return players


def _exit_location_compatible_with_river(exit_locations, river_tiles):
    river_tile_locations = [river_tile.location for river_tile in river_tiles]
    for exit_location in exit_locations:
        if exit_location in river_tile_locations:
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


# For debugging only
def debug_board_tiles(board):
    for x in range(board.width):
        for y in range(board.height):
            tile = board.grid[x][y]
            print(f"Assigned {str(tile)} tile to {tile.location} at grid[{x}][{y}]")
