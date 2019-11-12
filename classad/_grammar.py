import pyparsing as pp

pp.ParserElement.enablePackrat()

SQUOTE = pp.Suppress("'")
DQUOTE = pp.Suppress('"')
LPAR = pp.Suppress("(")
RPAR = pp.Suppress(")")
LBRACKET = pp.Suppress("[")
RBRACKET = pp.Suppress("]")
LBRACE = pp.Suppress("{")
RBRACE = pp.Suppress("}")

# Operators
binary_operator = pp.oneOf("\\\\ && | ^ & == != is isnt < > <= >= << >> >>> + - * / %")(
    "operator*"
)
unary_operator = pp.Word("+-~!", max=1)("unary_operator*").setName("unary_operator")
operator = binary_operator | unary_operator

# Reserved Words
boolean_literal = pp.oneOf("true false", caseless=True, asKeyword=True)("boolean*")
error_literal = pp.CaselessKeyword("error")("error*")
undefined_literal = pp.CaselessKeyword("undefined")("undefined*")
parent_literal = pp.CaselessKeyword("parent")("parent*")

# Tokens
octal_digit = pp.srange("[0-7]")
nonzero_digit = pp.srange("[1-9]")
decimal_digit = pp.nums
reserved_word = (
    error_literal
    | boolean_literal
    | pp.CaselessKeyword("isnt")
    | pp.CaselessKeyword("is")
    | parent_literal
    | undefined_literal
).setName("reserved_word")
punctuation = pp.oneOf("= ( ) { } [ ] , ;").setName("punctuation")
integer_literal = (
    "0"
    | pp.Word(nonzero_digit, decimal_digit)
    | pp.Combine("0" + pp.Word(octal_digit))
    | pp.Combine("0" + pp.Word(pp.srange("[xX]"), pp.hexnums))
)("integer*")
exponent = pp.Combine(
    pp.CaselessLiteral("e") + pp.Optional(pp.oneOf("+ -")) + pp.Word(pp.nums)
)
floating_point_literal = (
    pp.Combine(pp.Word(pp.nums) + "." + pp.Word(pp.nums) + pp.Optional(exponent))
    | pp.Combine("." + pp.Word(pp.nums) + pp.Optional(exponent))
    | pp.Combine(pp.Word(pp.nums) + exponent)
).setResultsName("float*")
escaped_char = pp.Word("NnTtBbRrFf\\\"'", max=1)
non_quote = (
    "\\" + escaped_char
    | "\\" + pp.Word(octal_digit, min=1, max=2)
    | "\\" + pp.Word(pp.srange("[0-3]"), max=1) + pp.Word(octal_digit, min=2, max=2)
    | pp.Word(pp.printables, excludeChars="\"'\\\n\r0")
)
unquoted_name = pp.Word(pp.alphas + "_", pp.alphanums + "_")
quoted_name = (SQUOTE + pp.OneOrMore(non_quote | '"') + SQUOTE).setName("quoted_name")
string_literal = (DQUOTE + pp.ZeroOrMore(non_quote | "'") + DQUOTE)("string*").setName(
    "string_literal"
)
literal = (integer_literal | floating_point_literal | string_literal).setName("literal")
attribute_name = (unquoted_name | quoted_name)("attribute_name*").setName(
    "attribute_name"
)

# Expression grammar
expression = pp.Forward()
suffix_expression = pp.Forward()
binary_expression = pp.Forward()

list_expression = (
    LBRACE + pp.Group(pp.Optional(pp.delimitedList(expression)))("list*") + RBRACE
).setName("list_expression")
attribute_definition = (pp.Group(attribute_name + "=" + expression))(
    "attribute*"
).setName("attribute_definition")
record_expression = (
    LBRACKET
    + pp.Group(pp.Optional(pp.delimitedList(attribute_definition, delim=";")))(
        "record*"
    )
    + RBRACKET
).setName("record_expression")
function_call = (
    unquoted_name + LPAR + pp.Group(pp.Optional(pp.delimitedList(expression))) + RPAR
)("function*").setName("function_call")
atom = (
    boolean_literal
    | error_literal
    | undefined_literal
    | parent_literal
    | literal
    | function_call
    | attribute_name
    | list_expression
    | record_expression
    | LPAR + expression + RPAR
).setName("atom")
subscriptable = (  # introduced to remove recursion in suffix_expression
    error_literal
    | undefined_literal
    | parent_literal
    | function_call
    | attribute_name
    | list_expression
    | record_expression
    | LPAR + expression + RPAR
).setName("subscriptable")
suffix_expression << (
    subscriptable + "." + attribute_name
    | subscriptable + LBRACKET + expression + RBRACKET
    | atom
).setName("suffix_expression")
prefix_expression = (pp.Optional(unary_operator) + suffix_expression).setName(
    "prefix_expression"
)
binary_expression << (
    prefix_expression + binary_operator + binary_expression | prefix_expression
).setName("binary_expression")
expression << (
    pp.Group(binary_expression)("if")
    + pp.Suppress("?")
    + pp.Group(expression)("then")
    + pp.Suppress(":")
    + pp.Group(expression)("else")
    | binary_expression
).setName("expression")
