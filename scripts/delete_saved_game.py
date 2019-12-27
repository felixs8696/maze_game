import argparse
import os

from src.constants import GAME_BACKUP_DIR

from src.utils import get_backup_file_path, delete_game_backup, get_yes_or_no_response, response_is_yes_and_not_empty

if __name__ == '__main__':
    if os.path.exists(GAME_BACKUP_DIR):
        parser = argparse.ArgumentParser()
        parser.add_argument("-g", "--game_id", help="Enter a game id to delete a saved game.", type=str,
                            required=True)
        args = parser.parse_args()

        backup_file_path = get_backup_file_path(args.game_id)
        if os.path.exists(backup_file_path):
            prompt = f"Are you sure you want to delete the save file for game {args.game_id}? " \
                     f"This will delete file {backup_file_path}. (y/n) (default=n):"
            response = get_yes_or_no_response(prompt)
            if response_is_yes_and_not_empty(response):
                delete_game_backup(args.game_id)
            else:
                print(f"Cancelling. No files deleted.")
        else:
            print(f"Save file for game {args.game_id} does not exist at {backup_file_path}. Nothing to delete.")
    else:
        print(f"No saved games. Save directory '{GAME_BACKUP_DIR}' does not exist.")
