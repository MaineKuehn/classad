from classad import parse
from classad._primitives import HTCInt


def test_simple():
    first_part = parse("my.a + 2")
    my_classad = parse("a = 4")
    assert first_part.evaluate(my=my_classad) == HTCInt(6)
