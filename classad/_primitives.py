"""
Literal constants: integer, float, string, boolean, error, or undefined
"""


class Undefined:
    """
    The keyword ``UNDEFINED`` (case insensitive) represents the ``UNDEFINED`` value.
    """
    def __eq__(self, other):
        return type(self) == type(other)


class Error:
    """
    The keyword ``ERROR`` (case insensitive) represents the ``ERROR`` value.
    """
    def __eq__(self, other):
        return type(self) == type(other)


class Attribute:
    """An attribute is the tuple from attribute name and expression."""
    pass
