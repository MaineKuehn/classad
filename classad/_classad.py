from collections import OrderedDict
from collections.abc import MutableMapping
from typing import Iterator, _T_co, _KT, _VT_co, _VT, Any

from classad._primitives import Undefined


class ClassAd(MutableMapping):
    __slots__ = "_data"

    def __init__(self):
        self._data = OrderedDict()

    def __setitem__(self, key: _KT, value: _VT) -> None:
        """
        Keynames that are reserved and, therefore, cannot be used: error, false, is,
            isnt, parent, true, undefined
        :param key:
        :param value:
        :return:
        """
        key = key.casefold()
        if key in ["error", "false", "is", "isnt", "parent", "true", "undefined"]:
            raise ValueError(f'{key} is a reserved name')
        self._data[key] = value

    def __delitem__(self, key: _KT) -> None:
        self._data.pop(key, None)

    def __getitem__(self, key: _KT) -> _VT_co:
        return self._data.get(key, Undefined())

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[_T_co]:
        return iter(self._data)

    def evaluate(self, key: _KT, target: "ClassAd") -> Any:
        """
        Perform a matchmaking between an expression defined by the named attribute
        key in the context of the target ClassAd.
        :param key:
        :param target:
        :return:
        """
        expression = self[key]
        return expression.evaluate(my=self, target=target)
