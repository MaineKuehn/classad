import pyparsing as pp

from classad._base_expression import Expression
from classad._expression import (
    ClassAd,
    AttributeExpression,
    FunctionExpression,
    ArithmeticExpression,
    SubscriptableExpression,
    TernaryExpression,
    NamedExpression,
    UnaryExpression,
)
from classad._primitives import (
    Error,
    Undefined,
    HTCBool,
    HTCInt,
    HTCFloat,
    HTCStr,
    HTCList,
)

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
    lambda s, l, t: HTCBool(1) if t[0] in ["true"] else HTCBool(0)
)
error_literal = pp.CaselessKeyword("error").setParseAction(lambda: Error())
undefined_literal = pp.CaselessKeyword("undefined").setParseAction(lambda: Undefined())
parent_literal = pp.CaselessKeyword("parent").setParseAction(
    lambda s, l, t: NamedExpression.from_grammar(t[0])
)
target_literal = pp.CaselessKeyword("target").setParseAction(
    lambda s, l, t: NamedExpression.from_grammar(t[0])
)
super_literal = pp.CaselessKeyword("super").setParseAction(
    lambda s, l, t: NamedExpression.from_grammar(t[0])
)

# Tokens
octal_digit = pp.srange("[0-7]")
nonzero_digit = pp.srange("[1-9]")
decimal_digit = pp.nums
reserved_word = pp.MatchFirst(
    (
        error_literal,
        boolean_literal,
        pp.CaselessKeyword("isnt"),
        pp.CaselessKeyword("is"),
        parent_literal,
        undefined_literal,
        super_literal,
    )
).setName("reserved_word")
integer_literal = pp.MatchFirst(
    (
        "0",
        pp.Word(nonzero_digit, decimal_digit),
        pp.Combine("0" + pp.Word(octal_digit)),
        pp.Combine("0" + pp.Word(pp.srange("[xX]"), pp.hexnums)),
    )
).setParseAction(lambda s, l, t: HTCInt(t[0]))("integer*")
exponent = pp.Combine(
    pp.CaselessLiteral("e") + pp.Optional(pp.oneOf("+ -")) + pp.Word(pp.nums)
)
floating_point_literal = (
    pp.MatchFirst(
        (
            pp.Combine(
                pp.Word(pp.nums) + "." + pp.Word(pp.nums) + pp.Optional(exponent)
            ),
            pp.Combine("." + pp.Word(pp.nums) + pp.Optional(exponent)),
            pp.Combine(pp.Word(pp.nums) + exponent),
        )
    )
    .setParseAction(lambda s, l, t: HTCFloat(t[0]))
    .setResultsName("float*")
)
escaped_char = pp.Word("NnTtBbRrFf\\\"'", max=1)
non_quote = pp.MatchFirst(
    (
        pp.Combine("\\" + escaped_char),
        pp.Combine("\\" + pp.Word(octal_digit, min=1, max=2)),
        pp.Combine(
            "\\"
            + pp.Word(pp.srange("[0-3]"), max=1)
            + pp.Word(octal_digit, min=2, max=2)
        ),
        pp.Word(pp.printables, " ", excludeChars="\"'\\\n\r0"),
    )
)
unquoted_name = pp.Word(pp.alphas + "_", pp.alphanums + "_")
quoted_name = pp.Combine((SQUOTE + pp.OneOrMore(non_quote | '"') + SQUOTE)).setName(
    "quoted_name"
)
string_literal = (
    pp.Combine(DQUOTE + pp.ZeroOrMore(non_quote | "'") + DQUOTE)("string*")
    .setParseAction(lambda s, l, t: HTCStr(t[0]))
    .setName("string_literal")
)
literal = pp.MatchFirst(
    (floating_point_literal, integer_literal, string_literal)
).setName("literal")
attribute_name = (
    (unquoted_name | quoted_name)("attribute_name*")
    .setParseAction(lambda s, l, t: AttributeExpression.from_grammar(t[0]))
    .setName("attribute_name")
)

# Expression grammar
expression = pp.Forward()
suffix_expression = pp.Forward()
arithmetic_expression = pp.Forward()

