import operator
from collections import MutableMapping, OrderedDict

import pyparsing as pp
from typing import Any, Iterable, List, Iterator

from classad._primitives import Error, Undefined
from ._base_expression import Expression
from . import _functions


def scope_up(key: List[str]):
    return key[:-1]


def evaluate_isnt_operator(a, b):
    result = a.__htc_isnt__(b)
    if result == NotImplemented:
        result = b.__htc_isnt__(a)
    return result


def evaluate_is_operator(a, b):
    result = a.__htc_is__(b)
    if result == NotImplemented:
        result = b.__htc_is__(a)
    return result


def evaluate_eq_operator(a, b):
    result = a.__htc_eq__(b)
    if result == NotImplemented:
        result = b.__htc_eq__(a)
    return result


def evaluate_ne_operator(a, b):
    result = a.__htc_ne__(b)
    if result == NotImplemented:
        result = b.__htc_ne__(a)
    return result


def evaluate_not_operator(a):
    return a.__htc_not__()


class ClassAd(Expression, MutableMapping):
    __slots__ = "_data"

    def __add__(self, other):
        return Error()

    __sub__ = __rsub__ = __radd__ = __add__

    def __init__(self):
        super().__init__()
        self._data = OrderedDict()

    def __setitem__(self, key: str, value: Expression) -> None:
        """
        Keynames that are reserved and, therefore, cannot be used: error, false, is,
            isnt, parent, true, undefined
        """
        try:
            key = key.casefold()
        except AttributeError:
            key = key._expression.casefold()
        if key in ["error", "false", "is", "isnt", "parent", "true", "undefined"]:
            raise ValueError(f"{key} is a reserved name")
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        self._data.pop(key, None)

    def __getitem__(self, key: Iterable) -> Expression:
        if isinstance(key, str):
            key = [key]
        expression = self._data
        for token in key:
            token = token.casefold()
            try:
                expression = expression[token]
            except KeyError:
                return Undefined()
        return expression

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def _evaluate(
        self, key: Iterable = None, my: "ClassAd" = None, target: "ClassAd" = None
    ) -> Any:
        """
        Perform a matchmaking between an expression defined by the named attribute
        key in the context of the target ClassAd.
        """
        expression = self[key]
        new_key = key[:-1]
        return expression._evaluate(key=new_key, my=self, target=target)

    @classmethod
    def from_grammar(cls, tokens):
        result = cls()
        for token in tokens:
            result[token[0]] = token[1]
        return result

    def __eq__(self, other):
        if type(self) == type(other):
            return self._data == other._data
        return False

    def __repr__(self):
        return f"<{self.__class__.__name__}>: {self._data}"


class NamedExpression(Expression):
    @classmethod
    def from_grammar(cls, tokens):
        if "super" == tokens:
            raise NotImplementedError("Super is not supported")
        result = cls()
        result._expression = tokens
        return result


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

    def _evaluate(
        self, key: Iterable = None, my: "ClassAd" = None, target: "ClassAd" = None
    ) -> Any:
        expression = []
        for element in self._expression:
            expression.append(element._evaluate(key=key, my=my, target=target))
        return getattr(_functions, self._name)(*expression)

    @classmethod
    def from_grammar(cls, tokens):
        return cls(tokens[0], tokens[1])

    def __repr__(self):
        return f"<{self.__class__.__name__}>: {self._name}{self._expression}"


class TernaryExpression(Expression):
    def _evaluate(
        self, key: Iterable = None, my: "ClassAd" = None, target: "ClassAd" = None
    ) -> Any:
        if self._expression[0]:
            return self._expression[1]._evaluate(key=key, my=my, target=target)
        else:
            return self._expression[2]._evaluate(key=key, my=my, target=target)


