from typing import Any

from classad._classad import ClassAd


class Expression:
    def __init__(self):
        self._expression = None

    def evaluate(self, my: ClassAd, target: ClassAd) -> Any:
        return NotImplemented

    @classmethod
    def from_grammar(cls, tokens):
        print(f"received {tokens}")
        result = cls()
        result._expression = tokens
        return result

    def __repr__(self):
        return f"<{self.__class__.__name__}>: {self._expression}"


class FunctionExpression(Expression):
    @classmethod
    def from_grammar(cls, tokens):
        result = cls()
        result._expression = tokens
        return result


class AttributeExpression(Expression):
    @classmethod
    def from_grammar(cls, tokens):
        result = cls()
        result._expression = tokens
        return result