list_expression = (
    pp.Group(LBRACE + pp.Optional(pp.delimitedList(expression)) + RBRACE)
    .setParseAction(lambda s, l, t: HTCList(t[0]))
    .setName("list_expression")
)
attribute_definition = (pp.Group(attribute_name + pp.Suppress("=") + expression))(
    "attribute*"
).setName("attribute_definition")
record_expression = (
    pp.MatchFirst(
        (
            LBRACKET
            + pp.Group(
                pp.Optional(
                    pp.delimitedList(attribute_definition, delim=";")
                    + pp.Optional(pp.Suppress(";"))
                )
            )("record*")
            + RBRACKET,
            pp.Group(pp.delimitedList(attribute_definition, delim=pp.Empty())),
        )
    )
    .setParseAction(lambda s, l, t: ClassAd.from_grammar(t[0]))
    .setName("record_expression")
)
function_call = (
    (
        pp.Combine(unquoted_name + LPAR)
        + pp.Group(pp.Optional(pp.delimitedList(expression))).setParseAction(
            lambda s, l, t: tuple(t[0])
        )
        + RPAR
    )("function*")
    .setParseAction(lambda s, l, t: FunctionExpression.from_grammar(t))
    .setName("function_call")
)
atom = pp.MatchFirst(
    (
        list_expression,
        boolean_literal,
        error_literal,
        undefined_literal,
        parent_literal,
        super_literal,
        function_call,
        record_expression,
        literal,
        attribute_name,
        LPAR + expression + RPAR,
    )
).setName("atom")
subscriptable = pp.MatchFirst(
    (  # introduced to remove recursion in suffix_expression
        list_expression,
        error_literal,
        undefined_literal,
        parent_literal,
        super_literal,
        target_literal,
        function_call,
        attribute_name,
        record_expression,
        LPAR + expression + RPAR,
    )
).setName("subscriptable")
suffix_expression << pp.MatchFirst(
    (
        pp.Group(
            "."
            + pp.delimitedList(attribute_name, ".").setParseAction(
                lambda s, l, t: AttributeExpression.from_grammar(t)
            )
        ).setParseAction(lambda s, l, t: AttributeExpression.from_grammar(t[0])),
        pp.Group(
            subscriptable
            + pp.Suppress(".")
            + pp.delimitedList(attribute_name, ".").setParseAction(
                lambda s, l, t: AttributeExpression.from_grammar(t)
            )
        ).setParseAction(lambda s, l, t: AttributeExpression.from_grammar(t[0])),
        pp.Group(subscriptable + LBRACKET + expression + RBRACKET).setParseAction(
            lambda s, l, t: SubscriptableExpression.from_grammar(t[0])
        ),
        atom,
    )
).setName("suffix_expression")


def binary_parse_action(s, l, t):
    return ArithmeticExpression.from_grammar(t[0])


def unary_parse_action(s, l, t):
    return UnaryExpression.from_grammar(t[0])


# unary operators: + - ~ !
# binary operators: \\ && | ^ & == != is isnt < > <= >= << >> >>> + - * / %
arithmetic_expression << pp.infixNotation(
    suffix_expression,
    [
        (pp.oneOf("- !"), 1, pp.opAssoc.RIGHT, unary_parse_action),
        (pp.oneOf("* /"), 2, pp.opAssoc.LEFT, binary_parse_action),
        (pp.oneOf("+ -"), 2, pp.opAssoc.LEFT, binary_parse_action),
        (pp.oneOf("< <= >= >"), 2, pp.opAssoc.LEFT, binary_parse_action),
        (pp.oneOf("== != =?= is =!= isnt"), 2, pp.opAssoc.LEFT, binary_parse_action),
        ("&&", 2, pp.opAssoc.LEFT, binary_parse_action),
        ("||", 2, pp.opAssoc.LEFT, binary_parse_action),
    ],
)

expression << pp.Group(
    pp.MatchFirst(
        (
            (
                pp.Group(arithmetic_expression)("if")
                + pp.Suppress("?")
                + pp.Optional(expression, default=None)("then")
                + pp.Suppress(":")
                + pp.Group(expression)("else")
            ).setParseAction(lambda s, l, t: TernaryExpression.from_grammar(t)),
            arithmetic_expression,
        )
    )
).setParseAction(lambda s, l, t: Expression.from_grammar(t[0])).setName("expression")


def parse(content: str):
    try:
        result = expression.parseString(content, parseAll=True)
    except pp.ParseException:
        raise
    return result[0]
