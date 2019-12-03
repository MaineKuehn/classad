"""
This module defines internal functions as defined in the classad specification
in the `HTCondor Manual <https://htcondor.readthedocs.io/en/stable/misc-concepts/
classad-mechanism.html>`_.
Some of the functions defined in the `official specification
<https://research.cs.wisc.edu/htcondor/classad/refman/node4.html#
SECTION00043900000000000000>`_
are excluded as those are not listed in the HTCondor Manual, those include

* isClassad(a: "Expression") -> bool: ...
* isList(a: "Expression") -> bool: ...
* isAbstime(a: "Expression") -> bool: ...
* isReltime(a: "Expression") -> bool: ...
* sum(l: List) -> number: ...
* avg(l: List) -> number: ...
* min(l: List) -> number: ...
* max(l: List) -> number: ...
* member(x: literal_type, l: str) -> bool: ...
* identicalMember(x: literal_type, l: str) -> bool: ...
* regexpMember(pattern: str, l: str, options: Optional[str] = None) -> bool: ...
* anycompare(s: str, l: List, t: literal_type) -> bool: ...
* allcompare(s: str, l: List, t: literal_type) -> bool: ...
* absTime(s: str) -> AbsTime: ...
* absTime(t: Optional[literal_type] = None, z: Optional[int] = None) -> AbsTime: ...
* relTime(t: literal_type) -> RelTime: ...
* splitTime(time: Union[RelTime, AbsTime]) -> ClassAd: ...
* formatTime(t: Union[AbsTime, int], s: str) -> str: ...

.. TODO::

    General check for number of attributes defined is currently not supported
    by the given functions below. We should maybe consider overriding all functions
    and having the general function with `*args`.
"""
import math
import random as py_random
from typing import TypeVar, List, Union, overload, Optional, Any

from classad._grammar import parse
from classad._base_expression import Expression
from classad._primitives import (
    Undefined,
    Error,
    HTCFloat,
    HTCInt,
    HTCStr,
    HTCBool,
    HTCList,
)

T = TypeVar("T", HTCFloat, HTCInt)
number = Union[HTCFloat, HTCInt]
literal_type = Union[number, HTCStr, HTCBool, Undefined, Error]


def eval(expression: Any) -> literal_type:
    """
    Evaluates :py:attr:`expression` as a string and then returns the
    result of evaluating the contents of the string as a :py:class:`~.ClassAd`
    expression.
    """
    if isinstance(expression, Expression):
        return expression
    return parse(expression)


def unparse(attribute: Expression) -> str:
    """
    This function looks up the value of the provided :py:attr:`attribute` and
    returns the unparsed version as a :py:class:`str`. The attribute's value is
    not evaluated.
    If the attribute's value is ``x + 3``, then the function would return the
    string ``"x + 3"``. If the provided attribute cannot be found, an empty string
    is returned.

    This function returns :py:class:`~.Error` if other than exactly ``1``
    argument is given or the argument is not an attribute reference.
    """
    return attribute.__repr__()


def ifThenElse(
    if_expression: literal_type,
    then_expression: literal_type,
    else_expression: literal_type,
) -> literal_type:
    """
    A conditional expression is described by :py:attr:`if_expression`. The following
    defines the return values, when :py:attr:`if_expression` evaluates to

    * :py:data:`True` - evaluate and return the value as given by
      :py:attr:`then_expression`
    * :py:data:`False` - evaluate and return the value as given by
      :py:attr:`else_expression`
    * :py:class:`~.Undefined` - return the value :py:class:`~.Undefined`
    * :py:class:`~.Error` - return the value :py:class:`~.Error`
    * ``0.0`` - evaluate and return the value as given by
      :py:attr:`else_expression`
    * non-``0.0`` float values - evaluate and return the value as given by
      :py:attr:`then_expression`

    If :py:attr:`if_expression`` evaluates to give a value of type :py:class:`str`,
    the function returns the value :py:class:`~.Error`. The implementation uses lazy
    evaluation, so expressions are only evaluated as defined.

    This function returns :py:class:`~.Error` if other than exactly ``3``
    arguments are given.

    .. TODO::

        What about int?
    """
    result = eval(if_expression)
    if isinstance(result, (HTCStr, Error)):
        return Error()
    if isinstance(result, Undefined):
        return Undefined()
    if result:  # true and non-zero floats
        return eval(then_expression)
    elif not result:  # false and zero floats
        return eval(else_expression)


def isUndefined(expression: literal_type) -> Union[HTCBool, Error]:
    """
    Returns :py:data:`True`, if :py:attr:`expression` evaluates to
    :py:class:`~.Undefined`. Returns :py:data:`False` in all other cases.

    This function returns :py:class:`~.Error` if other than exactly ``1``
    argument is given.
    """
    result = eval(expression)
    if isinstance(result, Undefined):
        return HTCBool(1)
    return HTCBool(0)


