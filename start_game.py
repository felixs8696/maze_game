import random
import argparse
import json
import os
import uuid
import time
import matplotlib.pyplot as plt

from timeout_decorator.timeout_decorator import TimeoutError

from src.game import Game
from src.board import Board
from src.constants import *
from src.utils_favorites import save_favorite_games, load_favorite_games, get_game_board_config, \
    GAME_SEED, BOARD_CONFIG, NUM_PLAYERS
from src.utils import load_game_from_backup, get_backup_file_path, save_game_backup, get_yes_or_no_response, \
    response_is_yes
from src.exceptions import ZeroRemainingSafeTiles


def ask_for_board_config():
    print(f"Set Up Game Board")
    board_height = int(input(f"Board height (Rec: 6-12, default=8): ") or 8)
    print(f"Chosen board height: {board_height}\n")
    board_width = int(input(f"Board width (Rec: 6-12, default=8): ") or 8)
    print(f"Chosen board width: {board_width}\n")
    num_river_tiles = 0
    while num_river_tiles <= board_height and num_river_tiles <= board_width:
        num_river_tiles = int(input(f"Number of River Tiles (Rec: 12-14, default=12): ") or 12)
        if num_river_tiles <= board_height and num_river_tiles <= board_width:
            print(f"Number of river tiles must be at least as much as either the height or width of the board.")
    print(f"Chosen number of river tiles: {num_river_tiles}\n")
    river_max_num_turns = int(input(f"Max Number of River Bends (Rec: 2-4, default=4): ") or 4)
    print(f"Chosen max number of river bends: {river_max_num_turns}\n")
    num_marshes = int(input(f"Number of Marshes (Rec: 6-10, default=8): ") or 8)
    print(f"Chosen number of marshes: {num_marshes}\n")
    num_hospitals = int(input(f"Number of Hospitals (Rec: 1, default=1): ") or 1)
    print(f"Chosen number of hospitals: {num_hospitals}\n")
    num_shops = int(input(f"Number of Shops (Rec: 1, default=1): ") or 1)
    print(f"Chosen number of shops: {num_shops}\n")
    num_aa_portal_sets = int(input(f"Number of AA Portal Sets (1 portal each) (Rec: 1, default=1): ") or 1)
    print(f"Chosen number of AA portal sets: {num_aa_portal_sets}\n")
    num_ab_portal_sets = int(input(f"Number of AB Portal Sets (2 portals each) (Rec: 1, default=1): ") or 1)
    print(f"Chosen number of AB portal sets: {num_ab_portal_sets}\n")
    num_abc_portal_sets = int(input(f"Number of ABC Portal Sets (3 portals each) (Rec: 1, default=1): ") or 1)
    print(f"Chosen number of ABC portal sets: {num_abc_portal_sets}\n")
    num_treasures = int(input(f"Number of Treasure tiles (Rec: 2, default=2): ") or 2)
    print(f"Chosen number of treasure tiles: {num_treasures}\n")
    num_inner_walls = int(input(f"Number of Inner Walls (Rec: 10-25, default=20): ") or 20)
    print(f"Chosen number of inner walls: {num_inner_walls}\n")
    num_exits = int(input(f"Number of Exits (Rec: 2, default=2): ") or 2)
    print(f"Chosen number of exits: {num_exits}\n")
    print()

    return dict(height=board_height, width=board_width, river_max_num_turns=river_max_num_turns,
                num_marshes=num_marshes, num_river_tiles=num_river_tiles, num_hospitals=num_hospitals,
                num_shops=num_shops, num_aa_portal_sets=num_aa_portal_sets, num_ab_portal_sets=num_ab_portal_sets,
                num_abc_portal_sets=num_abc_portal_sets, num_treasures=num_treasures, num_inner_walls=num_inner_walls,
                num_exits=num_exits)


def ask_and_get_player_names():
    print("Add players to the game")
    player_names = []
    while True:
        player_name = ''
        while player_name == '':
            player_name = input("Player name (type 'done' to stop adding players): ")
            if player_name == '':
                print(f"Invalid player name. Try again.")
        if player_name.lower() != 'done':
            player_names.append(player_name)
        else:
            break

    print(f"Added {player_names} to the game.")
    print()
    return player_names


