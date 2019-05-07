from pypeg2 import *



UNSIGNED_DIGITS = re.compile(r"\d+")
OPTIONAL_SIGN = re.compile(r"[-+]?")
BASE = re.compile(r"'b|'B|'d|'D|'o|'O|'h|'H")
BINARYOPERATOR = re.compile(r"\+|-|\*|/|%|==|!=|&&|\|\||\*\*|<=|>=|<|>")
EQUALITY_OPERATOR = re.compile(r"==|!=")
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
    grammar = Enum(K("byte"), K("shortint"), K("int"), K("longint"),
                   K("integer"), K("time"))


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
    grammar = attr("sign",
                   OPTIONAL_SIGN), attr("value", UNSIGNED_DIGITS), attr(
                       "base", None), attr("width", None)


class BaseOnlyNumber(str):
    """
    base only numbers like 'b0 or 'hA
    """
    grammar = attr("sign", OPTIONAL_SIGN), attr("base", BASE), attr(
        "width", None), attr("value",
                             word)  # value may be hex (contains alphapetic)


class WidthBaseNumber(str):
    """
    numbers like 5'd2 or -7'd1
    """
    grammar = attr(
        "sign", OPTIONAL_SIGN), attr("width", UNSIGNED_DIGITS), attr(
            "base", BASE), attr("value",
                                word)  # value may be hex (contains alphapetic)


class Number(str):
    """
    numbers in verilog and SystemVerilog : 7'd5 ,5, -7'h4
    """
    grammar = attr("number", [WidthBaseNumber, BaseOnlyNumber, DefaultNumber])



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
        "signing", optional(Signing)), attr("packed_dimensions",
                                            maybe_some(PackedDimension))


class AtomDataType(str):
    """
    like int
    """
    grammar = attr("integer_type",
                   IntegerAtomType), attr("signing", optional(Signing))


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


class Primary(str):
    """
    """
    grammar = attr("primary_type", [Number, name()])


class CompositeTerm(List):
    """
    """
    grammar = Primary, "*", Primary


class IdentifierOnly(str):
    """
    """
    grammar = OPTIONAL_SIGN, name()


class Term(List):
    """
    """
    grammar = attr("term_type", [CompositeTerm, Number, IdentifierOnly])


class IntConExpression(str):
    """
    x+5<0
    """
    grammar = attr("lhs", some(Term)), attr("con_op", CON_OPERATOR), attr("rhs", some(Term))


class RangeExpression(str):
    """
    [ expression : expression ]
    """
    grammar = "[", attr("from_num", Number), ":", attr("to_num", Number), "]"


class ValueRange(str):
    """
    primary | range_expression
    """
    grammar = attr("value_range_type", [Number, RangeExpression])


class OpenValueRange(str):
    """
    """
    grammar = attr("value_range", ValueRange)


class OpenRangeList(List):
    """
    """
    grammar = OpenValueRange, maybe_some(",", OpenValueRange)


class InsideExpression(str):
    """
    inside_expression ::= expression inside { open_range_list }
    """
    grammar = name(), K("inside"), "{", attr("open_range_list", OpenRangeList), "}"


class Expression(str):
    """
    like 20 or x+5<y
    """
    grammar = attr("exp_type", [InsideExpression, IntConExpression, Primary])


class VariableDeclAssignment(str):
    """
    like x=5 or x  or x[10] or x[0:10]
    we don't handle dynamic arrays.
    we don't handle class instantiation.
    we accept only one variable dimension.
    """
    grammar = name(), attr("dimension", maybe_some(VariableDimension)), attr(
        "initial_value", optional("=", Number))


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
    grammar = attr("data_type",
                   DataType), attr("list_of_variable_decl_assignment",
                                   ListOfVariableDeclAssignments), ";"


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
    grammar = maybe_some(PropertyQualifier), attr("data_declaration",
                                                  DataDeclaration)


class LoopVariables(str):
    """
    loop_variables ::= [ index_variable_identifier ] { , [ index_variable_identifier ] }
    """
    grammar = optional(name()), maybe_some(",", optional(name()))


class ConstraintSet(List):
    """
    constraint_set ::= constraint_expression | { { constraint_expression } }
    """
    pass  # grammar is defined after constraint expression is defined


class NormalConstraint(str):
    """
    NormalConstraint ::= expression_or_dist ;
    we don't handle dist (weighted constraints).
    """
    grammar = attr("normal_con", Expression), ";"

class EqualityExpression(List):
    """
    """
    grammar = name(), EQUALITY_OPERATOR, Number



class ImplyConstraint(str):
    """
    ImplyConstraint ::= expression -> constraint_set
    we support only equality / non-equality expressions on the LHS of implication.
    like : op == 2 -> x+y<128; // op is of 2-bit size , so it's mapped to 2 boolean variables.
    """
    # grammar = EqualityExpression, "->", ConstraintSet
    pass




class IfConstraint(str):
    """
    IfConstraint ::= if ( expression ) constraint_set [ else constraint_set ]
    """
    grammar = K("if"), "(", attr("equality_exp", EqualityExpression), ")", attr("con_set", ConstraintSet), optional(
        K("else"), ConstraintSet)


class ArrayConstraint(str):
    """
    ArrayConstraint ::= foreach ( array_identifier [ loop_variables ] ) constraint_set
    """
    grammar = K(
        "foreach"), "(", name(), "[", LoopVariables, "]", ")", ConstraintSet


class ConstraintExpression(str):
    """
    constraint_expression ::= NormalConstraint
                        | ImplyConstraint
                        | IfConstraint
                        | ArrayConstraint
    """
    grammar = attr(
        "con_exp_type",
        [NormalConstraint, ImplyConstraint, IfConstraint, ArrayConstraint])


ConstraintSet.grammar = attr("con_set_type", [
    ConstraintExpression, ("{", maybe_some(ConstraintExpression), "}")
])

ImplyConstraint.grammar = attr("equality_exp", EqualityExpression), "->", attr("con_set", ConstraintSet)



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
    grammar = optional(K("static")), K("constraint"), name(), attr(
        "con_block", ConstraintBlock)


class ConstraintPrototype(str):
    """
    constraint_prototype ::= [ static ] constraint constraint_identifier ;
    """
    grammar = optional(K("static")), K("constraint"), name(), ";"


class ClassConstraint(str):
    """
    class_constraint ::= constraint_prototype | constraint_declaration
    """
    grammar = attr("class_con_type",
                   [ConstraintPrototype, ConstraintDeclaration])


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
