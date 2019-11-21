import pytest

from classad import quantize
from classad._primitives import Error, HTCInt, HTCFloat, HTCList, HTCStr

FLOAT_APPROXIMATION = 0.0000000001


class TestQuantize:
    def test_int(self):
        assert isinstance(quantize(HTCInt(2), HTCInt(1)), HTCInt)
        assert isinstance(quantize(HTCFloat(2.0), HTCInt(1)), HTCInt)
        assert isinstance(quantize(HTCInt(0), HTCInt(2)), HTCInt)

    def test_float(self):
        assert isinstance(quantize(HTCInt(2), HTCFloat(1.0)), HTCFloat)
        assert isinstance(quantize(HTCFloat(2.0), HTCFloat(1.0)), HTCFloat)
        assert isinstance(quantize(HTCFloat(1.0), HTCFloat(2.1)), HTCFloat)
        assert isinstance(quantize(HTCInt(0), HTCFloat(2.0)), HTCFloat)

    def test_examples(self):
        assert HTCInt(8) == quantize(HTCInt(3), HTCInt(8))
        assert HTCInt(4) == quantize(HTCInt(3), HTCInt(2))
        assert HTCInt(0) == quantize(HTCInt(0), HTCInt(4))
        assert pytest.approx(HTCFloat(6.8), FLOAT_APPROXIMATION) == quantize(
            HTCFloat(1.5), HTCFloat(6.8)
        )
        assert pytest.approx(HTCFloat(7.2), FLOAT_APPROXIMATION) == quantize(
            HTCFloat(6.8), HTCFloat(1.2)
        )
        assert pytest.approx(HTCFloat(10.2), FLOAT_APPROXIMATION) == quantize(
            HTCInt(10), HTCFloat(5.1)
        )

    def test_list_examples(self):
        assert HTCInt(4) == quantize(HTCInt(0), HTCList([HTCInt(4)]))
        assert HTCInt(2) == quantize(
            HTCInt(2), HTCList([HTCInt(1), HTCInt(2), HTCStr("A")])
        )
        assert HTCFloat(3.0) == quantize(
            HTCInt(3), HTCList([HTCInt(1), HTCInt(2), HTCFloat(0.5)])
        )
        assert HTCFloat(3.0) == quantize(
            HTCFloat(2.7), HTCList([HTCInt(1), HTCInt(2), HTCFloat(0.5)])
        )
        assert isinstance(
            quantize(HTCInt(3), HTCList([HTCInt(1), HTCInt(2), HTCStr("A")])), Error
        )
