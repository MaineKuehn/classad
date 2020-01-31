"""
Literal constants: integer, float, string, boolean, error, or undefined
"""
from typing import Union

from classad._base_expression import PrimitiveExpression


class Undefined(PrimitiveExpression):
    """
    The keyword ``UNDEFINED`` (case insensitive) represents the ``UNDEFINED`` value.
    """

    __slots__ = ()

    def __bool__(self):
        raise TypeError

    def __htc_eq__(
        self, other: PrimitiveExpression
    ) -> "Union[PrimitiveExpression, Undefined, Error]":
        if isinstance(other, Error):
            return NotImplemented
        return Undefined()

    def __and__(self, other):
        if isinstance(other, HTCBool) and not other:
            return HTCBool(False)
        return self.__htc_eq__(other)

    def __or__(self, other):
        if isinstance(other, HTCBool) and other:
            return HTCBool(True)
        return self.__htc_eq__(other)

    __add__ = (
        __radd__
    ) = (
        __sub__
    ) = (
        __rsub__
    ) = (
        __mul__
    ) = (
        __rmul__
    ) = (
        __truediv__
    ) = (
        __rtruediv__
    ) = __lt__ = __le__ = __ge__ = __gt__ = __rand__ = __ror__ = __htc_ne__ = __htc_eq__

    def __eq__(self, other: PrimitiveExpression) -> "HTCBool":
        if type(self) == type(other):
            return HTCBool(True)
        return HTCBool(False)

    def __ne__(self, other: PrimitiveExpression) -> "HTCBool":
        return HTCBool(not self.__eq__(other))

    def __htc_not__(self) -> "Union[HTCBool, Undefined, Error]":
        return Undefined()

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def __hash__(self):
        return hash("undefined")


class Error(PrimitiveExpression):
    """
    The keyword ``ERROR`` (case insensitive) represents the ``ERROR`` value.
    """

    __slots__ = ()

    def __bool__(self):
        raise TypeError

    def __htc_eq__(
        self, other: PrimitiveExpression
    ) -> "Union[PrimitiveExpression, Undefined, Error]":
        return Error()

    __add__ = (
        __radd__
    ) = (
        __sub__
    ) = (
        __rsub__
    ) = (
        __mul__
    ) = (
        __rmul__
    ) = (
        __truediv__
    ) = (
        __rtruediv__
    ) = (
        __lt__
    ) = (
        __le__
    ) = (
        __ge__
    ) = __gt__ = __and__ = __rand__ = __or__ = __ror__ = __htc_ne__ = __htc_eq__

    def __eq__(self, other: PrimitiveExpression) -> "HTCBool":
        if type(self) == type(other):
            return HTCBool(True)
        return HTCBool(False)

    def __ne__(self, other: PrimitiveExpression) -> "HTCBool":
        return HTCBool(not self.__eq__(other))

    def __htc_not__(self) -> "Union[HTCBool, Undefined, Error]":
        return Error()

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def __hash__(self):
        return hash("error")


class HTCInt(int, PrimitiveExpression):
    __slots__ = ()

    def __add__(self, other):
        if isinstance(other, int):
            return HTCInt(super().__add__(other))
        elif isinstance(other, (float, Undefined, Error)):
            return NotImplemented
        return Error()

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, int):
            return HTCInt(super().__sub__(other))
        elif isinstance(other, (float, Undefined, Error)):
            return NotImplemented
        return Error()

    def __mul__(self, other):
        if isinstance(other, int):
            return HTCInt(super().__mul__(other))
        elif isinstance(other, (float, Undefined, Error)):
            return NotImplemented
        return Error()

    def __truediv__(self, other):
        try:
            if isinstance(other, int):
                return HTCFloat(super().__truediv__(other))
            elif isinstance(other, (float, Undefined, Error)):
                return NotImplemented
            return Error()
        except ZeroDivisionError:
            return Error()

    def __lt__(self, other):
        try:
            result = super().__lt__(other)
        except TypeError:
            return Error()
        else:
            return result if result is NotImplemented else HTCBool(result)

    def __ge__(self, other):
        try:
            result = super().__ge__(other)
        except TypeError:
            return Error()
        else:
            return result if result is NotImplemented else HTCBool(result)

    def __gt__(self, other):
        try:
            result = super().__gt__(other)
        except TypeError:
            return Error()
        else:
            return result if result is NotImplemented else HTCBool(result)

    def __le__(self, other):
        try:
            result = super().__le__(other)
        except TypeError:
            return Error()
        else:
            return result if result is NotImplemented else HTCBool(result)

    def __htc_eq__(
        self, other: PrimitiveExpression
    ) -> Union[PrimitiveExpression, Undefined, Error]:
        if isinstance(other, int):
            return HTCBool(super().__eq__(other))
        elif isinstance(other, (Undefined, Error, HTCFloat)):
            return NotImplemented
        elif isinstance(other, float):
            return HTCBool(self == other)
        return Error()

    def __htc_ne__(
        self, other: PrimitiveExpression
    ) -> Union[PrimitiveExpression, Undefined, Error]:
        result = self.__htc_eq__(other)
        if isinstance(result, HTCBool):
            return HTCBool(not result)
        return result

    def __eq__(self, other: PrimitiveExpression) -> "HTCBool":
        if isinstance(other, int):
            return HTCBool(super().__eq__(other))
        elif isinstance(other, float):
            return NotImplemented
        return HTCBool(False)

    def __ne__(self, other: PrimitiveExpression) -> "HTCBool":
        if isinstance(other, int):
            return HTCBool(super().__ne__(other))
        elif isinstance(other, float):
            return NotImplemented
        return HTCBool(True)

    def __htc_not__(self) -> "Union[HTCBool, Undefined, Error]":
        return Error()

    def __repr__(self):
        return f"<{self.__class__.__name__}>: {self}"

    def __hash__(self):
        return super().__hash__()


