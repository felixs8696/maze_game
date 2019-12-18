from game import Game
from board import Board
from player import Player

import numpy as np
import random

if __name__ == '__main__':
    # random.seed(1)
    board = Board(height=8, width=8, river_max_num_turns=4, num_marshes=8, num_river_tiles=12, num_hospitals=1,
                  num_shops=1, num_aa_portal_sets=1, num_ab_portal_sets=1, num_abc_portal_sets=1, num_treasures=2,
                  num_inner_walls=32, num_exits=2)
    num_players = 2
    player_locations = random.sample(board.safe_locations, k=num_players)
    player_names = ['Bob', 'Alice']
    players = []
    for i in range(num_players):
        players.append(Player(initial_location=player_locations[i], name=player_names[i]))
    game = Game(board=board, players=players)
    game.display_board()
    game.begin_game()
