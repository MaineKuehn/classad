from classad import _grammar, quantize, parse
from classad._classad import ClassAd
from classad._primitives import Error, Undefined, HTCInt, HTCFloat, HTCList, HTCStr


class TestGrammar(object):
    def test_example_classad(self):
        classad = """
        MyType = "Machine"
        TargetType = "Job"
        Machine = "froth.cs.wisc.edu"
        Arch = "INTEL"
        OpSys = "LINUX"
        Disk = 35882
        Memory = 128
        KeyboardIdle = 173
        LoadAvg = 0.1000
        Requirements = TARGET.Owner=="smith" || LoadAvg<=0.3 && KeyboardIdle>15*60
        """
        result = _grammar.expression.parseString(classad, parseAll=True)
        print(result)
        assert isinstance(result[0], ClassAd)
        keys = result[0].keys()
        assert 10, len(keys)
        assert 35882, result[0]["Disk"]
        assert 0.1, result[0]["LoadAvg"]

    def test_old_and_new(self):
        old = r"""
        Foo = 3
        Bar = "ab\"cd\\ef"
        Moo = Foo =!= Undefined
        """
        new = r"""
        [
        Foo = 3;
        Bar = "ab\"cd\\ef";
        Moo = Foo isnt Undefined;
        ]
        """
        old_result = _grammar.expression.parseString(old, parseAll=True)
        new_result = _grammar.expression.parseString(new, parseAll=True)
        assert old_result[0] == new_result[0]

    def test_quantize(self):
        assert _grammar.expression.parseString("quantize(3, 8)")[0].evaluate(
            None, None
        ) == quantize(HTCInt(3), HTCInt(8))
        assert _grammar.expression.parseString("quantize(3, 2)")[0].evaluate(
            None, None
        ) == quantize(HTCInt(3), HTCInt(2))
        assert _grammar.expression.parseString("quantize(0, 4)")[0].evaluate(
            None, None
        ) == quantize(HTCInt(0), HTCInt(4))
        assert _grammar.expression.parseString("quantize(1.5, 6.8)")[0].evaluate(
            None, None
        ) == quantize(HTCFloat(1.5), HTCFloat(6.8))
        assert _grammar.expression.parseString("quantize(6.8, 1.2)")[0].evaluate(
            None, None
        ) == quantize(HTCFloat(6.8), HTCFloat(1.2))
        assert _grammar.expression.parseString("quantize(10, 5.1)")[0].evaluate(
            None, None
        ) == quantize(HTCInt(10), HTCFloat(5.1))
        assert _grammar.expression.parseString("quantize(0, {4})")[0].evaluate(
            None, None
        ) == quantize(HTCInt(0), HTCList([HTCInt(4)]))
        assert _grammar.expression.parseString('quantize(2, {1, 2, "A"})')[0].evaluate(
            None, None
        ) == quantize(HTCInt(2), HTCList([HTCInt(1), HTCInt(2), HTCStr("A")]))
        assert _grammar.expression.parseString("quantize(3, {1, 2, 0.5})")[0].evaluate(
            None, None
        ) == quantize(HTCInt(3), HTCList([HTCInt(1), HTCInt(2), HTCFloat(0.5)]))
        assert _grammar.expression.parseString("quantize(2.7, {1, 2, 0.5})")[
            0
        ].evaluate(None, None) == quantize(
            HTCFloat(2.7), HTCList([HTCInt(1), HTCInt(2), HTCFloat(0.5)])
        )
        assert _grammar.expression.parseString('quantize(3, {1, 2, "A"})')[0].evaluate(
            None, None
        ) == quantize(HTCInt(3), HTCList([HTCInt(1), HTCInt(2), HTCStr("A")]))

    def test_join(self):
        assert (
            _grammar.expression.parseString('join(", ", "a", "b", "c")')[0].evaluate(
                None, None
            )
            == "a, b, c"
        )
        assert (
            _grammar.expression.parseString('join(split("a b c"))')[0].evaluate(
                None, None
            )
            == "abc"
        )
        assert (
            _grammar.expression.parseString('join(";", split("a b c"))')[0].evaluate(
                None, None
            )
            == "a;b;c"
        )

    def test_parse(self):
        classad = "[a = 1; b = 2]"
        assert _grammar.expression.parseString(classad)[0] == parse(classad)

    def test_example_expressions(self):
        assert parse("(10 == 10)")
        assert not parse("(10 == 5)")
        assert parse('(10 == "ABC")') == Error()
        assert parse('"ABC" == "abc"')
        assert parse("(10 == UNDEFINED)") == Undefined()
        assert parse("(UNDEFINED == UNDEFINED)") == Undefined()

        assert parse("(10 =?= 10)")
        assert not parse("(10 =?= 5)")
        assert not parse('(10 =?= "ABC")')
        assert not parse('"ABC" =?= "abc"')
        assert not parse('(10 =?= UNDEFINED)')
        assert parse("(UNDEFINED =?= UNDEFINED)")

        assert not parse("(10 != 10)")
        assert parse("(10 != 5)")
        assert parse('(10 != "ABC")') == Error()
        assert not parse('"ABC" != "abc"')
        assert parse("(10 != UNDEFINED)") == Undefined()
        assert parse("(UNDEFINED != UNDEFINED)") == Undefined()

        assert not parse("(10 =!= 10)")
        assert parse("(10 =!= 5)")
        assert parse('(10 =!= "ABC")')
        assert parse('"ABC" =!= "abc"')
        assert parse("(10 =!= UNDEFINED)")
        assert not parse("(UNDEFINED =!= UNDEFINED)")
