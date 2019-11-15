"""
Literal constants: integer, float, string, boolean, error, or undefined
"""


class Undefined:
    """
    The keyword ``UNDEFINED`` (case insensitive) represents the ``UNDEFINED`` value.
    """
    def __eq__(self, other):
        return Undefined()


class Error:
    """
    The keyword ``ERROR`` (case insensitive) represents the ``ERROR`` value.
    """
    def __eq__(self, other):
        return type(self) == type(other)


class Attribute:
    """An attribute is the tuple from attribute name and expression."""
    pass


class HTCInt(int):
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


class HTCList(tuple):
    pass


class HTCStr(str):
    def __eq__(self, other):
        if isinstance(other, Undefined):
            return Undefined()
        if isinstance(other, str):
            return self.lower() == other.lower()
        return super().__eq__(other)


class HTCFloat(float):
    def __eq__(self, other):
        if isinstance(other, Undefined):
            return Undefined()
        return super().__eq__(other)


class HTCBool(object):
    def __init__(self, x):
        self._value = True if x != 0 else False

    def __bool__(self):
        return self._value

    def __eq__(self, other):
        if isinstance(other, Undefined):
            return Undefined()
        return super().__eq__(other)
