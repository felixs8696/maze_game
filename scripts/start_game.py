import random
import argparse
import json
import os
import uuid
import _pickle as pickle

from src.game import Game
from src.board import Board
from src.constants import *
from src.game_board_configs import *
from src.utils import load_game_from_backup, get_backup_file_path


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


def ask_and_get_player_names_for_playable_board(num_players):
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
    parser.add_argument("-i", "--playable_game_index", help="Chosen game index from playable game index.", type=int,
                        default=-1)
    parser.add_argument("-a", "--auto_rng", help="Set to use a machine random number generator to get items from the shop and "
                                                 "battle other players. Otherwise, use real dice for randomness.",
                        action="store_true")
    parser.add_argument("-o", "--omniscient", help="Set this flag to see all game info each turn.", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(GAME_BACKUP_DIR):
        os.mkdir(GAME_BACKUP_DIR)

    if args.game_id is None:
        game_id = str(uuid.uuid4())
        print(f"Your game_id is {game_id}. Run `./restore_game {game_id}` to "
              f"restore your game if it crashes. Or  run `./restore_game_omniscient <game_id>` "
              "to restore a game in omniscient mode")

        if args.playable_game_index == -1:
            random_seed = random.randint(MIN_GAME_SEED, MAX_GAME_SEED)
            board_config = ask_for_board_config()
            player_names = ask_and_get_player_names()
            if not player_names:
                print(f"Not enough players. Quitting game.")
                exit(0)
        else:
            if args.playable_game_index >= len(PLAYABLE_GAME_BOARDS):
                print(f"Invalid --playable_game_index. Please choose a number in this range "
                      f"[0, {len(PLAYABLE_GAME_BOARDS) - 1}]")
                exit(0)

            print(f"Loading board from valid playable_game_index ({args.playable_game_index}). "
                  f"Ignoring all other command line arguments.")
            chosen_board_config = PLAYABLE_GAME_BOARDS[args.playable_game_index]
            random_seed = chosen_board_config[GAME_SEED]
            board_config = chosen_board_config[BOARD_CONFIG]
            player_names = ask_and_get_player_names_for_playable_board(num_players=chosen_board_config[NUM_PLAYERS])

        random.seed(random_seed)
        board = Board(**board_config, auto_rng=args.auto_rng)
        players = board.generate_safe_players(player_names=player_names)
        game = Game(board=board, players=players, game_id=game_id, random_seed=random_seed, display_all_info_each_turn=args.omniscient)

        print(f"Starting game...")
        current_game_board_config = get_game_board_config(random_seed, len(player_names), **board_config)
        print(f"This is your game config. If you like this board and it does not already exist in the playable game "
              f"database, please add this config to the database, so you can repeat this game: "
              f"{json.dumps(current_game_board_config, indent=2)}")

        game_backup_file_path = os.path.join(GAME_BACKUP_DIR, f'{game_id}.pkl')
        with open(game_backup_file_path, 'wb+') as f:
            pickle.dump(game, f)
    else:
        try:
            saved_game = load_game_from_backup(game_id=args.game_id)
            random.seed(saved_game.random_seed)
            game = Game.copy_from(game=saved_game)
        except FileNotFoundError:
            print(f"No save file found for game {args.game_id} at {get_backup_file_path(game_id=args.game_id)}.")
            exit(1)

    game.display_all_info_each_turn = args.omniscient
    game.begin_game()
