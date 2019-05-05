from parser_classes import *
from parser_functions import *

# input sv file reading
INPUT_FILE_PATH = "code.txt"
with open(INPUT_FILE_PATH, "r") as input_file:
    SOURCE_CODE = input_file.read().replace("\n", "").strip(" ")
input_file.close()
C = parse(SOURCE_CODE, ClassDeclaration)
VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES = parse_data_declarations(C)
print(VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES)
LIST_OF_COEFFS = parse_constraints(C, VAR_NUMBER)
print(LIST_OF_COEFFS)