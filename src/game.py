import random
import time

from typing import List
from signal import signal, SIGINT

from src.board import Board
from src.player import Player
from src.movement import Movement
from src.datatypes import Direction, TileType
from src.symbols import *
from tabulate import tabulate
from src.exceptions import GameOver
from src.utils import get_yes_or_no_response, response_is_yes_and_not_empty, save_game_backup


class Game:
    def __init__(self, board: Board = None, players: List[Player] = None, randomize_player_order=True,
                 game_id: str = '', random_seed: int = 0, active_player_index: int = 0, game_over: bool = False,
                 display_all_info_each_turn=False):
        self.original_board = Board.copy_from(board=board)
        self.board = board
        self.random_seed = random_seed
        if randomize_player_order:
            self.players = self._randomize_player_order(players)
        else:
            self.players = players
        self.active_player_index = active_player_index
        self.game_over = game_over
        self.game_id = game_id
        self.display_all_info_each_turn = display_all_info_each_turn

    @staticmethod
    def copy_from(game):
        board = Board.copy_from(board=game.board)
        players = []
        for old_player in game.players:
            player = Player.copy_from(player=old_player)
            players.append(player)
        return Game(board=board, players=players, game_id=game.game_id, randomize_player_order=False,
                    random_seed=game.random_seed, active_player_index=game.active_player_index,
                    game_over=game.game_over, display_all_info_each_turn=game.display_all_info_each_turn)

    def reset(self):
        self.board = Board.copy_from(board=self.original_board)
        self.random_seed = self.random_seed
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

    def _grid_strings(self):
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

        return grid_rows

    def str_board(self):
        grid_rows = self._grid_strings()
        str_board = ""
        for row in grid_rows:
            for block in row:
                str_board += f"{block} "
            str_board += "\n"
        print(str_board)
        return str_board

    def display_board(self):
        grid_rows = self._grid_strings()
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

    def sigint_handler(self, signal_received, frame):
        print()
        print(f"Quitting game {self.game_id}. Run `./restore_game {self.game_id}` to restore this game. Or run "
              f"`./restore_game_omniscient {self.game_id}` to restore a game in omniscient mode")
        exit(0)

    def begin_game(self, auto_play=False, auto_turn_time_secs=1):
        signal(SIGINT, self.sigint_handler)
        print()
        print('Beginning game...\n')
        start = time.time()
        executed_moves = 0

        while not self.game_over:
            active_player = self.players[self.active_player_index]
            other_players = [player for player in self.players if player != active_player]
            active_player.begin_turn()
            tile = self.board.get_tile(active_player.location)
            available_tile_actions = tile.get_optional_actions(active_player)
            try:
                while not active_player.is_turn_over(other_players=other_players,
                                                     board=self.board,
                                                     available_tile_actions=available_tile_actions):
                    save_game_backup(game=self, game_id=self.game_id)
                    if self.display_all_info_each_turn:
                        print()
                        self.display_board()
                        self.display_player_statuses()
                    print(f"\n{active_player.name}'s Turn.")
                    original_location = active_player.location.copy()
                    chosen_move = active_player.request_move(other_players=other_players,
                                                             board=self.board,
                                                             available_tile_actions=available_tile_actions,
                                                             auto_play=auto_play,
                                                             auto_turn_time_secs=auto_turn_time_secs)
                    active_player.execute_move(chosen_move)
                    executed_moves += 1
                    if active_player.location != original_location:
                        if isinstance(chosen_move, Movement):
                            tile = self.board.get_tile(active_player.location)
                            tile.announce_tile(active_player)
                            if tile.type == TileType.HOSPITAL:
                                if not active_player.is_injured():
                                    print(f"{active_player.name} is not injured, so there is no need to heal.")
                            elif tile.type == TileType.SHOP:
                                if active_player.has_item():
                                    print(f"{active_player.name} is already holding an item, so he/she cannot acquire "
                                          f"another until the held item is dropped.")
                            active_player.execute_mandatory_actions()
                            active_player.show_colliding_players(other_players=other_players)
                    tile = self.board.get_tile(active_player.location)
                    available_tile_actions = tile.get_optional_actions(active_player)
                active_player.end_turn()
                self.next_player()

                display_game_info_prompt = 'Would you like to peek at the game board? (y/n): '
                if not self.display_all_info_each_turn:
                    print()
                    peek = get_yes_or_no_response(display_game_info_prompt)
                    if response_is_yes_and_not_empty(peek):
                        self.display_board()
                        self.display_player_statuses()
            except GameOver as e:
                print(f"{active_player.name} has exited the maze with the treasure and won the game.")
                self.display_board()
                self.display_player_statuses()
                end = time.time()
                print(f"Time taken to complete the game: {end - start} seconds.")
                print(f"{executed_moves} total moves made.")
                exit(0)
