from classad import substr
from classad._primitives import HTCStr, Error


class TestSubstr(object):
    def test_simple(self):
        test_string = "test_string"
        assert substr(HTCStr(test_string), 1) == HTCStr(test_string[1:])
        assert substr(1.0, 1) == Error()

    def test_zero(self):
        test_string = "test_string"
        assert substr(HTCStr(test_string), 0) == HTCStr(test_string)
        assert substr(HTCStr(test_string), 0) == substr(HTCStr(test_string), -0)

    def test_negative(self):
        test_string = "test_string"
        for offset in [-1, -len(test_string)]:
            assert substr(HTCStr(test_string), offset) == HTCStr(
                test_string[len(test_string) + offset :]  # noqa: E203
            )
