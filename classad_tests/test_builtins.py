import operator

import pytest

from classad._primitives import (
    Error,
    Undefined,
    HTCInt,
    HTCFloat,
    # HTCList,
    HTCBool,
    HTCStr,
)
from classad._operator import eq_operator, ne_operator


NUMERIC_OPERATORS = (
    operator.__add__,
    operator.__sub__,
    operator.__mul__,
    operator.__truediv__,
)
COMPARISON_OPERATORS = (
    operator.__eq__,
    operator.__ne__,
    operator.__gt__,
    operator.__ge__,
    operator.__le__,
    operator.__lt__,
    eq_operator,
    ne_operator,
)


@pytest.fixture(params=[HTCInt, HTCFloat])
def num_type(request):
    return request.param


def test_numbers(num_type):
    def assert_similar(op, htc_value, htc_type, builtin_value):
        """An HTC and builtin type behave similar with respect to an HTC value"""
        assert op(htc_value, htc_type(builtin_value)) == op(
            htc_value, htc_type(builtin_value)
        )
        assert op(htc_value, htc_type(builtin_value)) == op(htc_value, builtin_value)

    for value in (2, 3, -3, 256, -127, 2 ** 8, 1e6) + (
        () if num_type is HTCInt else (3 - 5, -3.5, 127.3, -123.2, 1e-8)
    ):
        for operation in NUMERIC_OPERATORS + COMPARISON_OPERATORS:
            assert_similar(operation, HTCInt(1), num_type, value)
            assert_similar(operation, HTCInt(123), num_type, value)
            assert_similar(operation, HTCInt(-123), num_type, value)
            assert_similar(operation, HTCFloat(1), num_type, value)
            assert_similar(operation, HTCFloat(123), num_type, value)
            assert_similar(operation, HTCFloat(-123), num_type, value)
        for operation in COMPARISON_OPERATORS:
            assert_similar(operation, HTCBool(True), num_type, value)
            assert_similar(operation, HTCBool(False), num_type, value)
            assert_similar(operation, Error(), num_type, value)
            assert_similar(operation, Undefined(), num_type, value)


def test_hashable():
    test = set()
    try:
        test.add(Undefined())
        test.add(Error())
        test.add(HTCInt(1))
        test.add(HTCFloat(0.0))
        test.add(HTCStr("test"))
        test.add(HTCBool(True))
    except TypeError:
        pytest.fail("Hashing not supported")
    assert len(test) == 6
