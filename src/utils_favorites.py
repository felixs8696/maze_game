import os
import json
from enum import Enum
import random

from src.board import Board
from src.game import Game
from src.constants import FAVORITE_GAMES_FILE_PATH, STR_GAME_BOARDS_DIR

GAME_SEED = 'game_seed'
NUM_PLAYERS = 'num_players'
BOARD_CONFIG = 'board_config'


class SaveMethod(Enum):
    COMBINE = 1
    OVERRIDE = 2
    UNDEFINED = 3


def delete_favorite_games_file():
    if os.path.exists(FAVORITE_GAMES_FILE_PATH):
        os.remove(FAVORITE_GAMES_FILE_PATH)
        print(f"Deleted {FAVORITE_GAMES_FILE_PATH}.")
    else:
        print(f"Playable games file {FAVORITE_GAMES_FILE_PATH} does not exist. Nothing to delete.")


def save_favorite_games(favorite_games_dict, method=SaveMethod.UNDEFINED):
    if method == SaveMethod.OVERRIDE:
        if os.path.exists(FAVORITE_GAMES_FILE_PATH):
            print(f"Overriding favorite games file at: {FAVORITE_GAMES_FILE_PATH}")
        with open(FAVORITE_GAMES_FILE_PATH, 'w+') as f:
            json.dump(favorite_games_dict, f)
    elif method == SaveMethod.COMBINE:
        if os.path.exists(FAVORITE_GAMES_FILE_PATH):
            old_favorite_games_dict = load_favorite_games()
            favorite_games_dict = {
                **old_favorite_games_dict,
                **favorite_games_dict
            }
        with open(FAVORITE_GAMES_FILE_PATH, 'w+') as f:
            json.dump(favorite_games_dict, f)
    else:
        if not os.path.exists(FAVORITE_GAMES_FILE_PATH):
            with open(FAVORITE_GAMES_FILE_PATH, 'w+') as f:
                json.dump(favorite_games_dict, f)
        else:
            raise OSError(f"{FAVORITE_GAMES_FILE_PATH} already exists. "
                          f"To save, run with SaveMethod.COMBINE or SaveMethod.OVERRIDE.")


def load_favorite_games():
    favorite_games_dict = {}
    if os.path.exists(FAVORITE_GAMES_FILE_PATH):
        with open(FAVORITE_GAMES_FILE_PATH, 'r') as f:
            favorite_games_dict = json.load(f)
    return favorite_games_dict


def display_favorite_games():
    favorite_games = load_favorite_games()
    for key, game_config in favorite_games.items():
        str_game_board_file_path = get_str_game_board_file_path(key)
        print(f"Game Key: {key}")
        print(f"{json.dumps(game_config)}")
        with open(str_game_board_file_path, 'r') as f:
            print(f.read())
        print(f"Run `./new_game_from_favorites {key}` to restore this game or run "
              f"`./new_game_from_favorites_omniscient {key}` to run in omniscient mode.")
        print(f"To remove this game from your favorites list run `./delete_favorited_game {key}`.")
        print()
    return favorite_games


def add_game_to_favorite_games(game_config, key):
    game_config_already_exists = False
    try:
        favorite_games_dict = load_favorite_games()
    except OSError:
        favorite_games_dict = {}

    favorite_game_key = key

    for key, existing_game_config in favorite_games_dict.items():
        if json_equal(existing_game_config, game_config):
            game_config_already_exists = True
            favorite_game_key = key
            break

    if not game_config_already_exists:
        favorite_games_dict[favorite_game_key] = game_config
        save_favorite_games(favorite_games_dict, method=SaveMethod.OVERRIDE)
        save_str_board_for_game_config(favorite_game_key, game_config)
        print(f"Successfully added game to favorites at key {favorite_game_key}.")
    else:
        print(f"Game already exists in favorites at key: {favorite_game_key}")
    return favorite_game_key


def remove_game_from_favorite_games(key):
    favorite_games_dict = load_favorite_games()
    try:
        del favorite_games_dict[key]
        save_favorite_games(favorite_games_dict, method=SaveMethod.OVERRIDE)
    except KeyError:
        print(f"Game with key '{key}' not found.")

    str_game_board_file_path = get_str_game_board_file_path(key)
    if os.path.exists(str_game_board_file_path):
        os.remove(str_game_board_file_path)
        print(f"Deleted ASCII board file.")

    if len(favorite_games_dict) == 0:
        print("The favorited games list is empty. No games to remove.")
        return None


def get_game_board_config(seed, num_players, **game_board_args):
    return {
        GAME_SEED: seed,
        NUM_PLAYERS: num_players,
        BOARD_CONFIG: {
            **game_board_args
        }
    }


def save_str_board_for_game_config(favorite_game_key, game_config):
    random_seed = game_config[GAME_SEED]
    board_config = game_config[BOARD_CONFIG]

    random.seed(random_seed)
    board = Board(**board_config)
    game = Game(board=board, randomize_player_order=False, random_seed=random_seed)
    str_game_board_file_path = get_str_game_board_file_path(favorite_game_key)
    if not os.path.exists(STR_GAME_BOARDS_DIR):
        os.mkdir(STR_GAME_BOARDS_DIR)
    with open(str_game_board_file_path, "w+") as f:
        f.write(game.str_board())

    random.seed()


def get_str_game_board_file_path(favorite_game_key):
    return os.path.join(STR_GAME_BOARDS_DIR, f'{favorite_game_key}.txt')


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


def json_equal(a, b):
    return ordered(a) == ordered(b)
