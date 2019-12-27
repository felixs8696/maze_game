import os
import _pickle as pickle

from constants import *

def get_yes_or_no_response(prompt):
    response = input(prompt)
    while response not in "YyNn":
        print("Invalid response.")
        response = input(prompt)
    return response


def response_is_yes_and_not_empty(response):
    if response != '':
        return response.lower() == 'yes' or response in "Yy"
    return False


def response_is_yes(response):
    return response.lower() == 'yes' or response in "Yy"


def response_is_no(response):
    return response in "Nn"


def ask_for_options(objects):
    objects_options = ""
    range_of_objects = range(len(objects))
    for i in range_of_objects:
        objects_options += f"({i}) {objects[i].description()}\n"
    print(f"{objects_options}")
    index = input("Please choose one of the above options (Press CTRL+C to quit the game): ")
    return index


def create_placeholder_matrix(width: int, height: int, placeholder):
    matrix = []
    for i in range(width):
        matrix_row = []
        for j in range(height):
            matrix_row.append(placeholder)
        matrix.append(matrix_row)
    return matrix


def prompt_real_dice_roll_result(player):
    number = -1
    while not 1 <= number <= 6:
        number = int(input(f"{player.name} roll a die and enter the number you get: ") or -1)
        if not 1 <= number != 6:
            print(f"Invalid dice roll {number}. Try again.")
    return number


def generate_dice_roll_map(one=None, two=None, three=None, four=None, five=None, six=None):
    dice_map = {
        1: one,
        2: two,
        3: three,
        4: four,
        5: five,
        6: six
    }

    for i in range(1,7):
        assert i in dice_map

    return dice_map


def get_backup_file_path(game_id):
    return os.path.join(GAME_BACKUP_DIR, f'{game_id}.pkl')


def delete_game_backup(game_id):
    game_backup_file_path = get_backup_file_path(game_id)
    if os.path.exists(game_backup_file_path):
        os.remove(game_backup_file_path)
        print(f"Deleted {game_backup_file_path}.")
    else:
        print(f"Save file {game_backup_file_path} does not exist. Nothing to delete.")


def save_game_backup(game, game_id):
    game_backup_file_path = get_backup_file_path(game_id)
    with open(game_backup_file_path, 'wb+') as f:
        pickle.dump(game, f)


def load_game_from_backup(game_id):
    game_backup_file_path = get_backup_file_path(game_id)
    with open(game_backup_file_path, 'rb') as f:
        game = pickle.load(f)
    return game