def isError(expression: literal_type) -> Union[HTCBool, Error]:
    """
    Returns :py:data:`True` if :py:attr:`expression` evaluates to :py:class:`~.Error`.
    Returns :py:data:`False` in all other cases.

    This function returns :py:class:`~.Error` if other than exactly ``1``
    argument is given.
    """
    result = eval(expression)
    if isinstance(result, Error):
        return HTCBool(1)
    return HTCBool(0)


def isString(expression: literal_type) -> Union[HTCBool, Error]:
    """
    Returns :py:data:`True` if :py:attr:`expression` evaluates to a :py:class:`str`.
    Returns :py:data:`False` in all other cases.

    This function returns :py:class:`~.Error` if other than exactly ``1``
    argument is given.
    """
    result = eval(expression)
    if isinstance(result, HTCStr):
        return HTCBool(1)
    return HTCBool(0)


def isInteger(expression: literal_type) -> Union[HTCBool, Error]:
    """
    Returns :py:data:`True` if :py:attr:`expression` evaluates to an :py:class:`int`.
    Returns :py:data:`False` in all other cases.

    This function returns :py:class:`~.Error` if other than exactly ``1``
    argument is given.
    """
    result = eval(expression)
    if isinstance(result, HTCInt):
        return HTCBool(1)
    return HTCBool(0)


def isReal(expression: literal_type) -> Union[HTCBool, Error]:
    """
    Returns :py:data:`True` if :py:attr:`expression` evaluates to  a :py:class:`float`.
    Returns :py:data:`False` in all other cases.

    This function returns :py:class:`~.Error` if other than exactly ``1``
    argument is given.
    """
    result = eval(expression)
    if isinstance(result, HTCFloat):
        return HTCBool(1)
    return HTCBool(0)


def isBoolean(expression: literal_type) -> Union[HTCBool, Error]:
    """
    Returns :py:data:`True` if :py:attr:`expression` evaluates to a :py:class:`bool`.
    Returns :py:data:`False` in all other cases.

    This function returns :py:class:`~.Error` if other than exactly ``1``
    argument is given.
    """
    result = eval(expression)
    if isinstance(result, HTCBool):
        return HTCBool(1)
    return HTCBool(0)


def int(expression: literal_type) -> Union[HTCInt, Error]:
    """
    Returns the integer value defined by :py:attr:`expression`.
    If the type of the evaluated :py:attr:`expression` is :py:class:`float`,
    the value is truncated (round towards zero) to an :py:class:`int`.
    If the type of the evaluated :py:attr:`expression` is :py:class:`str`,
    the string is converted to an :py:class:`int`. If this result is not an integer,
    :py:class:`~.Error` is returned.
    If the evaluated :py:attr:`expression` is :py:class:`~.Error` or
    :py:class:`~.Undefined`, :py:class:`~.Error` is returned.

    This function returns :py:class:`~.Error` if other than exactly ``1``
    argument is given.
    """
    result = eval(expression)
    if isInteger(result):
        return result
    elif isReal(result):
        return HTCInt(math.trunc(result))
    elif isString(result):
        try:
            return HTCInt(result)
        except ValueError:
            pass
    return Error()


def real(expression: literal_type) -> Union[HTCFloat, Error]:
    """
    Returns the :py:class:`float` value defined by :py:attr:`expression`.
    If the type of the evaluated :py:attr:`expression` is :py:class:`int`, the
    return value is the converted integer.
    If the type of the evaluated :py:attr:`expression` is :py:class:`str`, the
    string is converted to a :py:class:`float` value. If this result is not a
    float, :py:class:`~.Error` is returned.
    If the evaluated :py:attr:`expression` is :py:class:`~.Error` or
    :py:class:`~.Undefined`, :py:class:`~.Error` is returned.

    This function returns :py:class:`~.Error` if other than exactly ``1``
    argument is given.
    """
    result = eval(expression)
    if isReal(result):
        return result
    elif isInteger(result):
        return HTCFloat(result)
    elif isString(result):
        try:
            return HTCFloat(result)
        except ValueError:
            pass
    return Error()


def string(expression: literal_type) -> Union[HTCStr, Error]:
    """
    Returns the string that results from evaluating :py:attr:`expression`.
    A non-string value is converted to a string.
    If the evaluated :py:attr:`expression` is :py:class:`~.Error` or
    :py:class:`~.Undefined`, :py:class:`~.Error` is returned.

    This function returns :py:class:`~.Error` if other than exactly ``1``
    argument is given.
    """
    result = eval(expression)
    if isString(result):
        return result
    elif isUndefined(result) or isError(result):
        return Error()
    return HTCStr(result)


