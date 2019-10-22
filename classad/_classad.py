from collections.abc import MutableMapping
from typing import Iterator, _T_co, _KT, _VT_co, _VT

from classad._primitives import Undefined


class ClassAd(MutableMapping):
    __slots__ = "_data"

    def __init__(self):
        self._data = {}

    def __setitem__(self, key: _KT, value: _VT) -> None:
        key = key.casefold()
        self._data[key] = value

    def __delitem__(self, key: _KT) -> None:
        self._data.pop(key, None)

    def __getitem__(self, key: _KT) -> _VT_co:
        return self._data.get(key, Undefined())

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[_T_co]:
        return iter(self._data)
