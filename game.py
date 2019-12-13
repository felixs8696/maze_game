import random

from typing import List

from .board import Board
from .player import Player
from .movement import Movement


class Game:
    def __init__(self, board: Board, players: List[Player]):
        self.board = board
        self.players = self._randomize_player_order(players)
        self.active_player_index = 0
        self.game_over = False

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
