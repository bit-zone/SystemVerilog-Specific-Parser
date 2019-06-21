def parse_data_declaration(data_declaration_parsed_object, VAR_NUMBER,
                           VAR_SIZES, VAR_SIGNING, INITIAL_VALUES):
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
        for var_decl_assignment in list_of_variable_decl_assignment:
            var_name = var_decl_assignment.name.name
            if var_decl_assignment.initial_value != None:  # has initial value like x=5;
                initial_value_sign = var_decl_assignment.initial_value.number.sign
                initial_value_width = var_decl_assignment.initial_value.number.width
                initial_value_base = var_decl_assignment.initial_value.number.base
                initial_value_value = var_decl_assignment.initial_value.number.value
                initial_value = get_number(initial_value_sign,
                                           initial_value_width,
                                           initial_value_base,
                                           initial_value_value)
            else:
                initial_value = None
            dimension = var_decl_assignment.dimension
            if dimension == []:  # not array
                VAR_SIZES.append(var_size)
                VAR_SIGNING.append(var_signing)
                INITIAL_VALUES.append(initial_value)
                var_number = len(VAR_SIZES) - 1
                VAR_NUMBER[var_name] = var_number
    elif integer_type == IntegerAtomType('shortint'):
        pass
    elif integer_type == IntegerAtomType(
            'int') or integer_type == IntegerAtomType('integer'):
        pass
    elif integer_type == IntegerAtomType('longint'):
        pass
    elif integer_type == IntegerAtomType('time'):
        pass
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
            if var_decl_assignment.initial_value != None:  # has initial value like x=5;
                initial_value_sign = var_decl_assignment.initial_value.number.sign
                initial_value_width = var_decl_assignment.initial_value.number.width
                initial_value_base = var_decl_assignment.initial_value.number.base
                initial_value_value = var_decl_assignment.initial_value.number.value
                initial_value = get_number(initial_value_sign,
                                           initial_value_width,
                                           initial_value_base,
                                           initial_value_value)
            else:
                initial_value = None
            dimension = var_decl_assignment.dimension
            if dimension == []:  # not array
                VAR_SIZES.append(var_size)
                VAR_SIGNING.append(var_signing)
                INITIAL_VALUES.append(initial_value)
                var_number = len(VAR_SIZES) - 1
                VAR_NUMBER[var_name] = var_number

D = parse("byte x;",)