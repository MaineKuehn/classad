import operator
import pyparsing as pp
from typing import Any

from . import _functions
from ._classad import ClassAd


def evaluate_isnt_operator(a, b):
    if type(a) == type(b) and a == b:
        return False
    return True


class Expression:
    def __init__(self):
        self._expression = None

    def evaluate(self, my: ClassAd, target: ClassAd) -> Any:
        return NotImplemented

    @classmethod
    def from_grammar(cls, tokens):
        if isinstance(tokens, pp.ParseResults):
            if len(tokens) == 1:
                return tokens[0]
        result = cls()
        result._expression = tokens
        return result

    def __repr__(self):
        return f"<{self.__class__.__name__}>: {self._expression}"

    def __eq__(self, other):
        raise TypeError


class FunctionExpression(Expression):
    def __init__(self, name, args):
        super().__init__()
        self._name = name
        self._expression = args

    def evaluate(self, my: ClassAd, target: ClassAd) -> Any:
        print(f"{self._name}: {self._expression}")
        expression = []
        for element in self._expression:
            if isinstance(element, Expression):
                expression.append(element.evaluate(my, target))
            else:
                expression.append(element)
        print(f"calling with {expression}")
        return getattr(_functions, self._name)(*expression)

    @classmethod
    def from_grammar(cls, tokens):
        print(f"received {tokens}, {tokens[1]} ({type(tokens[1])})")
        return cls(tokens[0], tokens[1])

    def __repr__(self):
        return f"<{self.__class__.__name__}>: {self._name}{self._expression}"


class AttributeExpression(Expression):
    pass


class ArithmeticExpression(Expression):
    operator_map = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "<": operator.lt,
        "<=": operator.le,
        "=>": operator.ge,
        ">": operator.gt,
        "==": operator.eq,
        "&&": operator.and_,
        "||": operator.or_,
        "=!=": evaluate_isnt_operator,
        "isnt": evaluate_isnt_operator
    }

    @classmethod
    def from_grammar(cls, tokens):
        result = cls()
        try:
            return cls.operator_map[tokens[1]](tokens[0], tokens[-1])
        except TypeError:
            # TODO: lazy loading required
            if len(tokens) > 1:
                result._expression = tuple(tokens)
            else:
                result._expression = tokens[0]
        return result
