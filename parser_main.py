from parser_classes import *
from parser_functions import *

"""
we don't support else or not equal implication yet.
"""

def main_parser(SOURCE_CODE):
    """
    """
    C = parse(SOURCE_CODE, ClassDeclaration)
    VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES, BOOLEAN_INITIAL_VALUES, BOOLEAN_VAR_NUMBER = parse_data_declarations(C)
    LIST_OF_COEFFS = parse_constraints(C)
    return VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES, LIST_OF_COEFFS

# input sv file reading
INPUT_FILE_PATH = "code.txt"
with open(INPUT_FILE_PATH, "r") as input_file:
    SOURCE_CODE = input_file.read().replace("\n", "").strip(" ")
input_file.close()
# debugging mode
VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES, LIST_OF_COEFFS = main_parser(SOURCE_CODE)
print(VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES, LIST_OF_COEFFS)

# output in text file mode
def integer_initial_assignment_file_handling(initial_assignment_file_path, integer_initial_values):
    with open(initial_assignment_file_path, "w") as initial_assignment_file:
        disc,imp,integ = split_coeffs(integer_initial_values)
        for item in disc:
            if item is None:
                initial_assignment_file.write("0\n")
            else:
                initial_assignment_file.write(item)
        for item in imp:
            if item is None:
                initial_assignment_file.write("0\n")
            else:
                initial_assignment_file.write(item)
        for item in integ:
            if item is None:
                initial_assignment_file.write("0\n")
            else:
                initial_assignment_file.write(item)


def integer_sizes_file_handling(integer_sizes_file_path, integer_sizes):
    with open(integer_sizes_file_path, "w") as integer_sizes_file:
        disc,imp,integ = split_coeffs(integer_sizes)
        for item in disc:
            string_item = str(item)
            integer_sizes_file.write(string_item)
            integer_sizes_file.write("\n")
        for item in imp:
            string_item = str(item)
            integer_sizes_file.write(string_item)
            integer_sizes_file.write("\n")
        for item in integ:
            string_item = str(item)
            integer_sizes_file.write(string_item)
            integer_sizes_file.write("\n")

def split_coeffs(list_item):
    """
    split list of coeffs into 3 lists : discrete, implication, integer variables
    """
    disc=[]
    imp=[]
    integ=[]
                # split_coeffs list of coeffs [discrete imp integer]
                # using DISCRETE_VAR_INDEXES and IMP_VAR_INDEXES lists
    for i in range(len(list_item)): # integer part only
        if i in DISCRETE_VAR_INDEXES:
            disc.append(list_item[i])
        elif i in IMP_VAR_INDEXES:
            imp.append(list_item[i])
        else:
            integ.append(list_item[i])
    return disc, imp, integ
def integer_coeff_file_handling(integer_coeff_file_path, LIST_OF_COEFFS):
    with open(integer_coeff_file_path, "w") as integer_coeff_file:

        for list_item in LIST_OF_COEFFS:
            if len(list_item)==2: # formula (clause)
                disc,imp,integ = split_coeffs(list_item[1])
                for item in disc: 
                    string_item = str(item) 
                    integer_coeff_file.write(string_item)
                    integer_coeff_file.write("\n")
                for item in imp: 
                    string_item = str(item) 
                    integer_coeff_file.write(string_item)
                    integer_coeff_file.write("\n")
                for item in integ: 
                    string_item = str(item) 
                    integer_coeff_file.write(string_item)
                    integer_coeff_file.write("\n")



integer_initial_assignment_file_handling("integer_initial_values.txt", INITIAL_VALUES)
integer_sizes_file_handling("integer_sizes.txt", VAR_SIZES)
integer_coeff_file_handling("integer_coeff.txt", LIST_OF_COEFFS)
