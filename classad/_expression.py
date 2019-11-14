import operator
import pyparsing as pp
from typing import Any

from classad._classad import ClassAd


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


class FunctionExpression(Expression):
    pass


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
        ">": operator.gt
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
