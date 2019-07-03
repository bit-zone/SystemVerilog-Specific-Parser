from parser_classes import *

# global variables
VAR_NUMBER = {}
VAR_SIZES = []
VAR_SIGNING = []
INITIAL_VALUES = []
BOOLEAN_VAR_NUMBER = {}
BOOLEAN_INITIAL_VALUES = []
IMP_VAR_INDEXES = [] # contains indexex of implication variables z==0->() or if(z==0) so, z is imp variable
DISCRETE_VAR_INDEXES = [] # contains indexex of discrete variables

MAX_NUMBER_OF_INTEGER_VARIABLES = 32 # excluding bias
MAX_NUMBER_OF_BOOLEAN_VARIABLES = 2
MAX_NUMBER_OF_DISCRETE_VARIABLES = 2
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
    coeffs = [0] * (MAX_NUMBER_OF_INTEGER_VARIABLES+1)
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

def parse_inside_expression(inside_expression):
    """
    """
    discrete_coeffs = []
    discrete_var_name = inside_expression.name
    DISCRETE_VAR_INDEXES.append(VAR_NUMBER[discrete_var_name])
    open_range_list = inside_expression.open_range_list
    for open_value_range in open_range_list:
        value_range = open_value_range.value_range
        if isinstance(value_range.value_range_type, Number):  # 5
            number = value_range.value_range_type
            sign = number.number.sign
            width = number.number.width
            base = number.number.base
            value = number.number.value
            number = get_number(sign, width, base, value)
            discrete_coeffs.append(number)
            discrete_coeffs.append(number)
        elif isinstance(value_range.value_range_type, RangeExpression): # [5:9]
            range_expression = value_range.value_range_type
            from_number = range_expression.from_num
            to_number = range_expression.to_num
            sign = from_number.number.sign
            width = from_number.number.width
            base = from_number.number.base
            value = from_number.number.value
            from_number = get_number(sign, width, base, value)
            sign = to_number.number.sign
            width = to_number.number.width
            base = to_number.number.base
            value = to_number.number.value
            to_number = get_number(sign, width, base, value)
            discrete_coeffs.append(from_number)
            discrete_coeffs.append(to_number)


    return discrete_coeffs


def parse_normal_constraint(normal_constraint):
    """
    """

    expression = normal_constraint.normal_con
    if isinstance(expression.exp_type, IntConExpression):  # integer constraints
        int_con_expression_object = expression.exp_type
        integer_coeffs = parse_int_con_expression(int_con_expression_object)
        # adding zeros boolean coeffs
        boolean_coeffs = [0]*MAX_NUMBER_OF_BOOLEAN_VARIABLES
        coeffs = []
        coeffs.append(boolean_coeffs)
        coeffs.append(integer_coeffs)
    elif isinstance(expression.exp_type, InsideExpression):  # inside constraints
        inside_expression_object = expression.exp_type
        coeffs = parse_inside_expression(inside_expression_object)

    return coeffs

def parse_equality_expression(equality_expression):
    """
    """
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
    binary_value = bin(value)[2:].zfill(
        number_of_boolean_variables_for_this_variable)
    if not (BOOLEAN_VAR_NUMBER.__contains__(var_name)):
        BOOLEAN_VAR_NUMBER[var_name] = range(
            number_of_boolean_variables_for_this_variable)
    boolean_var_numbers = BOOLEAN_VAR_NUMBER[var_name]
    boolean_coeffs = [0] * MAX_NUMBER_OF_BOOLEAN_VARIABLES
    for boolean_var_number in boolean_var_numbers:
        boolean_coeffs[boolean_var_number] = 2 + int(not (
            int(binary_value[boolean_var_number])))
    return boolean_coeffs, var_name


def parse_imply_constraint(imply_constraint):
    """
    var == 1 -> {}
    the variable must be unsigned .
    """
    # LHS of implication
    equality_expression = imply_constraint.equality_exp
    boolean_coeffs, var_name = parse_equality_expression(equality_expression)
    IMP_VAR_INDEXES.append(VAR_NUMBER[var_name])
    # RHS of implication
    some_clauses = []
    constraint_set = imply_constraint.con_set.con_set_type
    if isinstance(constraint_set, ConstraintExpression):# x+y<1
        if isinstance(constraint_set.con_exp_type, NormalConstraint):
            normal_constraint = constraint_set.con_exp_type
            coeffs = parse_normal_constraint(normal_constraint)
            coeffs[0] = boolean_coeffs
            some_clauses.append(coeffs)
    else:  # { x+y<0; x+5<y; ....}
        for constraint in constraint_set:
            if isinstance(constraint.con_exp_type, NormalConstraint):
                normal_constraint = constraint.con_exp_type
                coeffs = parse_normal_constraint(normal_constraint)
                coeffs[0] = boolean_coeffs
                some_clauses.append(coeffs)
    return some_clauses

