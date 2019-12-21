import numpy as np
import random

from typing import List

from board import Board
from player import Player
from movement import Movement
from datatypes import Direction
from symbols import *
from tabulate import tabulate
from exceptions import GameOver


class Game:
    def __init__(self, board: Board, players: List[Player]):
        self.board = board
        self.players = self._randomize_player_order(players)
        self.active_player_index = 0
        self.game_over = False

    def display_player_statuses(self):
        headers = ['Active', 'Name', 'Location', 'Status', 'Item', 'Has Treasure', 'Can Move', 'Lost Next Turn']
        player_data = []
        for player in self.players:
            data = [player.active, player.name, player.location, player.status.name, str(player.item),
                    player.has_treasure, player.can_move, player.lose_next_turn]
            data = [x if x is not None else 'None' for x in data]
            player_data.append(data)
        print()
        print(tabulate(player_data, headers=headers))
        print()

    def _get_exit_locations(self):
        return [ex.location for ex in self.board.exits]

    def _get_exit_loc_to_dir_map(self):
        exit_loc_to_dir_map = {}
        for ex in self.board.exits:
            exit_loc_to_dir_map[ex.location] = ex.direction
        return exit_loc_to_dir_map

    def _grid_top_row(self, exit_loc_to_dir_map, exit_locations):
        top_row = [EMPTY, TOP_LEFT_CORNER]
        for x in range(self.board.width):
            if self.board.grid[x][self.board.height - 1].location not in exit_locations:
                top_row.append(HORIZONTAL_WALL)
            else:
                if exit_loc_to_dir_map[self.board.grid[x][self.board.height - 1].location] == Direction.UP:
                    top_row.append(EXIT_UP)
                else:
                    top_row.append(HORIZONTAL_WALL)
            if x < self.board.width - 1:
                top_row.append(HORIZONTAL_WALL)
        top_row.append(TOP_RIGHT_CORNER)
        return top_row

    def _grid_bottom_row(self, exit_loc_to_dir_map, exit_locations):
        bottom_row = [EMPTY, BOTTOM_LEFT_CORNER]
        for x in range(self.board.width):
            if self.board.grid[x][0].location not in exit_locations:
                bottom_row.append(HORIZONTAL_WALL)
            else:
                if exit_loc_to_dir_map[self.board.grid[x][0].location] == Direction.DOWN:
                    bottom_row.append(EXIT_DOWN)
                else:
                    bottom_row.append(HORIZONTAL_WALL)
            if x < self.board.width - 1:
                bottom_row.append(HORIZONTAL_WALL)
        bottom_row.append(BOTTOM_RIGHT_CORNER)
        return bottom_row

    def _horizontal_numbered_row(self):
        bottom_numbered_row = [EMPTY, EMPTY]
        for x in range(self.board.width):
            bottom_numbered_row.append(x)
            bottom_numbered_row.append(EMPTY)
        return bottom_numbered_row

    def _left_wall_or_exit(self, exit_loc_to_dir_map, exit_locations, y):
        if self.board.grid[0][y].location in exit_locations and \
                exit_loc_to_dir_map[self.board.grid[0][y].location] == Direction.LEFT:
            return EXIT_LEFT
        else:
            return VERTICAL_WALL

    def _right_wall_or_exit(self, exit_loc_to_dir_map, exit_locations, y):
        if self.board.grid[self.board.width - 1][y].location in exit_locations and \
                exit_loc_to_dir_map[self.board.grid[self.board.width - 1][y].location] == Direction.RIGHT:
            return EXIT_RIGHT
        else:
            return VERTICAL_WALL

    @staticmethod
    def _optimize_wall_cross_sections(grid_middle_rows):
        mirrored_grid_middle_rows = grid_middle_rows[::-1]
        height = len(mirrored_grid_middle_rows)
        width = len(mirrored_grid_middle_rows[0])
        for y in range(height - 2, -1, -2):
            for x in range(3, width - 2, 2):
                assert mirrored_grid_middle_rows[y][x] == EMPTY
                up = mirrored_grid_middle_rows[y + 1][x] == VERTICAL_WALL
                down = mirrored_grid_middle_rows[y - 1][x] == VERTICAL_WALL
                left = mirrored_grid_middle_rows[y][x - 1] == HORIZONTAL_WALL
                right = mirrored_grid_middle_rows[y][x + 1] == HORIZONTAL_WALL

                cross_section = WALL_CROSS_SECTION_MAP.get((up, down, left, right))
                if cross_section is None:
                    cross_section = EMPTY
                mirrored_grid_middle_rows[y][x] = cross_section
        unmirrored_grid_middle_rows = mirrored_grid_middle_rows[::-1]
        return unmirrored_grid_middle_rows

    def _location_to_display_board_coords(self, location):
        return ((self.board.height - 1) * 2) - (location.y * 2), (location.x * 2) + 2

    def _create_middle_rows(self, exit_loc_to_dir_map, exit_locations):
        grid_middle_rows = []
        for y in range(self.board.height - 1, -1, -1):
            inner_tile_row = [y]
            left_wall_or_exit = self._left_wall_or_exit(exit_loc_to_dir_map=exit_loc_to_dir_map,
                                                        exit_locations=exit_locations, y=y)
            inner_tile_row.append(left_wall_or_exit)
            for x in range(self.board.width):
                inner_tile_row.append(str(self.board.grid[x][y]))
                if x < self.board.width - 1:
                    inner_tile_row.append(EMPTY)

            right_wall_or_exit = self._right_wall_or_exit(exit_loc_to_dir_map=exit_loc_to_dir_map,
                                                          exit_locations=exit_locations, y=y)
            inner_tile_row.append(right_wall_or_exit)
            grid_middle_rows.append(inner_tile_row)

            if y > 0:
                empty_wall_row = [EMPTY, VERTICAL_WALL]
                for x in range(self.board.width):
                    empty_wall_row.append(EMPTY)
                    if x < self.board.width - 1:
                        empty_wall_row.append(EMPTY)
                empty_wall_row.append(VERTICAL_WALL)
                grid_middle_rows.append(empty_wall_row)

        for wall in self.board.inner_walls:
            loc_1, loc_2 = wall.adjacent_locations
            db_coord_1_x, db_coord_1_y = self._location_to_display_board_coords(loc_1)
            db_coord_2_x, db_coord_2_y = self._location_to_display_board_coords(loc_2)
            higher_x = max(db_coord_1_x, db_coord_2_x)
            lower_x = min(db_coord_1_x, db_coord_2_x)
            higher_y = max(db_coord_1_y, db_coord_2_y)
            lower_y = min(db_coord_1_y, db_coord_2_y)
            assert higher_x - lower_x == 2 or higher_y - lower_y == 2
            if higher_x - lower_x == 2:
                assert higher_y == lower_y
                wall_x = higher_x - 1
                wall_y = higher_y
                wall_type = HORIZONTAL_WALL
                grid_middle_rows[wall_x][wall_y] = wall_type
            elif higher_y - lower_y == 2:
                assert higher_x == lower_x
                wall_x = higher_x
                wall_y = higher_y - 1
                wall_type = VERTICAL_WALL
                grid_middle_rows[wall_x][wall_y] = wall_type

        grid_middle_rows = self._optimize_wall_cross_sections(grid_middle_rows)
        return grid_middle_rows

    def display_board(self):
        # print(np.array([str(wall) for wall in self.board.inner_walls]))
        exit_locations = self._get_exit_locations()
        exit_loc_to_dir_map = self._get_exit_loc_to_dir_map()

        grid_rows = []
        top_row = self._grid_top_row(exit_loc_to_dir_map=exit_loc_to_dir_map, exit_locations=exit_locations)
        middle_rows = self._create_middle_rows(exit_loc_to_dir_map=exit_loc_to_dir_map,
                                               exit_locations=exit_locations)
        bottom_row = self._grid_bottom_row(exit_loc_to_dir_map=exit_loc_to_dir_map, exit_locations=exit_locations)
        horizontal_numbered_row = self._horizontal_numbered_row()
        grid_rows.append(horizontal_numbered_row)
        grid_rows.append(top_row)
        grid_rows.extend(middle_rows)
        grid_rows.append(bottom_row)
        grid_rows.append(horizontal_numbered_row)

        for row in grid_rows:
            for block in row:
                print(block, end=" ")
            print()

    @staticmethod
    def _randomize_player_order(players):
        random.shuffle(players)
        return players

    def next_player(self):
        self.active_player_index = (self.active_player_index + 1) % len(self.players)

    def begin_game(self):
        print()
        print('Beginning game...\n')
        # print(f'Player order: ', [player.name for player in self.players])

        while not self.game_over:
            active_player = self.players[self.active_player_index]
            other_players = [player for player in self.players if not player == active_player]
            active_player.begin_turn()
            # available_tile_actions = []
            tile = self.board.get_tile(active_player.location)
            available_tile_actions = tile.get_optional_actions(active_player)
            while not active_player.is_turn_over(other_players=other_players,
                                                 board=self.board,
                                                 available_tile_actions=available_tile_actions):
                print(f"{[str(ex) for ex in self.board.exits]}")
                self.display_board()
                self.display_player_statuses()
                print(f"\n{active_player.name}'s Turn.")
                original_location = active_player.location.copy()
                chosen_move = active_player.request_move(other_players=other_players,
                                                         board=self.board,
                                                         available_tile_actions=available_tile_actions)
                try:
                    active_player.execute_move(chosen_move)
                except GameOver as e:
                    print(f"{active_player.name} has exited the maze with the treasure and won the game.")
                    self.display_board()
                    self.display_player_statuses()
                    exit(0)
                # tile = self.board.get_tile(active_player.location)
                # available_tile_actions = tile.get_optional_actions()
                if active_player.location != original_location:
                    if isinstance(chosen_move, Movement):
                        active_player.execute_mandatory_actions()
                        active_player.show_colliding_players(other_players=other_players)
                tile = self.board.get_tile(active_player.location)
                available_tile_actions = tile.get_optional_actions(active_player)
            active_player.end_turn()
            self.next_player()
