"""This module parse  systemVerilog code"""
from pypeg2 import *
MAX_NUMBER_OF_INTEGER_VARIABLES = 10

UNSIGNED_DIGITS = re.compile(r"\d+")
OPTIONAL_SIGN = re.compile(r"[-+]?")
BASE = re.compile(r"'b|'B|'d|'D|'o|'O|'h|'H")
BINARYOPERATOR = re.compile(r"\+|-|\*|/|%|==|!=|&&|\|\||\*\*|<=|>=|<|>")
CON_OPERATOR = re.compile(r"<=|>=|<|>")
"""
The Base token controls what number digits
are legal.Base must be one of d, h, o, or b, for the bases decimal,
hexadecimal, octal, and binary respectively.
"""
class BinaryOperator(str):
    """
    """
    grammar = attr("op", [
        "+", "-", "*", "/", "%", "==", "!=", "&&", "||", "**", "<=", ">=", "<",
        ">", "&", "|", "^", "^~", "~^", "<<", ">>", "==?", "!=?"
    ])


class RandomQualifier(Keyword):
    """
    the keywords for declare a random variables in systemVerilog .
    Note that here we deal with randc as rand.
    """
    grammar = Enum(K("rand"), K("randc"))

class Signing(Keyword):
    """
    this is optional while declaring a variable in systemVerilog.
    it can be signed or unsigned.
    """
    grammar = Enum(K("signed"), K("unsigned"))
class IntegerVectorType(Keyword):
    """
    the type of vector of the variable .
    it can be bit, logic or, reg.
    we deal all the 3 integer vector types as each other.
    bit : 2-state SystemVerilog data type, user-defined vector size
    logic : 4-state SystemVerilog data type, user-defined vector size
    reg : 4-state Verilog-2001 data type, user-defined vector size
    """
    grammar = Enum(K("bit"), K("logic"), K("reg"))

class IntegerAtomType(Keyword):
    """
    the integer types of declaring a variable in SystemVerilog.
    byte | shortint | int | longint | integer | time .
    byte : 2-state SystemVerilog data type, 8 bit signed integer
    shortint : 2-state SystemVerilog data type, 16 bit signed integer
    int : 2-state SystemVerilog data type, 32 bit signed integer
    longint : 2-state SystemVerilog data type, 64 bit signed integer
    integer : 4-state Verilog-2001 data type, 32 bit signed integer
    time : 4-state Verilog-2001 data type, 64-bit unsigned integer
    """
    grammar = Enum(K("byte"), K("shortint"), K("int"), K("longint"), K("integer"), K("time"))

# Note that we don't support or parse non-integer types

class IntegerType(str):
    """
    integer_vector_type | integer_atom_type
    """
    grammar = [attr("type", IntegerVectorType), attr("type", IntegerAtomType)]




class DefaultNumber(str):
    """
    default decimal-base numbers like 5 or -6
    """
    grammar = attr("sign", OPTIONAL_SIGN), attr("value", UNSIGNED_DIGITS), attr("base", None), attr("width", None)

class BaseOnlyNumber(str):
    """
    base only numbers like 'b0 or 'hA
    """
    grammar = attr("sign", OPTIONAL_SIGN), attr("base", BASE), attr("width", None), attr("value", word)  # value may be hex (contains alphapetic)


class WidthBaseNumber(str):
    """
    numbers like 5'd2 or -7'd1
    """
    grammar = attr("sign", OPTIONAL_SIGN), attr("width", UNSIGNED_DIGITS), attr("base", BASE), attr("value", word)  # value may be hex (contains alphapetic)


class Number(str):
    """
    numbers in verilog and SystemVerilog : 7'd5 ,5, -7'h4
    """
    grammar = attr("number", [WidthBaseNumber, BaseOnlyNumber, DefaultNumber])

"""
example of parsing numbers:

F = parse(r"2'h1", Number)
print(F.number.sign)
print(F.number.width)
print(F.number.base)
print(F.number.value)
"""

def get_number(sign, width, base, value):
    """
    returns the value of the number represented in verilog style
    """
    if base is None or base == "'d" or base == "'D": # decimal
        number = int(value)
    elif base == "'o" or base == "'O": # octal
        number = int(value, 8)
    elif base == "'h" or base == "'H": # hex
        number = int(value, 16)
    elif base == "'b" or base == "'B": # binary
        number = int(value, 2)
    if sign == '-':
        number = number * -1
    return number


class ConstantRange(str):
    """
    constant range is [from : to]
    """
    grammar = "[", attr("from_", Number), ":", attr("to_", Number), "]"
class ArraySize(str):
    """
    like [20]
    """
    grammar = "[", Number, "]"
class UnpackedDimension(str):
    """
     constant_range  | [ constant ]
    """
    grammar = [ConstantRange, ArraySize]
class UnsizedDimension(str):
    """
    []
    """
    grammar = "[", "]"
class PackedDimension(str):
    """
     constant_range  | unsized_dimension
    """
    grammar = attr("type", [ConstantRange, UnsizedDimension])
