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
