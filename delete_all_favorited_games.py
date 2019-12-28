import os
import numpy as np

from src.constants import STR_GAME_BOARDS_DIR
from src.utils import get_yes_or_no_response, response_is_yes_and_not_empty
from src.utils_favorites import remove_game_from_favorite_games

if __name__ == '__main__':
    if os.path.exists(STR_GAME_BOARDS_DIR):
        backup_files = os.listdir(STR_GAME_BOARDS_DIR)
        print(f"Favorited games and boards giles:\n{np.array(backup_files)}")
        prompt = f"Are you sure you want to delete all favorited games? This will delete the files listed above. " \
                 f"(y/n) (default=n):"
        response = get_yes_or_no_response(prompt)
        if response_is_yes_and_not_empty(response):
            all_saved_files = os.listdir(STR_GAME_BOARDS_DIR)
            if len(all_saved_files) == 0:
                print(f"No saved game boards. Save directory '{STR_GAME_BOARDS_DIR}' is empty.")
            else:
                for saved_file in all_saved_files:
                    key = saved_file.split('.')[0]
                    remove_game_from_favorite_games(key=key)
        else:
            print(f"Cancelling. No favorited games deleted.")
    else:
        print(f"No favorited games. Save directory '{STR_GAME_BOARDS_DIR}' does not exist.")
