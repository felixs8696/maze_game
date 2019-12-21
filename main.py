import random

from game import Game
from board import Board


if __name__ == '__main__':
    random.seed(5)
    board = Board(height=8, width=8, river_max_num_turns=4, num_marshes=8, num_river_tiles=12, num_hospitals=1,
                  num_shops=1, num_aa_portal_sets=1, num_ab_portal_sets=1, num_abc_portal_sets=1, num_treasures=2,
                  num_inner_walls=10, num_exits=2)
    player_names = ['Bob', 'Alice']
    players = board.generate_safe_players(player_names=player_names)
    game = Game(board=board, players=players, display_all_info_each_turn=True)
    game.begin_game()