class VectorDataType(str):
    """
    like bit [1:0] or bit
    """
    grammar = attr("integer_type", IntegerVectorType), attr(
        "signing", optional(Signing)), attr("packed_dimensions", maybe_some(PackedDimension))


class AtomDataType(str):
    """
    like int
    """
    grammar = attr("integer_type", IntegerAtomType), attr("signing", optional(Signing))
class DataType(str):
    """
    we don't deal with enums.
    """
    grammar = attr("type", [VectorDataType, AtomDataType])

class VariableDimension(str):
    """
    unsized_dimension | unpacked_dimension
    """
    grammar = [UnsizedDimension, UnpackedDimension]
class BinaryExpression(List):
    """
    has binary operator
    like x+5<y
    """
    pass
    #grammar = Expression, BinaryOperator, Expression
class Term(List):
    pass

class IntConExpression(str):
    """
    x+5<0
    """
    pass
class Primary(str):
    """
    """
    grammar = attr("primary_type", [Number, name()])
class RangeExpression(str):
    """
    [ expression : expression ]
    """
    pass
    #grammar = "[", Expression, ":", Expression, "]"
class ValueRange(str):
    """
    """
    pass
    #grammar = [Expression, RangeExpression]
class OpenValueRange(str):
    """
    """
    grammar = ValueRange
class OpenRangeList(str):
    """
    """
    grammar = OpenValueRange, maybe_some(",", OpenValueRange)
class InsideExpression(str):
    """
    inside_expression ::= expression inside { open_range_list }
    """
    pass
    #grammar = Expression, K("inside"), maybe_some(OpenRangeList)
class Expression(str):
    """
    like 20 or x+5<y
    """
    grammar = attr("exp_type", [InsideExpression, IntConExpression, Primary])

class CompositeTerm(List):
    pass
class IdentifierOnly(str):
    pass
CompositeTerm.grammar = Primary, "*", Primary
IdentifierOnly.grammar = OPTIONAL_SIGN, name()
Term.grammar = attr("term_type", [CompositeTerm, Number, IdentifierOnly])
IntConExpression.grammar = attr("lhs", some(Term)), attr("con_op", CON_OPERATOR), attr("rhs", some(Term))
BinaryExpression.grammar = Primary, maybe_some(BINARYOPERATOR, Primary)
RangeExpression.grammar = "[", Primary, ":", Primary, "]"
ValueRange.grammar = [Primary, RangeExpression]
InsideExpression.grammar = name(), K("inside"), "{", OpenRangeList, "}"

#INT_CON_EXPRESSION_OBJECT = parse("-5*y<x-10", IntConExpression)



def fill_coeffs(term, coeffs, factor):
    if isinstance(term.term_type, Number): # +5 or -5
        number = term.term_type
        sign = number.number.sign
        width = number.number.width
        base = number.number.base
        value = number.number.value
        number = get_number(sign, width, base, value)
        coeffs[-1] += (number*factor)
    if isinstance(term.term_type, IdentifierOnly):  # x or -x
        identifier = term.term_type.name
        var_number = VAR_NUMBER[identifier]
        if term.term_type == "-":
            coeffs[var_number] = -1*factor
        else:
            coeffs[var_number] = 1*factor
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
        coeffs[var_number] = number*factor


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



class VariableDeclAssignment(str):
    """
    like x=5 or x  or x[10] or x[0:10]
    we don't handle dynamic arrays.
    we don't handle class instantiation.
    we accept only one variable dimension.
    """
    grammar = name(), attr("dimension", maybe_some(VariableDimension)), attr("initial_value", optional("=", Number))
class ListOfVariableDeclAssignments(List):
    """
    like x,y or x=5,y=6
    """
    grammar = VariableDeclAssignment, maybe_some(",", VariableDeclAssignment)

class DataDeclaration(str):
    """
    like int x;
    we don't handle type declaration .
    we don't handle implicit data types .
    """
    grammar = attr("data_type", DataType), attr(
        "list_of_variable_decl_assignment", ListOfVariableDeclAssignments), ";"


class PropertyQualifier(str):
    """
    property_qualifier ::= random_qualifier | class_item_qualifier
    """
    grammar = RandomQualifier


class ClassProperty(str):
    """
    class_property ::= { property_qualifier } data_declaration
                 | const { class_item_qualifier } data_type const_identifier [ = constant_expression ] ;
    we assume that class property can only be data declaration.
    """
    grammar = maybe_some(PropertyQualifier), attr("data_declaration", DataDeclaration)
class LoopVariables(str):
    """
    loop_variables ::= [ index_variable_identifier ] { , [ index_variable_identifier ] }
    """
    grammar = optional(name()), maybe_some(",", optional(name()))

class ConstraintSet(str):
    """
    constraint_set ::= constraint_expression | { { constraint_expression } }
    """
    pass # grammar is defined after constraint expression is defined
