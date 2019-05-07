from parser_classes import *

# global variables
VAR_NUMBER = {}
VAR_SIZES = []
VAR_SIGNING = []
INITIAL_VALUES = []
BOOLEAN_VAR_NUMBER = {}
BOOLEAN_INITIAL_VALUES = []
LIST_OF_COEFFS = []
MAX_NUMBER_OF_INTEGER_VARIABLES = 10
MAX_NUMBER_OF_BOOLEAN_VARIABLES = 2
EXIST_TRUE = 0b11
EXIST_FALSE = 0b10
NOT_EXIST = 0b00

def get_number(sign, width, base, value):
    """
    returns the value of the number represented in verilog style
    """
    if base is None or base == "'d" or base == "'D":  # decimal
        number = int(value)
    elif base == "'o" or base == "'O":  # octal
        number = int(value, 8)
    elif base == "'h" or base == "'H":  # hex
        number = int(value, 16)
    elif base == "'b" or base == "'B":  # binary
        number = int(value, 2)
    if sign == '-':
        number = number * -1
    return number


def fill_coeffs(term, coeffs, factor):
    if isinstance(term.term_type, Number):  # +5 or -5
        number = term.term_type
        sign = number.number.sign
        width = number.number.width
        base = number.number.base
        value = number.number.value
        number = get_number(sign, width, base, value)
        coeffs[-1] += (number * factor)
    if isinstance(term.term_type, IdentifierOnly):  # x or -x
        identifier = term.term_type.name
        var_number = VAR_NUMBER[identifier]
        if term.term_type == "-":
            coeffs[var_number] = -1 * factor
        else:
            coeffs[var_number] = 1 * factor
    if isinstance(term.term_type, CompositeTerm):  # 5*y or y*5
        first_op = term.term_type[0].primary_type
        second_op = term.term_type[1].primary_type
        if isinstance(first_op, Number):
            number = first_op
            identifier = second_op.thing
        else:
            number = second_op
            identifier = first_op.thing
        sign = number.number.sign
        width = number.number.width
        base = number.number.base
        value = number.number.value
        number = get_number(sign, width, base, value)
        var_number = VAR_NUMBER[identifier]
        coeffs[var_number] = number * factor


def parse_int_con_expression(int_con_expression_object):
    """
    """
    lhs_object = int_con_expression_object.lhs
    con_op = int_con_expression_object.con_op
    rhs_object = int_con_expression_object.rhs
    coeffs = [0] * MAX_NUMBER_OF_INTEGER_VARIABLES
    if con_op == "<=" or con_op == "<":
        lhs_factor = 1
        rhs_factor = -1
    elif con_op == ">=" or con_op == ">":
        lhs_factor = -1
        rhs_factor = 1
    for term in lhs_object:
        fill_coeffs(term, coeffs, lhs_factor)
    for term in rhs_object:
        fill_coeffs(term, coeffs, rhs_factor)
    if con_op == "<" or con_op == ">":
        coeffs[-1] += 1
    return coeffs

def parse_normal_constraint(normal_constraint):
    """
    """

    expression = normal_constraint.normal_con
    if isinstance(expression.exp_type, IntConExpression):  # integer constraints
        int_con_expression_object = expression.exp_type
        coeffs = parse_int_con_expression(int_con_expression_object)

    return coeffs

def parse_imply_constraint(imply_constraint):
    """
    var == 1 -> {}
    the variable must be unsigned .
    """
    # LHS of implication
    equality_expression = imply_constraint.equality_exp
    var_name = equality_expression.name
    operator = equality_expression[0]
    number = equality_expression[1]
    sign = number.number.sign
    width = number.number.width
    base = number.number.base
    value = number.number.value
    value = get_number(sign, width, base, value)
    # this var_name must be only boolean
    var_number = VAR_NUMBER[var_name]
    var_size = VAR_SIZES[var_number]
    number_of_boolean_variables_for_this_variable = var_size
    binary_value = bin(value)[2:].zfill(number_of_boolean_variables_for_this_variable)
    if not(BOOLEAN_VAR_NUMBER.__contains__(var_name)):
        BOOLEAN_VAR_NUMBER[var_name] = range(number_of_boolean_variables_for_this_variable)
    boolean_var_numbers = BOOLEAN_VAR_NUMBER[var_name]
    boolean_coeffs = [0]*MAX_NUMBER_OF_BOOLEAN_VARIABLES
    for boolean_var_number in boolean_var_numbers:
        boolean_coeffs[boolean_var_number] = 2 + int(not (int(binary_value[boolean_var_number])))
    # RHS of implication
    some_clauses = []
    constraint_set = imply_constraint.con_set.con_set_type
    if isinstance(constraint_set, ConstraintExpression):# x+y<1
        if isinstance(constraint_set.con_exp_type, NormalConstraint):
            normal_constraint = constraint_set.con_exp_type
            integer_coeffs = parse_normal_constraint(normal_constraint)
            clause = []
            clause.append(boolean_coeffs)
            clause.append(integer_coeffs)
            some_clauses.append(clause)
    else:  # { x+y<0; x+5<y; ....}
        for constraint in constraint_set:
            if isinstance(constraint.con_exp_type, NormalConstraint):
                normal_constraint = constraint.con_exp_type
                integer_coeffs = parse_normal_constraint(normal_constraint)
                clause = []
                clause.append(boolean_coeffs)
                clause.append(integer_coeffs)
                some_clauses.append(clause)
    return some_clauses

