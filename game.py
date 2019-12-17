import numpy as np
import random

from typing import List

from board import Board
from player import Player
from movement import Movement
from datatypes import Direction
from constants import *

class Game:
    def __init__(self, board: Board, players: List[Player]):
        self.board = board
        self.players = self._randomize_player_order(players)
        self.active_player_index = 0
        self.game_over = False

    def display_board(self):
        exit_locations = [ex.location for ex in self.board.exits]
        exit_loc_to_dir_map = {}
        for ex in self.board.exits:
            exit_loc_to_dir_map[ex.location] = ex.direction

        print(TOP_LEFT_CORNER, end=" ")
        for x in range(self.board.width):
            if self.board.grid[x][self.board.height - 1].location not in exit_locations:
                print(HIGH_HORIZONTAL_LINE, end=" ")
            else:
                if exit_loc_to_dir_map[self.board.grid[x][self.board.height - 1].location] == Direction.UP:
                    print(EXIT_UP, end=" ")
                else:
                    print(HIGH_HORIZONTAL_LINE, end=" ")
        print(TOP_RIGHT_CORNER, end=" ")
        print()
        for y in range(self.board.height - 1, -1, -1):
            if self.board.grid[0][y].location not in exit_locations:
                print(VERTICAL_LINE, end =" ")
            else:
                if exit_loc_to_dir_map[self.board.grid[0][y].location] == Direction.LEFT:
                    print(EXIT_LEFT, end=" ")
                else:
                    print(VERTICAL_LINE, end=" ")
            for x in range(self.board.width):
                print(str(self.board.grid[x][y]), end =" ")
            if self.board.grid[self.board.width - 1][y].location not in exit_locations:
                print(VERTICAL_LINE, end =" ")
            else:
                if exit_loc_to_dir_map[self.board.grid[self.board.width - 1][y].location] == Direction.RIGHT:
                    print(EXIT_RIGHT, end=" ")
                else:
                    print(VERTICAL_LINE, end=" ")
            print()
        print(BOTTOM_LEFT_CORNER, end =" ")
        for x in range(self.board.width):
            if self.board.grid[x][0].location not in exit_locations:
                print(LOW_HORIZONTAL_LINE, end=" ")
            else:
                if exit_loc_to_dir_map[self.board.grid[x][0].location] == Direction.DOWN:
                    print(EXIT_DOWN, end=" ")
                else:
                    print(LOW_HORIZONTAL_LINE, end=" ")
        print(BOTTOM_RIGHT_CORNER, end=" ")
        print()

    @staticmethod
    def _randomize_player_order(players):
        random.shuffle(players)
        return players

    def next_player(self):
        self.active_player_index = (self.active_player_index + 1) % len(self.players)

    def begin_game(self):
        print('Beginning game...')
        print(f'Player order: ', self.players)

        while not self.game_over:
            active_player = self.players[self.active_player_index]
            active_player.begin_turn()
            while not active_player.is_turn_over():
                chosen_move = active_player.request_move()
                active_player.execute_move(chosen_move)
                if isinstance(chosen_move, Movement):
                    tile = self.board.get_tile(active_player.location)
                    game_tile_actions = tile.get_actions()
                    active_player.execute_mandatory_actions_and_get_remaining(game_tile_actions)
            active_player.end_turn()
            self.next_player()
