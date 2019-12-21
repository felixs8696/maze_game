GAME_SEED = 'game_seed'
NUM_PLAYERS = 'num_players'
BOARD_CONFIG = 'board_config'

def get_game_board_config(seed, num_players, **game_board_args):
    return {
        GAME_SEED: seed,
        NUM_PLAYERS: num_players,
        BOARD_CONFIG: {
            **game_board_args
        }
    }

PLAYABLE_GAME_BOARDS = {
    0: get_game_board_config(seed=5, num_players=2, height=8, width=8, river_max_num_turns=4, num_marshes=8, num_river_tiles=12,
                             num_hospitals=1, num_shops=1, num_aa_portal_sets=1, num_ab_portal_sets=1,
                             num_abc_portal_sets=1, num_treasures=2, num_inner_walls=10, num_exits=2),
    1: {"game_seed": 0,
        "num_players": 2,
        "board_config": {
            "height": 10,
            "width": 10,
            "river_max_num_turns": 6,
            "num_marshes": 16,
            "num_river_tiles": 16,
            "num_hospitals": 2,
            "num_shops": 2,
            "num_aa_portal_sets": 1,
            "num_ab_portal_sets": 1,
            "num_abc_portal_sets": 1,
            "num_treasures": 3,
            "num_inner_walls": 32,
            "num_exits": 2
        }
    }
}