def parse_constraints(class_declaration_object):
    """
    use parse_constraints() to parse each constraint in the class declaration.
    """

    for class_item in class_declaration_object:

        if isinstance(class_item.item,
                      ClassConstraint):  # class constrinat,not class property
            if isinstance(class_item.item.class_con_type,
                          ConstraintDeclaration):  # not prototype
                constraint_block = class_item.item.class_con_type.con_block
                for constraint_block_item in constraint_block:
                    constraint_expression = constraint_block_item.con_exp
                    if isinstance(constraint_expression.con_exp_type, NormalConstraint):
                        normal_constraint = constraint_expression.con_exp_type
                        coeffs = parse_normal_constraint(normal_constraint)
                        LIST_OF_COEFFS.append(coeffs)
                    elif isinstance(constraint_expression.con_exp_type, ImplyConstraint):
                        imply_constraint = constraint_expression.con_exp_type
                        some_coeffs = parse_imply_constraint(imply_constraint)
                        LIST_OF_COEFFS.append(some_coeffs)
                    elif isinstance(constraint_expression.con_exp_type, IfConstraint):
                        pass
                    elif isinstance(constraint_expression.con_exp_type, ArrayConstraint):
                        pass
    return LIST_OF_COEFFS


def parse_data_declaration(data_declaration_parsed_object):
    """
    inputs:
    data declaration parsed object that contains string like int x=5;
    outputs:
    dictionary which maps variable name to number.
    list of variable sizes.
    list of initial values of variables.
    """

    list_of_variable_decl_assignment = data_declaration_parsed_object.list_of_variable_decl_assignment
    data_declaration_data_type = data_declaration_parsed_object.data_type
    integer_type = data_declaration_data_type.type.integer_type
    signing = data_declaration_data_type.type.signing
    if integer_type == IntegerAtomType('byte'):
        var_size = 8
        var_signing = "signed"
        if signing == "unsigned":
            var_signing = "unsigned"
    elif integer_type == IntegerAtomType('shortint'):
        var_size = 16
        var_signing = "signed"
        if signing == "unsigned":
            var_signing = "unsigned"
    elif integer_type == IntegerAtomType(
            'int') or integer_type == IntegerAtomType('integer'):
        var_size = 32
        var_signing = "signed"
        if signing == "unsigned":
            var_signing = "unsigned"
    elif integer_type == IntegerAtomType('longint'):
        var_size = 64
        var_signing = "signed"
        if signing == "unsigned":
            var_signing = "unsigned"
    elif integer_type == IntegerAtomType('time'):
        var_size = 64
        var_signing = "unsigned"
        if signing == "signed":
            var_signing = "signed"
    elif integer_type == IntegerVectorType(
            'bit') or integer_type == IntegerVectorType(
                'logic') or integer_type == IntegerVectorType('reg'):
        var_size = 1
        packed_dimensions = data_declaration_data_type.type.packed_dimensions
        if len(packed_dimensions) == 1:  # not array
            packed_dimension = packed_dimensions[0].type
            from_sign = packed_dimension.from_.number.sign
            from_width = packed_dimension.from_.number.width
            from_base = packed_dimension.from_.number.base
            from_value = packed_dimension.from_.number.value
            from_number = get_number(from_sign, from_width, from_base,
                                     from_value)
            to_sign = packed_dimension.to_.number.sign
            to_width = packed_dimension.to_.number.width
            to_base = packed_dimension.to_.number.base
            to_value = packed_dimension.to_.number.value
            to_number = get_number(to_sign, to_width, to_base, to_value)
            var_size = abs(from_number - to_number) + 1
        var_signing = "unsigned"
        if signing == "signed":
            var_signing = "signed"
    for var_decl_assignment in list_of_variable_decl_assignment:
        var_name = var_decl_assignment.name.name
        if var_decl_assignment.initial_value is not None:  # has initial value like x=5;
            initial_value_sign = var_decl_assignment.initial_value.number.sign
            initial_value_width = var_decl_assignment.initial_value.number.width
            initial_value_base = var_decl_assignment.initial_value.number.base
            initial_value_value = var_decl_assignment.initial_value.number.value
            initial_value = get_number(initial_value_sign, initial_value_width,
                                       initial_value_base, initial_value_value)
        else:
            initial_value = None
        dimension = var_decl_assignment.dimension
        if dimension == []:  # not array
            VAR_SIZES.append(var_size)
            VAR_SIGNING.append(var_signing)
            INITIAL_VALUES.append(initial_value)
            var_number = len(VAR_SIZES) - 1
            VAR_NUMBER[var_name] = var_number


# parse_data_declaration("reg [7:0] x = 5 ;")


def parse_data_declarations(class_declaration_object):
    """
    use parse_data_declaration() to parse each data declaration in the class declaration.
    """

    for class_item in class_declaration_object:

        if isinstance(class_item.item,
                      ClassConstraint):  # class constrinat,not class property
            continue
        data_declaration_object = class_item.item.data_declaration

        parse_data_declaration(data_declaration_object)
    return VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES
