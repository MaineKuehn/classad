from collections import OrderedDict
from collections.abc import MutableMapping
from typing import Iterator, Any, TYPE_CHECKING
from classad._primitives import Undefined

if TYPE_CHECKING:
    from classad._expression import Expression


class ClassAd(MutableMapping):
    __slots__ = "_data"

    def __init__(self):
        self._data = OrderedDict()

    def __setitem__(self, key: str, value: "Expression") -> None:
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

    def __getitem__(self, key: str) -> "Expression":
        key = key.casefold()
        return self._data.get(key, Undefined())

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def evaluate(self, key: str, target: "ClassAd") -> Any:
        """
        Perform a matchmaking between an expression defined by the named attribute
        key in the context of the target ClassAd.
        :param key:
        :param target:
        :return:
        """
        expression = self[key]
        return expression.evaluate(my=self, target=target)

    @classmethod
    def from_grammar(cls, tokens):
        result = cls()
        for token in tokens:
            print(token)
            result[token[0]] = token[1]
        return result

    def __eq__(self, other):
        if type(self) == type(other):
            return self._data == other._data
        return False

    def __repr__(self):
        return f"<{self.__class__.__name__}>: {self._data}"
