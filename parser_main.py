from parser_classes import *
from parser_functions import *

"""
we don't support else or not equal implication yet.
"""


# input sv file reading
INPUT_FILE_PATH = "code.txt"
with open(INPUT_FILE_PATH, "r") as input_file:
    SOURCE_CODE = input_file.read().replace("\n", "").strip(" ")
input_file.close()
C = parse(SOURCE_CODE, ClassDeclaration)
VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES, BOOLEAN_INITIAL_VALUES, BOOLEAN_VAR_NUMBER = parse_data_declarations(C)
print(VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES, BOOLEAN_INITIAL_VALUES, BOOLEAN_VAR_NUMBER)
LIST_OF_COEFFS = parse_constraints(C)
print(LIST_OF_COEFFS)


def integer_initial_assignment_file_handling(initial_assignment_file_path, integer_initial_values):
    with open(initial_assignment_file_path, "w") as initial_assignment_file:

        for item in integer_initial_values:
            if item is None:
                initial_assignment_file.write("0\n")
            else:
                initial_assignment_file.write(item)


def integer_sizes_file_handling(integer_sizes_file_path, integer_sizes):
    with open(integer_sizes_file_path, "w") as integer_sizes_file:

        for item in integer_sizes:
            string_item = str(item)
            integer_sizes_file.write(string_item)
            integer_sizes_file.write("\n")

print(IMP_VAR_INDEXES)

integer_initial_assignment_file_handling("integer_initial_values.txt", INITIAL_VALUES)
integer_sizes_file_handling("integer_sizes.txt", VAR_SIZES)
