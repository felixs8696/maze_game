import argparse

from src.utils_favorites import load_favorite_games, remove_game_from_favorite_games

if __name__ == '__main__':
    favorite_games = load_favorite_games()
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--unique_key", help="Unique ID for favorited game to remove.", type=str,
                        required=True)
    args = parser.parse_args()

    remove_game_from_favorite_games(args.unique_key)
