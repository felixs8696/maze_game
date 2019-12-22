import os
import numpy as np

from constants import GAME_BACKUP_DIR
from utils import delete_game_backup, get_yes_or_no_response, response_is_yes_and_not_empty

if __name__ == '__main__':
    print(f"Saved game files:\n{np.array(os.listdir(GAME_BACKUP_DIR))}")
    prompt = f"Are you sure you want to delete all saved games? This will delete the files listed above. " \
             f"(y/n) (default=n):"
    response = get_yes_or_no_response(prompt)
    if response_is_yes_and_not_empty(response):
        for saved_file in os.listdir(GAME_BACKUP_DIR):
            game_id = saved_file.split('.')[0]
            delete_game_backup(game_id)
    else:
        print(f"Cancelling. No files deleted.")
