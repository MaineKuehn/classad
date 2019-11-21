import operator
from collections import MutableMapping

import pyparsing as pp
from typing import Any, Iterable, List, Iterator, Optional, Union

from classad._operator import eq_operator, ne_operator, not_operator
from classad._primitives import Error, Undefined, HTCBool
from ._base_expression import Expression
from . import _functions


def scope_up(key: List[str]):
    return key[:-1]


class ClassAd(Expression, MutableMapping):
    __slots__ = "_data"

    def __add__(self, other):
        return Error()

    __sub__ = __rsub__ = __radd__ = __add__

    def __init__(self):
        super().__init__()
        self._data = dict()

    def __setitem__(self, key: Union[str, Expression], value: Expression) -> None:
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

    def __delitem__(self, key: Union[str, Expression]) -> None:
        self._data.pop(key, None)

    def __getitem__(self, key: Iterable[Union[str, Expression]]) -> Expression:
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
        self,
        key: Optional[Iterable[Union[str, Expression]]] = None,
        my: "Optional[ClassAd]" = None,
        target: "Optional[ClassAd]" = None,
    ) -> Any:
        """
        Perform a matchmaking between an expression defined by the named attribute
        key in the context of the target ClassAd.
        """
        if key is None:
            return self
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
        return HTCBool(type(self) == type(other) and self._data == other._data)

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
        self,
        key: Optional[Iterable[Union[str, Expression]]] = None,
        my: "Optional[ClassAd]" = None,
        target: "Optional[ClassAd]" = None,
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
        self,
        key: Optional[Iterable[Union[str, Expression]]] = None,
        my: "Optional[ClassAd]" = None,
        target: "Optional[ClassAd]" = None,
    ) -> Any:
        predicate, if_true, if_false = self._expression
        result = predicate._evaluate(key=key, my=my, target=target)
        if if_true is None:
            if isinstance(result, Undefined):
                return if_false._evaluate(key=key, my=my, target=target)
            else:
                return result
        if isinstance(result, Undefined):
            return Undefined()
        if isinstance(result, HTCBool):
            if result:
                return if_true._evaluate(key=key, my=my, target=target)
            elif not result:
                return if_false._evaluate(key=key, my=my, target=target)
        return Error()


class DotExpression(Expression):
    def _evaluate(
        self,
        key: Optional[Iterable[Union[str, Expression]]] = None,
        my: "Optional[ClassAd]" = None,
        target: "Optional[ClassAd]" = None,
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
        self,
        key: Optional[Iterable[Union[str, Expression]]] = None,
        my: "Optional[ClassAd]" = None,
        target: "Optional[ClassAd]" = None,
    ) -> Any:
        operand = self._expression[0]._evaluate(key=key, my=my, target=target)
        index = self._expression[1]._evaluate(key=key, my=my, target=target)
        return operand[index]._evaluate(key=key, my=my, target=target)


class AttributeExpression(Expression):
    def _evaluate(
        self,
        key: Optional[Iterable[Union[str, Expression]]] = None,
        my: "Optional[ClassAd]" = None,
        target: "Optional[ClassAd]" = None,
    ) -> Any:
        def find_scope(current_key):
            if len(current_key) > 0:
                return my[current_key]
            return my

        value = Undefined()
        if self._expression[0] == ".":
            key = scope_up(self._expression[1])
            expression = self._expression[1][-1]
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
    operator_map = {"-": None, "!": not_operator}

    def _evaluate(
        self,
        key: Optional[Iterable[Union[str, Expression]]] = None,
        my: "Optional[ClassAd]" = None,
        target: "Optional[ClassAd]" = None,
    ):
        operand = self._expression[1]._evaluate(key=key, my=my, target=target)
        return self.operator_map[self._expression[0]](operand)


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
        "==": eq_operator,
        "!=": ne_operator,
        "&&": operator.and_,
        "||": operator.or_,
        "=!=": operator.ne,
        "isnt": operator.ne,
        "=?=": operator.eq,
        "is": operator.eq,
    }

    def _calculate(self, first, second, operand):
        try:
            return self.operator_map[operand](first, second)
        except (ArithmeticError, AttributeError, TypeError):
            return Error()

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
        self,
        key: Optional[Iterable[Union[str, Expression]]] = None,
        my: "Optional[ClassAd]" = None,
        target: "Optional[ClassAd]" = None,
    ):
        result = self._expression[0]._evaluate(key=key, my=my, target=target)
        for position in range(0, len(self._expression) - 1, 2):
            second = self._expression[position + 2]._evaluate(
                key=key, my=my, target=target
            )
            result = self._calculate(result, second, self._expression[position + 1])
        return result