class DotExpression(Expression):
    def _evaluate(
        self, key: Iterable = None, my: "ClassAd" = None, target: "ClassAd" = None
    ) -> Any:
        scope = self._expression[0]
        checked = set()
        to_check = self._expression[1]
        while isinstance(to_check, AttributeExpression):
            if to_check._expression not in checked:
                checked.add(to_check._expression)
                result = scope[to_check._expression]
                if not isinstance(result, Undefined):
                    to_check = result
                else:
                    try:
                        new_scope = my[key]
                    except TypeError:
                        return Undefined()
                    if new_scope != scope:
                        checked.remove(to_check._expression)
                        scope = new_scope
                    else:
                        return Undefined()
            else:
                return Undefined()
        return to_check


class SubscriptableExpression(Expression):
    def _evaluate(
        self, key: Iterable = None, my: "ClassAd" = None, target: "ClassAd" = None
    ) -> Any:
        if len(self._expression) == 2:
            return self._expression[0][self._expression[1]]._evaluate(
                key=key, my=my, target=target
            )
        return NotImplemented


class AttributeExpression(Expression):
    def _evaluate(
        self, key: Iterable = None, my: "ClassAd" = None, target: "ClassAd" = None
    ) -> Any:
        def find_scope(current_key):
            if len(current_key) > 0:
                return my[current_key]
            return my

        value = Undefined()
        if self._expression[0] == ".":
            key = scope_up(self._expression[1])
            expression = self._expression[1][-1]
        elif self._expression[0] == "super":
            key = scope_up(key)
            expression = self._expression[1]
        else:
            expression = self._expression
        try:
            context = find_scope(key)
        except TypeError:
            return Error()
        while isinstance(value, Undefined):
            value = context[expression]
            if isinstance(value, Undefined):
                if len(key) == 0:
                    return Undefined()
                key = scope_up(key)
                context = find_scope(key)
        if isinstance(value, AttributeExpression):
            return value._evaluate(key=key, my=my, target=target)
        return value

    @classmethod
    def from_grammar(cls, tokens):
        result = cls()
        if isinstance(tokens, pp.ParseResults):
            if isinstance(tokens[0], ClassAd):
                result = DotExpression()
                result._expression = tuple(tokens)
            elif isinstance(tokens[0], str) and tokens[0] == ".":
                result._expression = tuple([tokens[0], tokens[1]._expression])
            elif isinstance(tokens[0], NamedExpression):
                result._expression = tuple(
                    [tokens[0]._expression, tokens[1]._expression]
                )
            else:
                if len(tokens) > 1:
                    result._expression = tuple(token._expression for token in tokens)
                else:
                    result._expression = tokens[0]._expression
        else:
            result._expression = tokens
        return result


class UnaryExpression(Expression):
    operator_map = {"-": None, "!": evaluate_not_operator}

    def _evaluate(
        self, key: List[str] = None, my: "ClassAd" = None, target: "ClassAd" = None
    ):
        checked = set()
        to_check = self._expression[1]
        while (
            isinstance(to_check, AttributeExpression)
            and to_check._expression not in checked
        ):
            checked.add(to_check._expression)
            to_check = to_check._evaluate(key=key, my=my, target=target)
        return self.operator_map[self._expression[0]](to_check)


class ArithmeticExpression(Expression):
    operator_map = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "<": operator.lt,
        "<=": operator.le,
        ">=": operator.ge,
        ">": operator.gt,
        "==": evaluate_eq_operator,
        "!=": evaluate_ne_operator,
        "&&": operator.and_,
        "||": operator.or_,
        "=!=": evaluate_isnt_operator,
        "isnt": evaluate_isnt_operator,
        "=?=": evaluate_is_operator,
        "is": evaluate_is_operator,
    }

    def _calculate(self, first, second, operand):
        try:
            return self.operator_map[operand](first, second)
        except (ArithmeticError, AttributeError, TypeError):
            raise NotImplementedError

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

    def _evaluate(
        self, key: List[str] = None, my: "ClassAd" = None, target: "ClassAd" = None
    ):
        result = self._expression[0]._evaluate(key=key, my=my, target=target)
        for position in range(0, len(self._expression) - 1, 2):
            second = self._expression[position + 2]._evaluate(
                key=key, my=my, target=target
            )
            result = self._calculate(result, second, self._expression[position + 1])
        return result
