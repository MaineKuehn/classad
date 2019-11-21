"""
Literal constants: integer, float, string, boolean, error, or undefined
"""
from typing import Union

from classad._base_expression import PrimitiveExpression


class Undefined(PrimitiveExpression):
    """
    The keyword ``UNDEFINED`` (case insensitive) represents the ``UNDEFINED`` value.
    """

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


class Error(PrimitiveExpression):
    """
    The keyword ``ERROR`` (case insensitive) represents the ``ERROR`` value.
    """

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


class HTCInt(int, PrimitiveExpression):
    def __add__(self, other):
        if isinstance(other, HTCInt):
            return HTCInt(super().__add__(other))
        elif (
            isinstance(other, HTCFloat)
            or isinstance(other, Undefined)
            or isinstance(other, Error)
        ):
            return NotImplemented
        return Error()

    def __sub__(self, other):
        if isinstance(other, HTCInt):
            return HTCInt(super().__sub__(other))
        elif (
            isinstance(other, HTCFloat)
            or isinstance(other, Undefined)
            or isinstance(other, Error)
        ):
            return NotImplemented
        return Error()

    def __mul__(self, other):
        if isinstance(other, HTCInt):
            return HTCInt(super().__mul__(other))
        elif (
            isinstance(other, HTCFloat)
            or isinstance(other, Undefined)
            or isinstance(other, Error)
        ):
            return NotImplemented
        return Error()

    def __truediv__(self, other):
        try:
            if isinstance(other, HTCInt):
                return HTCFloat(super().__truediv__(other))
            elif (
                isinstance(other, HTCFloat)
                or isinstance(other, Undefined)
                or isinstance(other, Error)
            ):
                return NotImplemented
            return Error()
        except ZeroDivisionError:
            return Error()

    def __lt__(self, other):
        try:
            return HTCBool(super().__lt__(other))
        except TypeError:
            return Error()

    def __ge__(self, other):
        result = self.__lt__(other)
        if isinstance(result, HTCBool):
            return HTCBool(not result)
        return result

    def __gt__(self, other):
        try:
            return HTCBool(super().__gt__(other))
        except TypeError:
            return Error()

    def __le__(self, other):
        result = self.__gt__(other)
        if isinstance(result, HTCBool):
            return HTCBool(not result)
        return result

    def __htc_eq__(
        self, other: PrimitiveExpression
    ) -> Union[PrimitiveExpression, Undefined, Error]:
        if type(self) == type(other) or isinstance(other, HTCFloat):
            return HTCBool(super().__eq__(other))
        elif isinstance(other, Undefined) or isinstance(other, Error):
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


class HTCList(tuple, PrimitiveExpression):
    def __htc_not__(self) -> "Union[HTCBool, Undefined, Error]":
        return Error()

    def __repr__(self):
        return f"<{self.__class__.__name__}>: {[element for element in self]}"


class HTCStr(str, PrimitiveExpression):
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


class HTCFloat(float, PrimitiveExpression):
    def __mul__(self, other):
        if isinstance(other, HTCFloat) or isinstance(other, HTCInt):
            return HTCFloat(super().__mul__(other))
        elif isinstance(other, Undefined) or isinstance(other, Error):
            return NotImplemented
        return Error()

    __rmul__ = __mul__

    def __htc_not__(self) -> "Union[HTCBool, Undefined, Error]":
        return Error()

    def __repr__(self):
        return f"<{self.__class__.__name__}>: {self}"


class HTCBool(PrimitiveExpression):
    def __init__(self, x):
        super().__init__()
        self._value = True if x != 0 else False

    def __eq__(self, other):
        return type(self) == type(other) and self._value == other._value

    def __bool__(self):
        return self._value

    def __or__(self, other):
        if not self._value:
            if isinstance(other, HTCBool) or isinstance(other, Undefined):
                return other
        elif self._value:
            return HTCBool(True)
        return Error()

    def __and__(self, other):
        if not self._value:
            return HTCBool(False)
        elif self._value:
            if isinstance(other, HTCBool) or isinstance(other, Undefined):
                return other
        return Error()

    def __htc_not__(self) -> "Union[HTCBool, Undefined, Error]":
        return HTCBool(not self._value)

    def __repr__(self):
        return f"<{self.__class__.__name__}>: {self._value}"
