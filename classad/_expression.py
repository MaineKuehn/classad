import operator
import pyparsing as pp
from typing import Any

from . import _functions
from ._classad import ClassAd


def evaluate_isnt_operator(a, b):
    return a.__isnt__(b)


def evaluate_is_operator(a, b):
    return a.__is__(b)


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
        return type(self) == type(other) and self._expression == other._expression


class FunctionExpression(Expression):
    def __init__(self, name, args):
        super().__init__()
        self._name = name
        self._expression = args

    def __eq__(self, other):
        return (
            type(self) == type(other)
            and self._expression == other._expression
            and self._name == other._name
        )

    def evaluate(self, my: ClassAd, target: ClassAd) -> Any:
        expression = []
        for element in self._expression:
            if isinstance(element, Expression):
                expression.append(element.evaluate(my, target))
            else:
                expression.append(element)
        return getattr(_functions, self._name)(*expression)

    @classmethod
    def from_grammar(cls, tokens):
        return cls(tokens[0], tokens[1])

    def __repr__(self):
        return f"<{self.__class__.__name__}>: {self._name}{self._expression}"


class TernaryExpression(Expression):
    @classmethod
    def from_grammar(cls, tokens):
        if tokens[0]:
            return tokens[1]
        else:
            return tokens[2]


class SubscriptableExpression(Expression):
    @classmethod
    def from_grammar(cls, tokens):
        if len(tokens) == 2:
            return tokens[0][tokens[1]]
        return NotImplemented


class AttributeExpression(Expression):
    def __add__(self, other):
        raise ArithmeticError

    def __sub__(self, other):
        raise ArithmeticError

    def __mul__(self, other):
        raise ArithmeticError

    def __truediv__(self, other):
        raise ArithmeticError

    def __lt__(self, other):
        raise TypeError

    def __le__(self, other):
        raise TypeError

    def __ge__(self, other):
        raise TypeError

    def __gt__(self, other):
        raise TypeError

    def __eq__(self, other):
        if type(self) == type(other):
            if self._expression == other._expression:
                return True
            return False
        raise TypeError

    def __ne__(self, other):
        raise TypeError

    def __and__(self, other):
        raise ArithmeticError

    def __or__(self, other):
        raise ArithmeticError

    def __isnt__(self, other):
        raise TypeError

    def __is__(self, other):
        raise TypeError


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
        "!=": operator.ne,
        "&&": operator.and_,
        "||": operator.or_,
        "=!=": evaluate_isnt_operator,
        "isnt": evaluate_isnt_operator,
        "=?=": evaluate_is_operator,
        "is": evaluate_is_operator,
    }

    @classmethod
    def from_grammar(cls, tokens):
        result = cls()
        try:
            return cls.operator_map[tokens[1]](tokens[0], tokens[-1])
        except (TypeError, AttributeError):
            # TODO: lazy loading required
            if len(tokens) > 1:
                result._expression = tuple(tokens)
            else:
                result._expression = tokens[0]
        return result

    def __eq__(self, other):
        if type(self) == type(other):
            # check operators
            return all(
                (
                    self._expression[0] == other._expression[0],
                    self.operator_map[self._expression[1]]
                    == self.operator_map[other._expression[1]],
                    self._expression[2] == other._expression[2],
                )
            )
        return False
