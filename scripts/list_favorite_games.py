from src.utils_favorites import display_favorite_games


if __name__ == '__main__':
    favorite_games = display_favorite_games()
    if len(favorite_games) == 0:
        print(f"No favorites found. Run `./add_game_to_favorites <game_config> <unique_key>` to add a game to "
              f"favorites")