def floor(expression: literal_type) -> Union[HTCInt, Error]:
    """
    Returns the integer that results from evaluating :py:attr:`expression`, if
    the type of the evaluated :py:attr:`expression` is :py:class:`int`.
    If the type of the evaluated :py:attr:`expression` is not integer, function
    :py:func:`~.real` is called. Its return value is then used to return the
    largest magnitude integer that is not larger than the returned value.
    If function :py:func:`~.real` returns :py:class:`~.Error` or
    :py:class:`~.Undefined`, :py:class:`~.Error` is returned.

    This function returns :py:class:`~.Error` if other than exactly ``1``
    argument is given.
    """
    result = eval(expression)
    if isInteger(result):
        return result
    result = real(result)
    try:
        return HTCInt(math.floor(result))
    except TypeError:
        pass
    return Error()


def ceiling(expression: literal_type) -> Union[HTCInt, Error]:
    """
    Returns the integer that results from evaluating :py:attr:`expression`, if
    the type of the evaluated :py:attr:`expression` is :py:class:`int`.
    If the type of the evaluated :py:attr:`expression` is not integer, function
    :py:func:`~.real` is called. Its return value is then used to return the
    smallest magnitude integer that is not less than the returned value.
    If function :py:func:`~.real` returns :py:class:`~.Error` or
    :py:class:`~.Undefined`, :py:class:`~.Error` is returned.

    This function returns :py:class:`~.Error` if other than exactly ``1``
    argument is given.
    """
    result = eval(expression)
    if isInteger(result):
        return result
    result = real(result)
    try:
        return HTCInt(math.ceil(result))
    except TypeError:
        pass
    return Error()


@overload
def pow(base: HTCInt, exponent: HTCInt) -> HTCInt:
    ...


@overload
def pow(base: HTCInt, exponent: HTCInt) -> HTCFloat:
    ...


@overload
def pow(base: HTCFloat, exponent: HTCFloat) -> HTCFloat:
    ...


def pow(base, exponent):
    """
    Calculates :py:attr:`base` raised to the power of :py:attr:`exponent`.
    If :py:attr:`exponent` is an integer value greater than or equal to ``0``,
    and :py:attr:`base` is an integer, then an integer value is returned.
    If :py:attr:`exponent` is an integer value less than ``0``, or if either
    :py:attr:`base` or :py:attr:`exponent` is a float, then a float value is
    returned. An invocation with ``exponent=0`` or ``exponent=0.0``, for any
    value of ``base``, including ``0`` or ``0.0``returns the value ``1`` or
    ``1.0``, type appropriate.
    """
    result = math.pow(base, exponent)
    if exponent >= 0 and isinstance(exponent, HTCInt) and isinstance(base, HTCInt):
        return HTCInt(result)
    return HTCFloat(result)


@overload
def quantize(a: literal_type, b: HTCInt) -> HTCInt:
    ...


@overload
def quantize(a: literal_type, b: HTCFloat) -> HTCFloat:
    ...


@overload
def quantize(a: literal_type, b: List[literal_type]) -> literal_type:
    ...


def quantize(a, b):
    """
    :py:func:`~.quantize` computes the quotient of ``a/b``, in order to further
    compute ``ceiling(quotient) * b``. This computes and returns an integral
    multiple of :py:attr:`b` that is at least as large as :py:attr:`a`. So, when
    ``b >= a``, the return value will be :py:attr:`b`. The return type is the
    same as that of :py:attr:`b`, where :py:attr:`b` is an :py:class:`int` or
    :py:class:`float`.

    When :py:attr:`b` is a :py:class:`list`, :py:func:`~.quantize` returns the
    first value in the list that is greater than or equal to :py:attr:`a`.
    When no value in the list is greater than or equal to :py:attr:`a`, this
    computes and returns an integral multiple of the last member in the list
    that is at least as large as :py:attr:`a`.

    This function returns :py:func:`~.Error` if :py:attr:`a` or :py:attr:`b`, or
    a member of the list that must be considered is not an int or float.

    Here are examples:

    .. code::

        8     = quantize(3, 8)
        4     = quantize(3, 2)
        0     = quantize(0, 4)
        6.8   = quantize(1.5, 6.8)
        7.2   = quantize(6.8, 1.2)
        10.2  = quantize(10, 5.1)

        4     = quantize(0, {4})
        2     = quantize(2, {1, 2, "A"})
        3.0   = quantize(3, {1, 2, 0.5})
        3.0   = quantize(2.7, {1, 2, 0.5})
        ERROR = quantize(3, {1, 2, "A"})
    """
    if isinstance(b, HTCList):
        for element in b:
            try:
                if element >= a:
                    return element
            except TypeError:
                return Error()
        return quantize(a, element)
    else:
        try:
            quotient = HTCFloat(a / b)
        except TypeError:
            return Error()
        return ceiling(quotient) * b


