import pytest

from classad import quantize
from classad._primitives import Error


FLOAT_APPROXIMATION = 0.0000000001


class TestQuantize:
    def test_int(self):
        assert isinstance(quantize(2, 1), int)
        assert isinstance(quantize(2.0, 1), int)
        assert isinstance(quantize(0, 2), int)

    def test_float(self):
        assert isinstance(quantize(2, 1.0), float)
        assert isinstance(quantize(2.0, 1.0), float)
        assert isinstance(quantize(1.0, 2.1), float)
        assert isinstance(quantize(0, 2.0), float)

    def test_examples(self):
        assert 8 == quantize(3, 8)
        assert 4 == quantize(3, 2)
        assert 0 == quantize(0, 4)
        assert pytest.approx(6.8, FLOAT_APPROXIMATION) == quantize(1.5, 6.8)
        assert pytest.approx(7.2, FLOAT_APPROXIMATION) == quantize(6.8, 1.2)
        assert pytest.approx(10.2, FLOAT_APPROXIMATION) == quantize(10, 5.1)

    def test_list_examples(self):
        assert 4 == quantize(0, [4])
        assert 2 == quantize(2, [1, 2, "A"])
        assert 3.0 == quantize(3, [1, 2, 0.5])
        assert 3.0 == quantize(2.7, [1, 2, 0.5])
        assert isinstance(quantize(3, [1, 2, "A"]), Error)