def ask_and_get_player_names_for_favorite_board(num_players):
    print(f"This game board requires {num_players} players. Please add their names.")
    player_names = []
    while len(player_names) < num_players:
        player_names.append(input('Player name: '))
    print()
    return player_names


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--game_id", help="Enter a game id to restore an unfinished game.", type=str,
                        default=None)
    parser.add_argument("-k", "--unique_key", help="Chosen unique key from available favorite game keys.", type=str,
                        default=None)
    parser.add_argument("-d", "--auto_rng", help="Set to use a machine random number generator to get items from the "
                                                 "shop and battle other players. Otherwise, use real dice for "
                                                 "randomness.",
                        action="store_true")
    parser.add_argument("-o", "--omniscient", help="Set this flag to see all game info each turn.", action="store_true")
    parser.add_argument("-a", "--auto_play", help="Set this flag to have all players auto-play against each other "
                                                  "as random-strategy computers.", action="store_true")
    parser.add_argument("-t", "--auto_play_turn_time", help="Number of seconds each auto player should take per turn.",
                        type=int, default=1)
    parser.add_argument("-n", "--num_auto_play_profile_times", help="Number of times to average auto play stats over",
                        type=int, default=1)
    args = parser.parse_args()

    if not os.path.exists(GAME_BACKUP_DIR):
        os.mkdir(GAME_BACKUP_DIR)

    if args.game_id is None:
        game_id = str(uuid.uuid4())
        print(f"Your game_id is {game_id}. Run `./restore_game {game_id}` to "
              f"restore your game if it crashes. Or  run `./restore_game_omniscient {game_id}` "
              "to restore a game in omniscient mode.\n")

        if args.unique_key is None:
            random_seed = random.randint(MIN_GAME_SEED, MAX_GAME_SEED)
            board_config = ask_for_board_config()
            player_names = ask_and_get_player_names()
            if not player_names:
                print(f"Not enough players. Quitting game.")
                exit(0)
        else:
            favorite_game_boards = load_favorite_games()
            if args.unique_key not in favorite_game_boards:
                print(f"Invalid --unique_key. Please from one of the following game keys {favorite_game_boards.keys()}")
                exit(0)

            print(f"Loading favorited game board: '{args.unique_key}'.")
            chosen_board_config = favorite_game_boards[args.unique_key]
            random_seed = chosen_board_config[GAME_SEED]
            board_config = chosen_board_config[BOARD_CONFIG]

            if not args.auto_play:
                prompt = f"Would you like to play with the original number of players " \
                    f"({chosen_board_config[NUM_PLAYERS]}) for this favorited board? (y/n): "
                player_with_orig_num_players = get_yes_or_no_response(prompt)

                if response_is_yes(player_with_orig_num_players):
                    player_names = ask_and_get_player_names_for_favorite_board(
                        num_players=chosen_board_config[NUM_PLAYERS])
                else:
                    player_names = ask_and_get_player_names()
            else:
                player_names = [f"Player {i + 1}" for i in range(chosen_board_config[NUM_PLAYERS])]
            print()

        random.seed(random_seed)
        print('Generating board (This may take a while)...')
        print()
        try:
            board = Board(**board_config, auto_rng=args.auto_rng)
        except ZeroRemainingSafeTiles as e:
            print(f"{e}. Too many non-safe tiles assigned to the board. Please assign less non-safe tiles.")
            exit(1)
        except TimeoutError:
            print(f"Cancelling program. Took longer than 15 seconds to generate the board. "
                  f"Please play with a smaller board.")
            exit(1)
        try:
            players = board.generate_safe_players(player_names=player_names)
        except ZeroRemainingSafeTiles as e:
            print(f"{e}. Insufficient safe locations to spawn players on. Please assign less non-safe tiles.")
            exit(1)
        game = Game(board=board, players=players, game_id=game_id, random_seed=random_seed,
                    display_all_info_each_turn=args.omniscient)

        print(f"Starting game...")
        current_game_board_config = get_game_board_config(random_seed, len(player_names), **board_config)
        print(f"This is your game config. If you like this board and you did not already add it to your favorite, "
              f"please run `./add_game_to_favorites '{json.dumps(current_game_board_config)}' <unique_key>`"
              f"so you can repeat this game.")

        save_game_backup(game, game_id)
    else:
        try:
            saved_game = load_game_from_backup(game_id=args.game_id)
            random.seed(saved_game.random_seed)
            game = Game.copy_from(game=saved_game)
        except FileNotFoundError:
            print(f"No save file found for game {args.game_id} at {get_backup_file_path(game_id=args.game_id)}.")
            exit(1)

    game.display_all_info_each_turn = args.omniscient
    if not args.auto_play:
        game.run(auto_play=False)
    else:
        heat_map = game.original_board.get_heat_map()
        plt.imshow(heat_map, cmap='Wistia')
        print(f"Board movement heat map:\n{heat_map}")
        print(f"Close heat map plot to continue.")
        plt.show()

        list_of_time_taken_in_secs = []
        list_of_num_executed_moves = []
        for i in range(args.num_auto_play_profile_times):
            time_taken_in_secs, num_executed_moves = game.run(auto_play=args.auto_play,
                                                              auto_turn_time_secs=args.auto_play_turn_time)
            print(f"Game played: {i}")
            print(f"Time taken to complete the game: {time_taken_in_secs} seconds.")
            print(f"{num_executed_moves} total moves made.")
            list_of_time_taken_in_secs.append(time_taken_in_secs)
            list_of_num_executed_moves.append(num_executed_moves)

            print(f"Average time taken to complete game in sec (over {i + 1} games)): "
                  f"{sum(list_of_time_taken_in_secs) / len(list_of_time_taken_in_secs)}")
            print(f"List of times taken: {list_of_time_taken_in_secs}")
            print(f"Average number of total moves made (over {i + 1} games): "
                  f"{sum(list_of_num_executed_moves) / len(list_of_num_executed_moves)}")
            print(f"List of moves made: {list_of_num_executed_moves}")

            game.reset()
