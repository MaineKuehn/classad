from classad import _grammar, quantize, parse
from classad._classad import ClassAd


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
        assert _grammar.expression.parseString(
            "quantize(3, 8)")[0].evaluate(None, None) == quantize(3, 8)
        assert _grammar.expression.parseString(
            "quantize(3, 2)")[0].evaluate(None, None) == quantize(3, 2)
        assert _grammar.expression.parseString(
            "quantize(0, 4)")[0].evaluate(None, None) == quantize(0, 4)
        assert _grammar.expression.parseString(
            "quantize(1.5, 6.8)")[0].evaluate(None, None) == quantize(1.5, 6.8)
        assert _grammar.expression.parseString(
            "quantize(6.8, 1.2)")[0].evaluate(None, None) == quantize(6.8, 1.2)
        assert _grammar.expression.parseString(
            "quantize(10, 5.1)")[0].evaluate(None, None) == quantize(10, 5.1)
        assert _grammar.expression.parseString(
            "quantize(0, {4})")[0].evaluate(None, None) == quantize(0, [4])
        assert _grammar.expression.parseString(
            'quantize(2, {1, 2, "A"})')[0].evaluate(None, None) == quantize(
            2, [1, 2, "A"])
        assert _grammar.expression.parseString(
            "quantize(3, {1, 2, 0.5})")[0].evaluate(None, None) == quantize(
            3, [1, 2, 0.5])
        assert _grammar.expression.parseString(
            "quantize(2.7, {1, 2, 0.5})")[0].evaluate(None, None) == quantize(
            2.7, [1, 2, 0.5])
        assert _grammar.expression.parseString(
            'quantize(3, {1, 2, "A"})')[0].evaluate(None, None) == quantize(
            3, [1, 2, "A"])

    def test_join(self):
        assert _grammar.expression.parseString(
            'join(", ", "a", "b", "c")')[0].evaluate(None, None) == "a, b, c"
        assert _grammar.expression.parseString(
            'join(split("a b c"))')[0].evaluate(None, None) == "abc"
        assert _grammar.expression.parseString(
            'join(";", split("a b c"))')[0].evaluate(None, None) == "a;b;c"

    def test_parse(self):
        classad = "[a = 1; b = 2]"
        assert _grammar.expression.parseString(classad)[0] == parse(classad)
