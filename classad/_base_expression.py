import pyparsing as pp

from typing import Iterable, Any, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ._expression import ClassAd
    from ._primitives import Undefined, Error, HTCBool


class Expression:
    _expression: "Expression"

    def evaluate(
        self, key: Iterable = None, my: "ClassAd" = None, target: "ClassAd" = None
    ) -> Any:
        if isinstance(key, str):
            key = key.split(".")
        return self._evaluate(key=key, my=my, target=target)

    def _evaluate(
        self, key: Iterable = None, my: "ClassAd" = None, target: "ClassAd" = None
    ) -> Any:
        return NotImplemented

    @classmethod
    def from_grammar(cls, tokens):
        result = cls()
        if isinstance(tokens, pp.ParseResults):
            # return all primitives as is
            if len(tokens) == 1:
                return tokens[0]
            else:
                expression = []
                for token in tokens:
                    if isinstance(token, pp.ParseResults):
                        expression.append(token[0])
                    else:
                        expression.append(token)
                result._expression = tuple(expression)
        else:
            result._expression = tokens
        return result

    def __repr__(self):
        return f"<{self.__class__.__name__}>: {self._expression}"

    def __eq__(self, other):
        return type(self) == type(other) and self._expression == other._expression


class PrimitiveExpression(Expression):
    def evaluate(
        self, key: Iterable = None, my: "ClassAd" = None, target: "ClassAd" = None
    ) -> Any:
        return self

    def _evaluate(
        self, key: Iterable = None, my: "ClassAd" = None, target: "ClassAd" = None
    ) -> Any:
        return self

    def __htc_eq__(
        self, b: "PrimitiveExpression"
    ) -> "Union[PrimitiveExpression, Undefined, Error]":
        return NotImplemented

    def __htc_ne__(
        self, b: "PrimitiveExpression"
    ) -> "Union[PrimitiveExpression, Undefined, Error]":
        return NotImplemented

    def __htc_not__(self) -> "Union[HTCBool, Undefined, Error]":
        return NotImplemented

    def __htc_isnt__(self, b: "PrimitiveExpression") -> "HTCBool":
        return NotImplemented
