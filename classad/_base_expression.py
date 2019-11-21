import pyparsing as pp

from typing import Iterable, Any, TYPE_CHECKING, Union, Optional

if TYPE_CHECKING:
    from ._expression import ClassAd
    from ._primitives import Undefined, Error, HTCBool


class Expression:
    _expression: "Expression"

    def evaluate(
        self,
        key: "Optional[Iterable[Union[str, Expression]]]" = None,
        my: "Optional[ClassAd]" = None,
        target: "Optional[ClassAd]" = None,
    ) -> Any:
        if isinstance(key, str):
            key = key.split(".")
        return self._evaluate(key=key, my=my, target=target)

    def _evaluate(
        self,
        key: "Optional[Iterable[Union[str, Expression]]]" = None,
        my: "Optional[ClassAd]" = None,
        target: "Optional[ClassAd]" = None,
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
                expression = [
                    token[0] if isinstance(token, pp.ParseResults) else token
                    for token in tokens
                ]
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
        self,
        key: Optional[Iterable[Union[str, Expression]]] = None,
        my: "Optional[ClassAd]" = None,
        target: "Optional[ClassAd]" = None,
    ) -> Any:
        return self

    def _evaluate(
        self,
        key: Optional[Iterable[Union[str, Expression]]] = None,
        my: "Optional[ClassAd]" = None,
        target: "Optional[ClassAd]" = None,
    ) -> Any:
        return self

    def __htc_eq__(
        self, b: "PrimitiveExpression"
    ) -> "Union[HTCBool, Undefined, Error]":
        return NotImplemented

    def __htc_ne__(
        self, b: "PrimitiveExpression"
    ) -> "Union[HTCBool, Undefined, Error]":
        return NotImplemented

    def __htc_not__(self) -> "Union[HTCBool, Undefined, Error]":
        return NotImplemented

    def __eq__(self, other: "PrimitiveExpression") -> "HTCBool":
        """
        Implementation of `is` and `=?=` operator as defined by classad
        specification. Resulting values are only in the domain as defined by
        :py:class:`~.HTCBool`.

        .. Note:
            The `is` operator is similar to the equality operator `==`. It checks if
            the left hand side operand is identical in both type and value to the
            right hand side operator, returning the :py:class:`~.HTCBool` value
            `True` when they are identical.

        .. Warning:
            The `is` operator for strings is case-sensitive while it isn't for
            the HTCondor ``==`` operator.

        .. code:
            parse('("ABC" =?= "abc")').evaluate()  # result: HTCBool(False)
            parse("(10 =?= Undefined)").evaluate()  # result: HTCBool(False)
            parse("(10 == Undefined)").evaluate()  # result: Undefined
        """
        return NotImplemented

    def __ne__(self, other: "PrimitiveExpression") -> "HTCBool":
        """
        Implementation of `isnt` and `=!=` operator as defined by classad
        specification. Resulting values are only in the domain as defined by
        :py:class:`~.HTCBool`.

        .. Note:
            The `isnt` operator is similar to the inequality operator `!=`. It checks
            if the left hand side operand is not identical in both type and value to
            the right hand side operator, returning the :py:class:`~.HTCBool` value
            `False` when they are identical.

        .. Warning:
            The `isnt` operator for strings is case-sensitive while it isn't for
            the HTCondor ``!=`` operator..

        .. code:
            parse('("ABC" =!= "abc")').evaluate()  # result: HTCBool(True)
            parse("(10 =!= Undefined)").evaluate()  # result: HTCBool(True)
            parse("(10 != Undefined)").evaluate()  # result: Undefined
        """
        return NotImplemented
