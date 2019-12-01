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
