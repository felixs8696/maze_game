import os
import time
from tabulate import tabulate

from constants import GAME_BACKUP_DIR

if __name__ == '__main__':
    timestamp_game_id_tuples = []
    for saved_file in os.listdir(GAME_BACKUP_DIR):
        game_id = saved_file.split('.')[0]
        timestamp = os.path.getmtime(os.path.join(GAME_BACKUP_DIR, saved_file))
        timestamp_game_id_tuples.append((timestamp, game_id))
    timestamp_game_id_tuples.sort(key=lambda x: x[0])

    headers = ['Time Saved', 'Game ID']
    local_time_game_id_data = []
    for timestamp, game_id in timestamp_game_id_tuples:
        local_time = time.strftime("%A, %D %B %Y, %r", time.localtime(timestamp))
        local_time_game_id_data.append([local_time, game_id])
    print(tabulate(local_time_game_id_data, headers=headers))
    print()
    print("Run `python main.py -r <game_id>` to restore one of these games.")
