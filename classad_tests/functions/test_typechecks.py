from classad import isUndefined
from classad._primitives import Undefined, Error, HTCInt, HTCFloat, HTCStr, HTCList


class TestTypechecks(object):
    def test_isUndefined(self):
        assert isUndefined(Undefined())
        for element in [
            Error(),
            HTCInt(1),
            HTCFloat(2.0),
            HTCStr("test"),
            HTCList([Undefined()]),
        ]:
            assert not isUndefined(element)
