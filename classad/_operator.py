from typing import Union

from classad._base_expression import PrimitiveExpression
from classad._primitives import HTCBool, Undefined, Error


def isnt_operator(a: PrimitiveExpression, b: PrimitiveExpression) -> HTCBool:
    """
    Isnt operator as defined by classad specification. Resulting values are only
    in the domain as defined by :py:class:`~.HTCBool`.

    .. Note:
        The `isnt` operator is similar to the inequality operator. It checks if
        the left hand side operand is not identical in both type and value to
        the right hand side operator, returning the :py:class:`~.HTCBool` value
        `False` when they are identical.

    .. Warning:
        The `isnt` operator for strings is case-sensitive while it isn't for
        the inequality operator.

    .. code:
        parse('("ABC" =!= "abc")').evaluate()  # result: HTCBool(True)
        parse("(10 =!= Undefined)").evaluate()  # result: HTCBool(False)
        parse("(10 != Undefined)").evaluate()  # result: Undefined
    """
    result = a.__htc_isnt__(b)
    if result == NotImplemented:
        result = b.__htc_isnt__(a)
    return result


def is_operator(a, b):
    """
    Is operator as defined by classad specification.
    """
    result = a.__htc_is__(b)
    if result == NotImplemented:
        result = b.__htc_is__(a)
    return result


def eq_operator(
    a: PrimitiveExpression, b: PrimitiveExpression
) -> Union[HTCBool, Undefined, Error]:
    """
    Equality operator as defined by classad specification, i.e. operator does
    not only return :py:class:`~.HTCBool` but also :py:class:`~.Undefined` or
    :py:class:`~.Error` if necessary.

    This operator is used automatically when you use `"=="` in one of the
    classad expressions. However, when working with the parsed objects, i.e.
    :py:class:`~.PrimaryExpression` you will get the expected python
    behaviour.

    .. code:: python3
        parse("10 == Undefined").evaluate()  # result: Undefined
        HTCBool(True) == Undefined()  # result: False
    """
    result = a.__htc_eq__(b)
    if result == NotImplemented:
        result = b.__htc_eq__(a)
    return result


def ne_operator(
    a: PrimitiveExpression, b: PrimitiveExpression
) -> Union[HTCBool, Undefined, Error]:
    """
    Inequality operator as defined by classad specificiation, i.e. operator does
    not only return :py:class:`~.HTCBool` but also :py:class:`~.Undefined` or
    :py:class:`~.Error` if necessary.

    This operator is used automatically when you use `"!="` in one of the
    classad expressions. However, when working with the parsed objects, i.e.
    :py:class:`~.PrimaryExpression` you will get the expected python
    behaviour.

    .. code:: python3
        parse("10 != Undefined").evaluate()  # result: Undefined
        HTCBool(True) != Undefined()  # result: True
    """
    result = a.__htc_ne__(b)
    if result == NotImplemented:
        result = b.__htc_ne__(a)
    return result


def not_operator(a: PrimitiveExpression) -> Union[HTCBool, Undefined, Error]:
    """
    Logical not operator as defined by classad specification.

    .. code:: python3
        parse("!False").evaluate()  # result: True
    """
    return a.__htc_not__()
