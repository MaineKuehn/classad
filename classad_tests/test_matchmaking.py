from classad import parse
from classad._primitives import HTCInt, Undefined


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


def test_undefined():
    assert parse("""rank = TARGET.a""").evaluate("rank") == Undefined()
    assert parse("""rank = my.a""").evaluate("rank") == Undefined()


def test_lookup():
    my_classad = parse(
        """
    a = 10
    b = c
    """
    )
    target_classad = parse("""c = 1""")
    assert my_classad.evaluate(key="b", my=my_classad, target=target_classad) == HTCInt(
        1
    )


def test_nested_lookup():
    my_classad = parse("""rank = a.b + c""")
    target_classad = parse("""[c = 1; a = [b = 2; d = 1]]""")
    assert my_classad.evaluate(
        key="rank", my=my_classad, target=target_classad
    ) == HTCInt(3)
