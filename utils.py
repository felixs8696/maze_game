def get_yes_or_no_response(prompt):
    response = input(prompt)
    while response not in "YyNn":
        print("Invalid response.")
        response = input(prompt)
    return response


def response_is_yes(response):
    return response in "Yy"


def response_is_no(response):
    return response in "Nn"


def ask_for_options(objects):
    objects_options = ""
    range_of_objects = range(len(objects))
    for i in range_of_objects:
        objects_options += f"({i}) {objects[i].description()}\n"
    print(f"{objects_options}")
    index = input("Please choose one of the above options:")
    return index


def create_placeholder_matrix(width: int, height: int, placeholder):
    matrix = []
    for i in range(width):
        matrix_row = []
        for j in range(height):
            matrix_row.append(placeholder)
        matrix.append(matrix_row)
    return matrix