class NormalConstraint(str):
    """
    NormalConstraint ::= expression_or_dist ;
    we don't handle dist (weighted constraints).
    """
    grammar = attr("normal_con", Expression), ";"
class ImplyConstraint(str):
    """
    ImplyConstraint ::= expression -> constraint_set
    """
    grammar = Expression, "->", ConstraintSet
class IfConstraint(str):
    """
    IfConstraint ::= if ( expression ) constraint_set [ else constraint_set ]
    """
    grammar = K("if"), "(", Expression, ")", ConstraintSet, optional(K("else"), ConstraintSet)
class ArrayConstraint(str):
    """
    ArrayConstraint ::= foreach ( array_identifier [ loop_variables ] ) constraint_set
    """
    grammar = K("foreach"), "(", name(), "[", LoopVariables, "]", ")", ConstraintSet
class ConstraintExpression(str):
    """
    constraint_expression ::= NormalConstraint
                        | ImplyConstraint
                        | IfConstraint
                        | ArrayConstraint
    """
    grammar = attr("con_exp_type", [NormalConstraint, ImplyConstraint, IfConstraint, ArrayConstraint])

ConstraintSet.grammar = [ConstraintExpression, ("{", maybe_some(ConstraintExpression), "}")]

class ConstraintBlockItem(str):
    """
    we don't handle (solve identifier before another identifier)
    """
    grammar = attr("con_exp", ConstraintExpression)
class ConstraintBlock(List):
    """
    """
    grammar = "{", maybe_some(ConstraintBlockItem), "}"
class ConstraintDeclaration(str):
    """
    constraint_declaration ::= [ static ] constraint constraint_identifier constraint_block
    """
    grammar = optional(K("static")), K("constraint"), name(), attr("con_block", ConstraintBlock)


class ConstraintPrototype(str):
    """
    constraint_prototype ::= [ static ] constraint constraint_identifier ;
    """
    grammar = optional(K("static")), K("constraint"), name(), ";"
class ClassConstraint(str):
    """
    class_constraint ::= constraint_prototype | constraint_declaration
    """
    grammar = attr("class_con_type", [ConstraintPrototype, ConstraintDeclaration])

class ClassItem(str):
    """
    class_item ::= { attribute_instance } class_property
             | { attribute_instance } class_method
             | { attribute_instance } class_constraint
             | { attribute_instance } class_declaration
             | { attribute_instance } timeunits_declaration
             | { attribute_instance } covergroup_declaration
             | ;
    """
    grammar = attr("item", [ClassProperty, ClassConstraint, ";"])


class ClassDeclaration(List):
    """
    class_declaration ::= [ virtual ] class [ lifetime ] class_identifier [ parameter_port_list ] [ extends class_type [ ( list_of_arguments ) ] ];
                        { class_item }
                      endclass [ : class_identifier]
    we don't accept virtual classes .
    we don't accept classes that takes list of arguments .
    """
    grammar = K("class"), name(), ";", maybe_some(ClassItem), K("endclass")





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
    VAR_NUMBER = {}
    VAR_SIZES = []
    VAR_SIGNING = []
    INITIAL_VALUES = []
    for class_item in class_declaration_object:


        if isinstance(class_item.item, ClassConstraint) : # class constrinat,not class property
            continue
        data_declaration_object = class_item.item.data_declaration

        parse_data_declaration(data_declaration_object, VAR_NUMBER, VAR_SIZES,
                               VAR_SIGNING, INITIAL_VALUES)
    return VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES


def parse_constraints(class_declaration_object):
    """
    use parse_constraints() to parse each constraint in the class declaration.
    """
    list_of_coeffs = []
    for class_item in class_declaration_object:

        if isinstance(class_item.item, ClassConstraint):  # class constrinat,not class property
            if isinstance(class_item.item.class_con_type, ConstraintDeclaration): # not prototype
                constraint_block = class_item.item.class_con_type.con_block
                for constraint_block_item in constraint_block:
                    constraint_expression = constraint_block_item.con_exp
                    if isinstance(constraint_expression.con_exp_type, NormalConstraint):
                        normal_constraint = constraint_expression.con_exp_type
                        expression = normal_constraint.normal_con
                        if isinstance(expression.exp_type, IntConExpression): # integer constraints
                            int_con_expression_object = expression.exp_type
                            coeffs = parse_int_con_expression(int_con_expression_object)
                            list_of_coeffs.append(coeffs)
    return list_of_coeffs


    return coeffs
# input sv file reading
INPUT_FILE_PATH = "code.txt"
with open(INPUT_FILE_PATH, "r") as input_file:
    SOURCE_CODE = input_file.read().replace("\n", "").strip(" ")
input_file.close()
C = parse(SOURCE_CODE, ClassDeclaration)
VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES = parse_data_declarations(C)
print(VAR_NUMBER, VAR_SIZES, VAR_SIGNING, INITIAL_VALUES)
LIST_OF_COEFFS = parse_constraints(C)
print(LIST_OF_COEFFS)