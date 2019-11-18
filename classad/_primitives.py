"""
Literal constants: integer, float, string, boolean, error, or undefined
"""


class Undefined:
    """
    The keyword ``UNDEFINED`` (case insensitive) represents the ``UNDEFINED`` value.
    """

    def __eq__(self, other):
        return Undefined()

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
    ) = __ge__ = __gt__ = __ne__ = __and__ = __rand__ = __or__ = __ror__ = __eq__

    def __is__(self, other):
        if type(self) == type(other):
            return HTCBool(1)
        return HTCBool(0)

    def __isnt__(self, other):
        return not self.__is__(other)

    def __repr__(self):
        return f"<{self.__class__.__name__}>"


class Error:
    """
    The keyword ``ERROR`` (case insensitive) represents the ``ERROR`` value.
    """

    def __eq__(self, other):
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
    ) = __ge__ = __gt__ = __ne__ = __and__ = __rand__ = __or__ = __ror__ = __eq__

    def __is__(self, other):
        if type(self) == type(other):
            return HTCBool(1)
        return HTCBool(0)

    def __isnt__(self, other):
        return not self.__is__(other)

    def __repr__(self):
        return f"<{self.__class__.__name__}>"


class Attribute:
    """An attribute is the tuple from attribute name and expression."""

    pass


class HTCInt(int):
    def __add__(self, other):
        if isinstance(other, int):
            return HTCInt(super().__add__(other))
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, int):
            return HTCInt(super().__mul__(other))
        elif isinstance(other, float):
            return HTCFloat(other * int(self))
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, Undefined):
            return Undefined()
        if not isinstance(other, int):
            return Error()
        return super().__eq__(other)

    def __ne__(self, other):
        result = self.__eq__(other)
        if isinstance(result, bool):
            return not result
        return result

    def __truediv__(self, other):
        try:
            return super().__truediv__(other)
        except ZeroDivisionError:
            return Error()

    def __is__(self, other):
        """Case-sensitive comparison"""
        if type(self) == type(other) and self == other:
            return HTCBool(1)
        return HTCBool(0)

    def __isnt__(self, other):
        if type(self) != type(other) or self != other:
            return HTCBool(1)
        return HTCBool(0)


class HTCList(tuple):
    pass


class HTCStr(str):
    def __eq__(self, other):
        if isinstance(other, Undefined):
            return Undefined()
        if isinstance(other, str):
            return self.lower() == other.lower()
        return super().__eq__(other)

    def __ne__(self, other):
        result = self.__eq__(other)
        if isinstance(result, bool):
            return not result
        return result

    def __is__(self, other):
        if type(self) == type(other) and super().__eq__(other):
            return HTCBool(1)
        return HTCBool(0)

    def __isnt__(self, other):
        if type(self) != type(other) or super().__ne__(other):
            return HTCBool(1)
        return HTCBool(0)


class HTCFloat(float):
    def __eq__(self, other):
        if isinstance(other, Undefined):
            return Undefined()
        return super().__eq__(other)

    def __ne__(self, other):
        result = self.__eq__(other)
        if isinstance(result, bool):
            return not result
        return result


class HTCBool(object):
    def __init__(self, x):
        self._value = True if x != 0 else False

    def __bool__(self):
        return self._value

    def __eq__(self, other):
        if isinstance(other, Undefined):
            return Undefined()
        return super().__eq__(other)

    def __repr__(self):
        return f"<{self._value}>"
