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
    index = input("Please choose one of the above options: ")
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