class HTCList(tuple, PrimitiveExpression):
    __slots__ = ()

    def __htc_not__(self) -> "Union[HTCBool, Undefined, Error]":
        return Error()

    def __repr__(self):
        return f"<{self.__class__.__name__}>: {[element for element in self]}"


class HTCStr(str, PrimitiveExpression):
    __slots__ = ()

    def __htc_eq__(
        self, other: PrimitiveExpression
    ) -> Union[PrimitiveExpression, Undefined, Error]:
        if isinstance(other, str):
            return HTCBool(self.lower() == other.lower())
        return NotImplemented

    def __htc_ne__(
        self, other: PrimitiveExpression
    ) -> Union[PrimitiveExpression, Undefined, Error]:
        result = self.__htc_eq__(other)
        if isinstance(result, HTCBool):
            return HTCBool(not result)
        return result

    def __eq__(self, other: PrimitiveExpression) -> "HTCBool":
        if type(self) == type(other) and super().__eq__(other):
            return HTCBool(True)
        return HTCBool(False)

    def __ne__(self, other: PrimitiveExpression) -> "HTCBool":
        if type(self) != type(other) or super().__ne__(other):
            return HTCBool(True)
        return HTCBool(False)

    def __htc_not__(self) -> "Union[HTCBool, Undefined, Error]":
        return Error()

    def __repr__(self):
        return f"<{self.__class__.__name__}>: {self}"

    def __hash__(self):
        return super().__hash__()


class HTCFloat(float, PrimitiveExpression):
    __slots__ = ()

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return HTCFloat(super().__mul__(other))
        elif isinstance(other, (Undefined, Error)):
            return NotImplemented
        return Error()

    __rmul__ = __mul__

    def __htc_not__(self) -> "Union[HTCBool, Undefined, Error]":
        return Error()

    def __htc_eq__(
        self, other: PrimitiveExpression
    ) -> Union[PrimitiveExpression, Undefined, Error]:
        if isinstance(other, (int, float)):
            return HTCBool(super().__eq__(other))
        elif isinstance(other, (Undefined, Error)):
            return NotImplemented
        return Error()

    def __htc_ne__(
        self, other: PrimitiveExpression
    ) -> Union[PrimitiveExpression, Undefined, Error]:
        result = self.__htc_eq__(other)
        if isinstance(result, HTCBool):
            return HTCBool(not result)
        return result

    def __eq__(self, other: PrimitiveExpression) -> "HTCBool":
        if isinstance(other, (int, float)):
            return HTCBool(super().__eq__(other))
        return HTCBool(False)

    def __ne__(self, other: PrimitiveExpression) -> "HTCBool":
        if isinstance(other, (int, float)):
            return HTCBool(super().__ne__(other))
        return HTCBool(False)

    def __repr__(self):
        return f"<{self.__class__.__name__}>: {self}"

    def __hash__(self):
        return super().__hash__()


class HTCBool(PrimitiveExpression):
    __slots__ = ("_value",)

    def __init__(self, x):
        super().__init__()
        self._value = True if x != 0 else False

    def __add__(self, other):
        return Error()

    __sub__ = __mul__ = __truediv__ = __gt__ = __ge__ = __le__ = __lt__ = __add__

    def __eq__(self, other):
        return (
            type(self) == type(other) and self._value == other._value
        ) or other is self._value

    def __ne__(self, other):
        return (
            type(self) == type(other) and self._value != other._value
        ) or other is not self._value

    def __bool__(self):
        return self._value

    def __or__(self, other):
        if not self._value:
            if isinstance(other, (HTCBool, Undefined)):
                return other
        elif self._value:
            return HTCBool(True)
        return Error()

    def __and__(self, other):
        if not self._value:
            return HTCBool(False)
        elif self._value:
            if isinstance(other, (HTCBool, Undefined)):
                return other
        return Error()

    def __htc_eq__(
        self, other: PrimitiveExpression
    ) -> Union[PrimitiveExpression, Undefined, Error]:
        if isinstance(other, HTCBool):
            return HTCBool(self._value is other._value)
        elif isinstance(other, (Undefined, Error)):
            return NotImplemented
        elif isinstance(other, bool):
            return HTCBool(self._value is other)
        return Error()

    def __htc_ne__(
        self, other: "PrimitiveExpression"
    ) -> "Union[HTCBool, Undefined, Error]":
        return self.__htc_not__().__htc_eq__(other)

    def __htc_not__(self) -> "Union[HTCBool, Undefined, Error]":
        return HTCBool(not self._value)

    def __repr__(self):
        return f"<{self.__class__.__name__}>: {self._value}"

    def __hash__(self):
        return hash(self._value)