def round(expression: literal_type) -> Union[HTCInt, Error]:
    """
    Returns the integer that results from the evaluation of :py:attr:`expression`,
    if the type of the evaluated :py:attr:`expression` is :py:class:`int`.
    If the type of the evaluated :py:attr:`expression` is not :py:class:`int`,
    function :py:func:`~.real` is called. Its return value is then used to return
    the integer that results from a round-to-nearest rounding method. The nearest
    integer value to the return value is returned, except in the case of the
    value at the exact midpoint between two integer values. In this case, the
    even valued integer is returned.
    If ``real(expression)`` returns :py:class:`~.Error` or :py:class:`~.Undefined`,
    or the integer value does not fit into 32 bits, :py:class:`~.Error` is returned.

    This function returns :py:class:`~.Error` if other than exactly ``1``
    argument is given.
    """
    result = eval(expression)
    if isInteger(result):
        return result
    else:
        result = real(result)
        if isReal(result):
            return round(result)
    return Error()


def random(expression: literal_type = 1.0) -> Union[number, Error]:
    """
    If the optional argument :py:attr:`expression` evaluates to type :py:class:`int`
    or :py:class:`float` called ``x``, the return value is the integer or float ``r``
    randomly chosen from the interval ``0 <= r < x``. With no argument, the
    return value is chosen with ``random(1.0)``. Returns :py:class:`~.Error`
    in all other cases.

    This function returns :py:class:`~.Error` if greater than ``1`` argument
    is given.
    """
    result = eval(expression)
    if isinstance(result, HTCInt):
        return HTCInt(py_random.randint(0, result))
    elif isinstance(result, HTCFloat):
        return HTCFloat(py_random.uniform(0, result))
    return Error()


def strcat(expression: literal_type, *args: literal_type) -> Union[HTCStr, Error]:
    """
    Returns the string which is the concatenation of all arguments, where all
    arguments are converted to type :py:class:`str` by function :py:func:`~.string`.
    Returns :py:class:`~.Error` if any argument evaluates to :py:class:`~.Undefined`
    or :py:class:`~.Error`.
    """
    parts = []
    for arg in [expression, *args]:
        element = string(arg)
        if isinstance(element, Undefined) or isinstance(element, Error):
            return element
        parts.append(element)
    return HTCStr("".join(parts))


@overload
def join(seperator: HTCStr, *args: literal_type) -> Union[HTCStr, Error]:
    ...


@overload
def join(seperator: HTCStr, arguments: HTCList) -> Union[HTCStr, Error]:
    ...


@overload
def join(arguments: HTCList) -> Union[HTCStr, Error]:
    ...


def join(*args):
    """
    Returns the string which is the concatenation of all arguments after the first
    one. The first argument is the separator, and it is inserted between each of
    the other arguments during concatenation. All arguments are converted to type
    :py:class:`string` by :py:func:`~.string` before concatenation.
    If there are exactly two arguments and the second argument is a
    :py:class:`list`, all members of the list are converted to strings and then
    joined using the separator.
    If there is only one argument, and the argument is a list, all members of
    the list are converted to strings and then concatenated.

    Returns :py:class:`~.Error` if any argument evaluates to :py:class:`~Undefined`
    or :py:class:`~.Error`.

    For example:

    .. code::

        "a, b, c" = join(", ", "a", "b", "c")
        "abc"     = join(split("a b c"))
        "a;b;c"   = join(";", split("a b c"))
    """
    if len(args) == 1:
        return HTCStr("".join(args[0]))
    if len(args) == 2 and isinstance(args[1], HTCList):
        return HTCStr(args[0].join(args[1]))
    return HTCStr(args[0].join(args[1:]))


def substr(
    s: HTCStr, offset: HTCInt, length: Optional[HTCInt] = None
) -> Union[HTCStr, Error]:
    """
    Returns the substring of :py:attr:`s`, from the position indicated by
    :py:attr:`offset`, with (optional) :py:attr:`length` characters. The first
    character within :py:attr:`s` is at offset ``0``.
    If the optional :py:attr:`length` argument is not present, the substring
    extends to the end of the string.
    If :py:attr:`offset` is negative, the value ``(length - offset)`` is used
    for the offset.
    If :py:attr:`length` is negative, an initial substring is computed, from the
    offset to the end of the string. Then, the absolute value of :py:attr:`length`
    characters are deleted from the right end of the initial substring. Further,
    where characters of this resulting substring lie outside the original string,
    the part that lies within the original string is returned. If the substring
    lies completely outside the original string, the null string is returned.

    This function returns :py:class:`~.Error` if greater than ``3`` or less than
    ``2`` arguments are given.
    """
    raise NotImplementedError


def strcmp(a: literal_type, b: literal_type) -> Union[HTCInt, Error]:
    """
    Both arguments are converted to :py:class:`str` by function :py:func:`~.string`.
    The return value is an integer that will be

    * less than 0, if ``a`` is lexicographically less than ``b``
    * equal to 0, if ``a`` is lexicographically equal to ``b``
    * greater than 0, if ``a`` is lexicographically greater than ``b``

    If either argument evaluates to :py:class:`~.Error` or :py:class:`~.Undefined`,
    :py:class:`~.Error` is returned.

    This function returns :py:class:`~.Error` if other than ``2`` arguments are
    given.

    .. seealso::

        Case is significant in comparison.
        Refer to :py:func:`~.stricmp` for case insignificant comparison.
    """
    raise NotImplementedError