def parse_if_constraint(if_constraint):
    """
    """
    # condition part
    equality_expression =if_constraint.equality_exp
    boolean_coeffs, var_name = parse_equality_expression(equality_expression)
    IMP_VAR_INDEXES.append(VAR_NUMBER[var_name])
    # constraint set
    some_clauses = []
    constraint_set = if_constraint.con_set.con_set_type
    if isinstance(constraint_set, ConstraintExpression):  # x+y<1
        if isinstance(constraint_set.con_exp_type, NormalConstraint):
            normal_constraint = constraint_set.con_exp_type
            coeffs = parse_normal_constraint(normal_constraint)
            coeffs[0] = boolean_coeffs
            some_clauses.append(coeffs)
    else:  # { x+y<0; x+5<y; ....}
        for constraint in constraint_set:
            if isinstance(constraint.con_exp_type, NormalConstraint):
                normal_constraint = constraint.con_exp_type
                coeffs = parse_normal_constraint(normal_constraint)
                coeffs[0] = boolean_coeffs
                some_clauses.append(coeffs)
    return some_clauses


def get_arr_name(constraint):
    if isinstance(constraint.con_exp_type, NormalConstraint):
        normal_constraint = constraint.con_exp_type
        exp = normal_constraint.normal_con
        if isinstance(exp.exp_type, IntConExpression):
            int_exp = exp.exp_type
            exp_lhs = int_exp.lhs
            for term in exp_lhs:
                if isinstance(term.term_type, IdentifierOnly):
                    ident = term.term_type
                    elem = ident.elem_name
                    arr_name = ident.name
    return arr_name


def get_arr_size(arr_name):
    
    arr_size = 0
    i = 0
    for k in VAR_NUMBER.keys():
        s = f"{arr_name.name}{i}"
        if k == s:
            arr_size += 1
            i += 1
    return arr_size


def parse_constraints(class_declaration_object):
    """
    use parse_constraints() to parse each constraint in the class declaration.
    """
    LIST_OF_COEFFS = []
    global IMP_VAR_INDEXES, DISCRETE_VAR_INDEXES
    IMP_VAR_INDEXES.clear()
    DISCRETE_VAR_INDEXES.clear()
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
                        LIST_OF_COEFFS+=some_coeffs
                    elif isinstance(constraint_expression.con_exp_type, IfConstraint):
                        if_constraint = constraint_expression.con_exp_type
                        some_coeffs = parse_if_constraint(if_constraint)
                        LIST_OF_COEFFS+=some_coeffs
                    elif isinstance(constraint_expression.con_exp_type, ArrayConstraint):
                        arr_constraint = constraint_expression.con_exp_type
                        constraint_set = arr_constraint.con_set.con_set_type

                        
                        for constraint in constraint_set:
                            arr_name = get_arr_name(constraint)
                            arr_size = get_arr_size(arr_name)
                            for i in range(arr_size):
                                # replace arr[i] with arr0, arr1 ,...
                                if isinstance(constraint.con_exp_type, NormalConstraint):
                                    normal_constraint = constraint.con_exp_type
                                    exp = normal_constraint.normal_con
                                    if isinstance(exp.exp_type, IntConExpression):
                                        int_exp = exp.exp_type
                                        exp_lhs = int_exp.lhs
                                        for term in exp_lhs:
                                            if isinstance(term.term_type, IdentifierOnly):
                                                ident = term.term_type
                                                elem = ident.elem_name

                                                if elem is not None:
                                                    ident.name = Symbol(f"{arr_name}{i}")

                                    coeffs = parse_normal_constraint(normal_constraint)
                                    LIST_OF_COEFFS.append(coeffs)
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
        else: # unpacked array
            unpack_dim = dimension[0].type # assume one dimension only , UnpackedDimension
            arr_size = unpack_dim.type.size # assume array size only [5] not [0:5]
            sign = arr_size.number.sign
            width = arr_size.number.width
            base = arr_size.number.base
            value = arr_size.number.value
            arr_size = get_number(sign, width, base, value)
            for i in range(arr_size):
                var_element_name = f"{var_name}{i}"
                VAR_SIZES.append(var_size)
                VAR_SIGNING.append(var_signing)
                INITIAL_VALUES.append(initial_value)
                var_number = len(VAR_SIZES) - 1
                VAR_NUMBER[var_element_name] = var_number



# parse_data_declaration("reg [7:0] x = 5 ;")


def parse_data_declarations(class_declaration_object):
    """
    use parse_data_declaration() to parse each data declaration in the class declaration.
    """
    global VAR_SIGNING,VAR_SIZES,INITIAL_VALUES,BOOLEAN_INITIAL_VALUES
    VAR_SIGNING = []
    VAR_SIZES = []
    INITIAL_VALUES = []
    BOOLEAN_INITIAL_VALUES = []
    VAR_NUMBER.clear()
    for class_item in class_declaration_object:

        if isinstance(class_item.item,
                      ClassConstraint):  # class constrinat,not class property
            continue
        data_declaration_object = class_item.item.data_declaration

        parse_data_declaration(data_declaration_object)
    return VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES, BOOLEAN_INITIAL_VALUES, BOOLEAN_VAR_NUMBER
