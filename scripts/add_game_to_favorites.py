import argparse
import json

from src.utils_favorites import add_game_to_favorite_games


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--unique_key", help="Enter a game config save this game to favorites.", type=str,
                        required=True)
    parser.add_argument("-c", "--game_config", help="Enter a game config save this game to favorites.", type=str,
                        required=True)
    args = parser.parse_args()

    game_config = json.loads(args.game_config)
    key = add_game_to_favorite_games(game_config, args.unique_key)
    print(f"Run `./new_game_from_favorites {key}` to restore this game or run "
          f"`./new_game_from_favorites_omniscient {key}` to  run in omniscient mode.")