def stricmp(a: literal_type, b: literal_type) -> Union[HTCInt, Error]:
    """
    This function is the same as :py:func:`~.strcmp`, except that letter case is
    not significant.

    .. seealso::

        Refer to :py:func:`~.strcmp` for case significant comparison.
    """
    raise NotImplementedError


def toUpper(s: literal_type) -> Union[HTCStr, Error]:
    """
    The single argument :py:attr:`s` is converted to type :py:class:`str` by
    function :py:func:`~.string`. The return value is this string, with all lower
    case letters converted to upper case.
    If the argument evaluates to :py:class:`~.Error` or :py:class:`~.Undefined`,
    :py:class:`~.Error` is returned.

    This function returns :py:class:`~.Error` if other than exactly ``1``
    argument is given.
    """
    raise NotImplementedError


def toLower(s: literal_type) -> Union[HTCStr, Error]:
    """
    The single argument :py:attr:`s` is converted to type :py:class:`str` by
    function :py:func:`~.string`. The return value is this string, with all upper
    case letters converted to lower case.
    If the argument evaluates to :py:class:`~.Error` or :py:class:`~.Undefined`,
    :py:class:`~.Error` is returned.

    This function returns :py:class:`~.Error` if other than exactly ``1``
    argument is given.
    """
    raise NotImplementedError


def size(expression: literal_type) -> Union[HTCInt, Error]:
    """
    Returns the number of characters in the string, after calling function
    :py:func:`~.string`. If the argument evaluates to :py:class:`~.Error` or
    :py:class:`~.Undefined`, :py:class:`~.Error` is returned.

    This function returns :py:class:`~.Error` if other than exactly ``1``
    argument is given.
    """
    raise NotImplementedError


def split(s: HTCStr, tokens: Optional[HTCStr] = None) -> List[HTCStr]:
    """
    Returns a list of the substrings of :py:attr:`s` that have been split up by
    using any of the characters within string :py:attr:`tokens`.
    If :py:attr:`tokens` is not specified, then all white space characters are
    used to delimit the string.
    """
    if tokens:
        raise NotImplementedError
    return HTCList(s.split())


def splitUserName(name: HTCStr) -> List[HTCStr]:
    """
    Returns a list of two strings. Where :py:attr:`name` includes an ``@`` character,
    the first string in the list will be the substring that comes before the
    ``@`` character, and the second string in the list will be the substring
    that comes after. Thus, if :py:attr:`name` is ``"user@domain"``, then the
    returned list will be ``{"user", "domain"}``. If there is no ``@`` character
    in :py:attr:`name`, then the first string in the list will be :py:attr:`name`,
    and the second string in the list will be the empty string.
    Thus, if :py:attr:`name` is ``username``, then the returned list will be
    ``{"username", ""}``.
    """
    raise NotImplementedError


def splitSlotName(name: HTCStr) -> List[HTCStr]:
    """
    Returns a list of two strings. Where :py:attr:`name` includes an ``@``
    character, the first string in the list will be the substring that comes
    before the ``@`` character, and the second string in the list will be the
    substring that comes after. Thus, if :py:attr:`name` is ``"slot1@machine"``,
    then the returned list will be ``{"slot1", "machine"}``.
    If there is no ``@`` character in :py:attr:`name`, then the first string in
    the list will be the empty string, and the second string in the list will
    be :py:attr:`name`. Thus, if :py:attr:`name` is ``"machinename"``, then the
    returned list will be ``{"machinename"}``.
    """
    raise NotImplementedError


def time() -> HTCInt:
    """
    Returns the current coordinated universal time. This is the time, in seconds,
    since midnight of January 1, 1970.
    """
    raise NotImplementedError


