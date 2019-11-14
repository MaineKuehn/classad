import pyparsing as pp

from classad._classad import ClassAd
from classad._expression import Expression, AttributeExpression, FunctionExpression, \
    ArithmeticExpression
from classad._primitives import Error, Undefined

pp.ParserElement.enablePackrat()

SQUOTE = pp.Suppress("'")
DQUOTE = pp.Suppress('"')
LPAR = pp.Suppress("(")
RPAR = pp.Suppress(")")
LBRACKET = pp.Suppress("[")
RBRACKET = pp.Suppress("]")
LBRACE = pp.Suppress("{")
RBRACE = pp.Suppress("}")

# Reserved Words
boolean_literal = pp.oneOf("true false", caseless=True, asKeyword=True).setParseAction(
    lambda s, l, t: t[0] in ["true"])
error_literal = pp.CaselessKeyword("error").setParseAction(
    lambda: Error())
undefined_literal = pp.CaselessKeyword("undefined").setParseAction(
    lambda: Undefined())
parent_literal = pp.CaselessKeyword("parent")
target_literal = pp.CaselessKeyword("target")

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
).setParseAction(lambda s, l, t: int(t[0]))("integer*")
exponent = pp.Combine(
    pp.CaselessLiteral("e") + pp.Optional(pp.oneOf("+ -")) + pp.Word(pp.nums)
)
floating_point_literal = (
    pp.Combine(pp.Word(pp.nums) + "." + pp.Word(pp.nums) + pp.Optional(exponent))
    | pp.Combine("." + pp.Word(pp.nums) + pp.Optional(exponent))
    | pp.Combine(pp.Word(pp.nums) + exponent)
).setParseAction(lambda s, l, t: float(t[0])).setResultsName("float*")
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
literal = (floating_point_literal | integer_literal | string_literal).setName("literal")
attribute_name = (unquoted_name | quoted_name)("attribute_name*").setParseAction(
    lambda s, l, t: AttributeExpression.from_grammar(t[0])).setName(
    "attribute_name"
)

# Expression grammar
expression = pp.Forward()
suffix_expression = pp.Forward()
arithmetic_expression = pp.Forward()

list_expression = pp.Group(
    LBRACE + pp.Optional(pp.delimitedList(expression)) + RBRACE
).setParseAction(lambda s, l, t: tuple(t[0])).setName("list_expression")
attribute_definition = (pp.Group(attribute_name + pp.Suppress("=") + expression))(
    "attribute*"
).setName("attribute_definition")
record_expression = (
    LBRACKET
    + pp.Group(pp.Optional(pp.delimitedList(attribute_definition, delim=";")))(
        "record*"
    )
    + RBRACKET
    | pp.Group(pp.delimitedList(attribute_definition, delim=pp.Empty()))
).setParseAction(
    lambda s, l, t: ClassAd.from_grammar(t[0])).setName("record_expression")
function_call = (
    unquoted_name + LPAR + pp.Group(pp.Optional(pp.delimitedList(expression))) + RPAR
)("function*").setParseAction(
    lambda s, l, t: FunctionExpression.from_grammar(t)).setName("function_call")
atom = (
    LPAR + expression + RPAR
    | list_expression
    | boolean_literal
    | error_literal
    | undefined_literal
    | parent_literal
    | function_call
    | record_expression
    | literal
    | attribute_name
).setName("atom")
subscriptable = (  # introduced to remove recursion in suffix_expression
    list_expression
    | error_literal
    | undefined_literal
    | parent_literal
    | target_literal
    | function_call
    | attribute_name
    | record_expression
    | LPAR + expression + RPAR
).setName("subscriptable")
suffix_expression << (
    pp.Group(subscriptable + pp.Suppress(".") + attribute_name).setParseAction(
        lambda s, l, t: AttributeExpression.from_grammar(t[0]))
    | subscriptable + LBRACKET + expression + RBRACKET
    | atom
).setName("suffix_expression")


def binary_parse_action(s, l, t):
    return ArithmeticExpression.from_grammar(t[0])


# unary operators: + - ~ !
# binary operators: \\ && | ^ & == != is isnt < > <= >= << >> >>> + - * / %
arithmetic_expression << pp.infixNotation(suffix_expression, [
    ("-", 1, pp.opAssoc.RIGHT),
    (pp.oneOf("* /"), 2, pp.opAssoc.LEFT, binary_parse_action),
    (pp.oneOf("+ -"), 2, pp.opAssoc.LEFT, binary_parse_action),
    (pp.oneOf("< <= >= >"), 2, pp.opAssoc.LEFT, binary_parse_action),
    (pp.oneOf("== != =?= is =!= isnt"), 2, pp.opAssoc.LEFT, binary_parse_action),
    ("&&", 2, pp.opAssoc.LEFT, binary_parse_action),
    ("||", 2, pp.opAssoc.LEFT, binary_parse_action)
])

expression << pp.Group(
    pp.Group(arithmetic_expression)("if")
    + pp.Suppress("?")
    + pp.Group(expression)("then")
    + pp.Suppress(":")
    + pp.Group(expression)("else")
    | arithmetic_expression
).setParseAction(lambda s, l, t: Expression.from_grammar(t[0])).setName("expression")
