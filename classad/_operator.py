from typing import Union

from classad._base_expression import PrimitiveExpression
from classad._primitives import HTCBool, Undefined, Error


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
        HTCBool(True) == Undefined()  # result: HTCBool(False)
    """
    result = a.__htc_eq__(b)
    if result == NotImplemented:
        result = b.__htc_eq__(a)
    return result


def ne_operator(
    a: PrimitiveExpression, b: PrimitiveExpression
) -> Union[HTCBool, Undefined, Error]:
    """
    Inequality operator as defined by classad specification, i.e. operator does
    not only return :py:class:`~.HTCBool` but also :py:class:`~.Undefined` or
    :py:class:`~.Error` if necessary.

    This operator is used automatically when you use `"!="` in one of the
    classad expressions. However, when working with the parsed objects, i.e.
    :py:class:`~.PrimaryExpression` you will get the expected python
    behaviour.

    .. code:: python3
        parse("10 != Undefined").evaluate()  # result: Undefined
        HTCBool(True) != Undefined()  # result: HTCBool(True)
    """
    result = a.__htc_ne__(b)
    if result == NotImplemented:
        result = b.__htc_ne__(a)
    return result


def not_operator(a: PrimitiveExpression) -> Union[HTCBool, Undefined, Error]:
    """
    Logical not operator as defined by classad specification.

    .. code:: python3
        parse("!False").evaluate()  # result: HTCBool(True)
    """
    return a.__htc_not__()