def formatTime(time: Optional[HTCInt], format: Optional[HTCStr]) -> HTCStr:
    """
    Returns a formatted string that is a representation of :py:attr:`time`. The
    argument :py:attr:`time` is interpreted as coordinated universal time in
    seconds, since midnight of January 1, 1970. If not specified, :py:attr:`time`
    will default to the current time.

    The argument :py:attr:`format` is interpreted similarly to the format argument
    of the ANSI C strftime function. It consists of arbitrary text plus placeholders
    for elements of the time. These placeholders are percent signs (%) followed
    by a single letter. To have a percent sign in the output, use a double
    percent sign (%%). If :py:attr:`format` is not specified, it defaults to ``%c``.

    Because the implementation uses strftime() to implement this, and some
    versions implement extra, non-ANSI C options, the exact options available
    to an implementation may vary. An implementation is only required to
    implement the ANSI C options which are:

    ``%a``
        abbreviated weekday name

    ``%A``
        full weekday name

    ``%b``
        abbreviated month name

    ``%B``
        full month name

    ``%c``
        local date and time representation

    ``%d``
        day of the month (01-31)

    ``%H``
        hour in the 24-hour clock (0-23)

    ``%I``
        hour in the 12-hour clock (01-12)

    ``%j``
        day of the year (001-366)

    ``%m``
        month (01-12)

    ``%M``
        minute (00-59)

    ``%p``
        local equivalent of AM or PM

    ``%S``
        second (00-59)

    ``%U``
        week number of the year (Sunday as first day of week) (00-53)

    ``%w``
        weekday (0-6, Sunday is 0)

    ``%W``
        week number of the year (Monday as first day of week) (00-53)

    ``%x``
        local date representation

    ``%X``
        local time representation

    ``%y``
        year without century (00-99)

    ``%Y``
        year with century

    ``%Z``
        time zone name, if any
    """
    raise NotImplementedError


def interval(seconds: HTCInt) -> HTCStr:
    """
    Uses :py:attr:`seconds` to return a string of the form ``days+hh:mm:ss``.
    This represents an interval of time. Leading values that are zero are
    omitted from the string. For example, :py:attr:`seconds` of 67 becomes
    ``"1:07"``. A second example, :py:attr:`seconds` of
    ``1472523 = 17*24*60*60 + 1*60*60 + 3``, results in the string ``"17+1:02:03"``.
    """
    raise NotImplementedError


def debug(expression: literal_type) -> literal_type:
    """
    This function evaluates its argument, and it returns the result. Thus,
    it is a no-operation. However, a side-effect of the function is that
    information about the evaluation is logged to the evaluating program’s
    log file, at the ``D_FULLDEBUG`` debug level. This is useful for
    determining why a given ClassAd expression is evaluating the way it does.
    For example, if a condor_startd ``START`` expression is unexpectedly
    evaluating to :py:class:`~.Undefined`, then wrapping the expression in this
    :py:func:`~.debug` function will log information about each component of
    the expression to the log file, making it easier to understand the expression.
    """
    raise NotImplementedError


def envV1ToV2(old_env: HTCStr) -> HTCStr:
    """
    This function converts a set of environment variables from the old HTCondor
    syntax to the new syntax. The single argument should evaluate to a string
    that represents a set of environment variables using the old HTCondor
    syntax (usually stored in the job ClassAd attribute ``Env``). The result
    is the same set of environment variables using the new HTCondor syntax
    (usually stored in the job ClassAd attribute ``Environment``).
    If the argument evaluates to :py:class:`~.Undefined`, then the result is
    also :py:class:`~.Undefined`.
    """
    raise NotImplementedError


def mergeEnvironment(env: HTCStr, *args: HTCStr) -> HTCStr:
    """
    This function merges multiple sets of environment variables into a single
    set. If multiple arguments include the same variable, the one that appears
    last in the argument list is used. Each argument should evaluate to a string
    which represents a set of environment variables using the new HTCondor
    syntax or :py:class:`~.Undefined`, which is treated like an empty string.
    The result is a string that represents the merged set of environment
    variables using the new HTCondor syntax (suitable for use as the value of
    the job ClassAd attribute ``Environment``).
    """
    raise NotImplementedError


def stringListSize(
    string_list: HTCStr, delimiter: Optional[HTCStr]
) -> Union[HTCInt, Error]:
    """
    Returns the number of elements in the string :py:attr:`string_list`, as
    delimited by the optional :py:attr:`delimiter` string. Returns
    :py:class:`~.Error` if either argument is not a :py:class:`str`.

    This function returns :py:class:`~.Error` if other than ``1`` or ``2``
    arguments are given.

    .. note::

        The default delimiter contains the comma and space characters. A string
        within the :py:attr:`string_list` is ended (delimited) by one or more
        characters within the :py:attr:`delimiter` string.
    """
    raise NotImplementedError


@overload
def stringListSum(
    string_list: HTCStr, delimiter: Optional[HTCStr] = None
) -> Union[HTCInt, Error]:
    ...


@overload
def stringListSum(
    string_list: HTCStr, delimiter: Optional[HTCStr] = None
) -> Union[HTCFloat, Error]:
    ...


def stringListSum(string_list, delimiter=None):
    """
    Sums and returns the sum of all items in the string :py:attr:`string_list`, as
    delimited by the optional :py:attr:`delimiter` string. If all items in the list
    are integers, the return value is :py:class:`int`. If any item in the list
    is a float value (non-integer), the return value is :py:class:`float`.
    If any item does not represent an integer or float value, the return value is
    :py:class:`~.Error`.

    .. note::

        The default delimiter contains the comma and space characters. A string
        within the :py:attr:`string_list` is ended (delimited) by one or more
        characters within the :py:attr:`delimiter` string.
    """
    raise NotImplementedError


