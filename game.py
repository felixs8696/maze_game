import numpy as np
import random

from typing import List

from board import Board
from player import Player
from movement import Movement
from datatypes import Direction
from constants import *
from tabulate import tabulate


class Game:
    def __init__(self, board: Board, players: List[Player]):
        self.board = board
        self.players = self._randomize_player_order(players)
        self.active_player_index = 0
        self.game_over = False

    def display_player_statuses(self):
        headers = ['Active', 'Name', 'Location', 'Status', 'Item', 'Treasure', 'Can Move', 'Lost Next Turn']
        player_data = []
        for player in self.players:
            data = [player.active, player.name, player.location, player.status.name, player.item, player.treasure,
                    player.can_move, player.lose_next_turn]
            data = [x if x is not None else 'None' for x in data]
            player_data.append(data)
        print(tabulate(player_data, headers=headers))

    def _get_exit_locations(self):
        return [ex.location for ex in self.board.exits]

    def _get_exit_loc_to_dir_map(self):
        exit_loc_to_dir_map = {}
        for ex in self.board.exits:
            exit_loc_to_dir_map[ex.location] = ex.direction
        return exit_loc_to_dir_map

    def _get_inner_wall_adj_loc_to_wall_map(self):
        inner_wall_adj_loc_to_wall_map = {}
        for wall in self.board.inner_walls:
            inner_wall_adj_loc_to_wall_map[wall.adjacent_locations] = wall
        return inner_wall_adj_loc_to_wall_map

    def _grid_top_row(self, exit_loc_to_dir_map, exit_locations):
        top_row = [TOP_LEFT_CORNER]
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
        bottom_row = [BOTTOM_LEFT_CORNER]
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

    def _single_wall_row(self, inner_wall_adj_loc_to_wall_map, y):
        wall_row = [VERTICAL_WALL]
        for x in range(self.board.width):
            adjacent_locations = (self.board.grid[x][y].location, self.board.grid[x][y + 1].location)
            rev_adjacent_locations = (self.board.grid[x][y + 1].location, self.board.grid[x][y].location)
            if adjacent_locations in inner_wall_adj_loc_to_wall_map or \
                    rev_adjacent_locations in inner_wall_adj_loc_to_wall_map:
                wall_row.append(HORIZONTAL_WALL)
            else:
                wall_row.append(EMPTY)
            if x < self.board.width - 1:
                wall_row.append(EMPTY)
        wall_row.append(VERTICAL_WALL)
        return wall_row

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

    def _single_grid_row(self, exit_loc_to_dir_map, exit_locations, inner_wall_adj_loc_to_wall_map, y):
        grid_row = []
        left_wall_or_exit = self._left_wall_or_exit(exit_loc_to_dir_map=exit_loc_to_dir_map,
                                                    exit_locations=exit_locations, y=y)
        grid_row.append(left_wall_or_exit)
        for x in range(self.board.width):
            grid_row.append(str(self.board.grid[x][y]))
            if x < self.board.width - 1:
                adjacent_locations = (self.board.grid[x][y].location, self.board.grid[x + 1][y].location)
                rev_adjacent_locations = (self.board.grid[x + 1][y].location, self.board.grid[x][y].location)
                if adjacent_locations in inner_wall_adj_loc_to_wall_map or \
                        rev_adjacent_locations in inner_wall_adj_loc_to_wall_map:
                    grid_row.append(VERTICAL_WALL)
                else:
                    grid_row.append(EMPTY)
        right_wall_or_exit = self._right_wall_or_exit(exit_loc_to_dir_map=exit_loc_to_dir_map,
                                                      exit_locations=exit_locations, y=y)
        grid_row.append(right_wall_or_exit)
        return grid_row

    @staticmethod
    def _optimize_wall_cross_sections(grid_middle_rows):
        mirrored_grid_middle_rows = grid_middle_rows[::-1]
        height = len(mirrored_grid_middle_rows)
        width = len(mirrored_grid_middle_rows[0])
        for y in range(height - 2, -1, -2):
            for x in range(2, width - 2, 2):
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

    def _grid_middle_rows(self, inner_wall_adj_loc_to_wall_map, exit_loc_to_dir_map, exit_locations):
        middle_rows = []
        for y in range(self.board.height - 1, -1, -1):
            if y < self.board.height - 1:
                middle_rows.append(self._single_wall_row(inner_wall_adj_loc_to_wall_map, y))
            middle_rows.append(self._single_grid_row(exit_loc_to_dir_map=exit_loc_to_dir_map,
                                                     exit_locations=exit_locations,
                                                     inner_wall_adj_loc_to_wall_map=inner_wall_adj_loc_to_wall_map,
                                                     y=y))

        middle_rows = self._optimize_wall_cross_sections(middle_rows)

        return middle_rows

    def display_board(self):
        exit_locations = self._get_exit_locations()
        exit_loc_to_dir_map = self._get_exit_loc_to_dir_map()
        inner_wall_adj_loc_to_wall_map = self._get_inner_wall_adj_loc_to_wall_map()

        grid_rows = []
        top_row = self._grid_top_row(exit_loc_to_dir_map=exit_loc_to_dir_map, exit_locations=exit_locations)
        middle_rows = self._grid_middle_rows(inner_wall_adj_loc_to_wall_map=inner_wall_adj_loc_to_wall_map,
                                             exit_loc_to_dir_map=exit_loc_to_dir_map,
                                             exit_locations=exit_locations)
        bottom_row = self._grid_bottom_row(exit_loc_to_dir_map=exit_loc_to_dir_map, exit_locations=exit_locations)
        grid_rows.append(top_row)
        grid_rows.extend(middle_rows)
        grid_rows.append(bottom_row)

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
        print('Beginning game...')
        # print(f'Player order: ', [player.name for player in self.players])

        while not self.game_over:
            active_player = self.players[self.active_player_index]
            active_player.begin_turn()
            print(f"{active_player.name}'s Turn.")
            self.display_player_statuses()
            while not active_player.is_turn_over():
                chosen_move = active_player.request_move()
                active_player.execute_move(chosen_move)
                if isinstance(chosen_move, Movement):
                    tile = self.board.get_tile(active_player.location)
                    game_tile_actions = tile.get_actions()
                    active_player.execute_mandatory_actions_and_get_remaining(game_tile_actions)
                self.display_player_statuses()
            active_player.end_turn()
            self.next_player()
