from classad import parse
from classad._primitives import HTCInt


def test_simple():
    my_classad = parse("""rank = TARGET.Memory + TARGET.Mips """)
    target_classad = parse(
        """
    Memory = 8
    Mips = 10
    """
    )
    assert my_classad.evaluate(
        key="rank", my=my_classad, target=target_classad
    ) == HTCInt(18)


def test_nested():
    my_classad = parse("""rank = TARGET.a.b + TARGET.c""")
    target_classad = parse("""[c = 1; a = [b = 2; d = 1]]""")
    assert my_classad.evaluate(
        key="rank", my=my_classad, target=target_classad
    ) == HTCInt(3)