def stringListAvg(string_list: HTCStr, delimiter: Optional[HTCStr] = None) -> HTCFloat:
    """
    Sums and returns the float-valued average of all items in the string
    :py:attr:`string_list`, as delimited by the optional :py:attr:`delimiter` string.
    If any item does not represent an integer or float value, the return value
    is :py:class:`~.Error`. A list with ``0`` items (the empty list) returns the
    value 0.0.

    .. note::

        The default delimiter contains the comma and space characters. A string
        within the :py:attr:`string_list` is ended (delimited) by one or more
        characters within the :py:attr:`delimiter` string.
    """
    raise NotImplementedError


def stringListMin(
    string_list: HTCStr, delimiter: Optional[HTCStr] = None
) -> Union[number, Error, Undefined]:
    """
    Finds and returns the minimum value from all items in the string
    :py:attr:`string_list`, as delimited by the optional :py:attr:`delimiter` string.
    If all items in the list are integers, the return value is :py:class:`int`.
    If any item in the list is a float value (non-integer), the return value
    :py:class:`float`.
    If any item does not represent an integer or float value, the return value is
    :py:class:`~.Error`. A list with ``0`` items (the empty list) returns the value
    :py:class:`~.Undefined`.

    .. note::

        The default delimiter contains the comma and space characters. A string
        within the :py:attr:`string_list` is ended (delimited) by one or more
        characters within the :py:attr:`delimiter` string.
    """
    raise NotImplementedError


def stringListMax(
    string_list: HTCStr, delimiter: Optional[HTCStr] = None
) -> Union[number, Error, Undefined]:
    """
    Finds and returns the maximum value from all items in the string
    :py:attr:`string_list`, as delimited by the optional :py:attr:`delimiter` string.
    If all items in the list are integers, the return value is :py:class:`int`.
    If any item in the list is a float value (noninteger), the return value
    :py:class:`float`.
    If any item does not represent an integer or float value, the return value is
    :py:class:`~.Error`. A list with ``0`` items (the empty list) returns the value
    :py:class:`~.Undefined`.

    .. note::

        The default delimiter contains the comma and space characters. A string
        within the :py:attr:`string_list` is ended (delimited) by one or more
        characters within the :py:attr:`delimiter` string.
    """
    raise NotImplementedError


def stringListMember(
    x: HTCStr, string_list: HTCStr, delimiter: Optional[HTCStr] = None
) -> Union[HTCBool, Error]:
    """
    Returns :py:data:`True` if item :py:attr:`x` is in the string
    :py:attr:`string_list`, as delimited by the optional :py:attr:`delimiter`
    string.
    Returns :py:data:`False` if item :py:attr:`x` is not in the string
    :py:attr:`string_list`. Comparison is done with :py:func:`~.strcmp`.
    The return value is :py:class:`~.Error`, if any of the arguments are not strings.

    .. note::

        The default delimiter contains the comma and space characters. A string
        within the :py:attr:`string_list` is ended (delimited) by one or more
        characters within the :py:attr:`delimiter` string.
    """
    raise NotImplementedError


def stringListIMember(
    x: HTCStr, string_list: HTCStr, delimiter: Optional[HTCStr] = None
) -> Union[HTCBool, Error]:
    """
    Same as :py:func:`~.stringListMember`, but comparison is done with
    :py:func:`~.stricmp`, so letter case is not relevant.

    .. note::

        The default delimiter contains the comma and space characters. A string
        within the :py:attr:`string_list` is ended (delimited) by one or more
        characters within the :py:attr:`delimiter` string.
    """
    raise NotImplementedError


def stringListsIntersect(
    list_a: HTCStr, list_b: HTCStr, delimiter: Optional[HTCStr] = None
) -> Union[HTCInt, Error]:
    """
    Returns :py:data:`True` if the lists contain any matching elements, and
    returns :py:data:`False` if the lists do not contain any matching elements.
    Returns :py:class:`~.Error` if either argument is not a :py:class:`str` or
    if an incorrect number of arguments are given.

    .. note::

        The default delimiter contains the comma and space characters. A string
        within the :py:attr:`string_list` is ended (delimited) by one or more
        characters within the :py:attr:`delimiter` string.
    """
    raise NotImplementedError


def regexp(
    pattern: HTCStr, target: HTCStr, options: Optional[HTCStr] = None
) -> Union[HTCBool, Error]:
    """
    Uses the description of a regular expression given by string
    :py:attr:`pattern` to scan through the string :py:attr:`target`.
    Returns :py:data:`True` when target is a regular expression given by
    :py:attr:`pattern`. Returns :py:data:`False` otherwise.
    If any argument is not a :py:class:`str`, or if :py:attr:`pattern` does not
    describe a valid regular expression, returns :py:class:`~.Error`.

    The :py:attr:`options` argument is a string of special characters that
    modify the use of the regular expressions. Inclusion of characters other
    than these as options are ignored.

    ``I`` or ``i``
        Ignore letter case.

    ``M`` or ``m``
        Modifies the interpretation of the caret (^) and dollar sign ($)
        characters. The caret character matches the start of a string, as well
        as after each newline character. The dollar sign character matches
        before a newline character.

    ``S`` or ``s``
        The period matches any character, including the newline character.
    """
    raise NotImplementedError


