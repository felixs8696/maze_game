import os
import numpy as np

from src.constants import GAME_BACKUP_DIR
from src.utils import delete_game_backup, get_yes_or_no_response, response_is_yes_and_not_empty

if __name__ == '__main__':
    if os.path.exists(GAME_BACKUP_DIR):
        print(f"Saved game files:\n{np.array(os.listdir(GAME_BACKUP_DIR))}")
        prompt = f"Are you sure you want to delete all saved games? This will delete the files listed above. " \
                 f"(y/n) (default=n):"
        response = get_yes_or_no_response(prompt)
        if response_is_yes_and_not_empty(response):
            all_saved_files = os.listdir(GAME_BACKUP_DIR)
            if len(all_saved_files) == 0:
                print(f"No saved games. Save directory '{GAME_BACKUP_DIR}' is empty.")
            else:
                for saved_file in all_saved_files:
                    game_id = saved_file.split('.')[0]
                    delete_game_backup(game_id)
        else:
            print(f"Cancelling. No files deleted.")
    else:
        print(f"No saved games. Save directory '{GAME_BACKUP_DIR}' does not exist.")
