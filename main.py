from game import Game
from board import Board
from player import Player

if __name__ == '__main__':
    board = Board(height=8, width=8, river_max_num_turns=4, num_marshes=8, num_river_tiles=12, num_hospitals=1, num_shops=1,
                  num_aa_portal_sets=1, num_ab_portal_sets=1, num_abc_portal_sets=1, num_treasures=2)
    players = []
    # players = [Player(initial_location=board.safe_locations.pop(), name='Bob'),
    #            Player(initial_location=random_safe_locations.pop(), name='Alice')]
    game = Game(board=board, players=players)
    game.display_board()