def regexps(
    pattern: HTCStr,
    target: HTCStr,
    substitute: HTCStr,
    options: Optional[HTCStr] = None,
) -> Union[HTCStr, Error]:
    """
    Uses the description of a regular expression given by string
    :py:attr:`pattern` to scan through the string :py:attr:`target`.
    If :py:attr:`target` is a regular expression as described by :py:attr:`pattern`,
    the string substitute is returned, with backslash expansion performed.
    If any argument is not a :py:class:`str`, returns :py:class:`~.Error`.

    The :py:attr:`options` argument is a string of special characters that
    modify the use of the regular expressions. Inclusion of characters other
    than these as options are ignored.

    ``I`` or ``i``
        Ignore letter case.

    ``M`` or ``m``
        Modifies the interpretation of the caret (^) and dollar sign ($)
        characters. The caret character matches the start of a string, as well
        as after each newline character. The dollar sign character matches
        before a newline character.

    ``S`` or ``s``
        The period matches any character, including the newline character.
    """
    raise NotImplementedError


def stringList_regexpMember(
    pattern: HTCStr,
    string_list: HTCStr,
    delimiter: Optional[HTCStr] = None,
    options: Optional[HTCStr] = None,
) -> Union[HTCBool, Error]:
    """
    Uses the description of a regular expression given by string
    :py:attr:`pattern` to scan through the list of strings in :py:attr:`string_list`.
    Returns :py:data:`True` when one of the strings in :py:attr:`string_list`
    is a regular expression as described by :py:attr:`pattern`.
    The optional :py:attr:`delimiter` describes how the list is delimited, and
    string :py:attr:`options` modifies how the match is performed.
    Returns :py:data:`False` if :py:attr:`pattern` does not match any entries in
    :py:attr:`string_list`. The return value is :py:class:`~.Error`, if any of the
    arguments are not :py:class:`str`, or if :py:attr:`pattern` is not a valid
    regular expression.

    The :py:attr:`options` argument is a string of special characters that modify
    the use of the regular expressions. Inclusion of characters other than these as
    options are ignored.

    ``I`` or ``i``
        Ignore letter case.

    ``M`` or ``m``
        Modifies the interpretation of the caret (^) and dollar sign ($)
        characters. The caret character matches the start of a string, as well
        as after each newline character. The dollar sign character matches
        before a newline character.

    ``S`` or ``s``
        The period matches any character, including the newline character.
    """
    raise NotImplementedError


def userHome(userName: HTCStr, default: Optional[HTCStr] = None) -> HTCStr:
    """
    Returns the home directory of the given user as configured on the current
    system (determined using the getpwdnam() call).
    (Returns :py:attr:`default` if the :py:attr:`default` argument is passed
    and the home directory of the user is not defined.)
    """
    raise NotImplementedError


@overload
def userMap(mapSetName: HTCStr, userName: HTCStr) -> HTCList:
    """
    Map an input string using the given mapping set. Returns a list of groups
    to which the user belongs.
    """
    ...


@overload
def userMap(
    mapSetName: HTCStr, userName: HTCStr, preferredGroup: HTCStr
) -> Union[HTCStr, Undefined]:
    """
    Map an input string using the given mapping set. Returns a string, which is
    the preferred group if the user is in that group; otherwise it is the first
    group to which the user belongs, or :py:class:`~.Undefined` if the user
    belongs to no groups.
    """
    ...


@overload
def userMap(
    mapSetName: HTCStr, userName: HTCStr, preferredGroup: HTCStr, defaultGroup: HTCStr
) -> HTCStr:
    """
    Map an input string using the given mapping set. Returns a string, which is
    the preferred group if the user is in that group; the first group to which
    the user belongs, if any; and the default group if the user belongs to no
    groups.
    """
    ...


def userMap(mapSetName, userName, *args):
    """
    The maps for the :py:func:`~.userMap` function are defined by the following
    configuration macros: ``<SUBSYS>_CLASSAD_USER_MAP_NAMES``,
    ``CLASSAD_USER_MAPFILE_<name>`` and ``CLASSAD_USER_MAPDATA_<name>``
    (see the `HTCondor-wide Configuration File Entries section <https://htcondor.
    readthedocs.io/en/stable/admin-manual/configuration-macros.html#
    htcondor-wide-configuration-file-entries>`_).
    """
    raise NotImplementedError
