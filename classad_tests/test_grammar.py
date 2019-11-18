from classad import _grammar, quantize, parse
from classad._classad import ClassAd
from classad._expression import ArithmeticExpression
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
        assert isinstance(result[0], ClassAd)
        keys = result[0].keys()
        assert 10, len(keys)
        assert 35882, keys["Disk"]
        assert 0.1, keys["LoadAvg"]

        classad = """
        Requirements = (Arch == "INTEL") && (OpSys == "LINUX")
        Rank         = TARGET.Memory + TARGET.Mips
        """
        result = parse(classad)
        assert isinstance(result["requirements"], ArithmeticExpression)

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
        old_result = parse(old)
        new_result = parse(new)
        assert old_result == new_result

    def test_quantize(self):
        assert parse("quantize(3, 8)").evaluate() == quantize(HTCInt(3), HTCInt(8))
        assert parse("quantize(3, 2)").evaluate() == quantize(HTCInt(3), HTCInt(2))
        assert parse("quantize(0, 4)").evaluate() == quantize(HTCInt(0), HTCInt(4))
        assert parse("quantize(1.5, 6.8)").evaluate() == quantize(HTCFloat(1.5), HTCFloat(6.8))
        assert parse("quantize(6.8, 1.2)").evaluate() == quantize(HTCFloat(6.8), HTCFloat(1.2))
        assert parse("quantize(10, 5.1)").evaluate() == quantize(HTCInt(10), HTCFloat(5.1))
        assert parse("quantize(0, {4})").evaluate() == quantize(HTCInt(0), HTCList([HTCInt(4)]))
        assert parse('quantize(2, {1, 2, "A"})').evaluate() == quantize(
            HTCInt(2), HTCList([HTCInt(1), HTCInt(2), HTCStr("A")])
        )
        assert parse("quantize(3, {1, 2, 0.5})").evaluate() == quantize(
            HTCInt(3), HTCList([HTCInt(1), HTCInt(2), HTCFloat(0.5)])
        )
        assert parse("quantize(2.7, {1, 2, 0.5})").evaluate() == quantize(
            HTCFloat(2.7), HTCList([HTCInt(1), HTCInt(2), HTCFloat(0.5)])
        )
        assert parse('quantize(3, {1, 2, "A"})').evaluate() == quantize(
            HTCInt(3), HTCList([HTCInt(1), HTCInt(2), HTCStr("A")])
        )

    def test_join(self):
        assert parse('join(", ", "a", "b", "c")').evaluate() == "a, b, c"
        assert parse('join(split("a b c"))').evaluate() == "abc"
        assert parse('join(";", split("a b c"))').evaluate() == "a;b;c"

    def test_parse(self):
        classad = "[a = 1; b = 2]"
        assert _grammar.expression.parseString(classad)[0] == parse(classad)

    def test_example_expressions(self):
        assert parse("(10 == 10)").evaluate()
        assert not parse("(10 == 5)").evaluate()
        assert parse('(10 == "ABC")').evaluate() == Error()
        assert parse('"ABC" == "abc"').evaluate()
        assert parse("(10 == UNDEFINED)").evaluate() == Undefined()
        assert parse("(UNDEFINED == UNDEFINED)").evaluate() == Undefined()

        assert parse("(10 =?= 10)").evaluate()
        assert not parse("(10 =?= 5)").evaluate()
        assert not parse('(10 =?= "ABC")').evaluate()
        assert not parse('"ABC" =?= "abc"').evaluate()
        assert not parse("(10 =?= UNDEFINED)").evaluate()
        assert parse("(UNDEFINED =?= UNDEFINED)").evaluate()

        assert not parse("(10 != 10)").evaluate()
        assert parse("(10 != 5)").evaluate
        assert parse('(10 != "ABC")').evaluate() == Error()
        assert not parse('"ABC" != "abc"').evaluate()
        assert parse("(10 != UNDEFINED)").evaluate() == Undefined()
        assert parse("(UNDEFINED != UNDEFINED)").evaluate() == Undefined()

        assert not parse("(10 =!= 10)").evaluate()
        assert parse("(10 =!= 5)").evaluate()
        assert parse('(10 =!= "ABC")').evaluate()
        assert parse('"ABC" =!= "abc"').evaluate()
        assert parse("(10 =!= UNDEFINED)").evaluate()
        assert not parse("(UNDEFINED =!= UNDEFINED)").evaluate()

        assert parse("10 + undefined").evaluate() == Undefined()
        assert parse("error / 3.14").evaluate() == Error()
        assert parse('10 * "foo"').evaluate() == Error()
        assert parse("17 / 0").evaluate() == Error()

        assert parse("true?10:undefined").evaluate() == 10
        assert parse('false?error:"foo"').evaluate() == "foo"
        assert not parse("undefined is 10").evaluate()
        assert parse("error is error").evaluate()

    def test_aggregates(self):
        result = parse("{ 10, [foo={10}], {17, [bar=3]} }")
        assert len(result) == 3
        assert parse("{10, 17*2, 30}[1]").evaluate() == 34

    def test_attribute_references(self):
        assert parse("[a=1;b=a]").evaluate(key="b") == 1
        assert parse("[a=2;b=[c=1;d=a]]").evaluate(key="b.d") == 2
        assert parse("[a=2;b=[c=1;d=a+f];e=[f=10]]").evaluate(key="b.d") == Undefined()
        assert parse("[a=3;b=[c=1;d=[e=5;f=a+c+e]]]").evaluate(key="b.d.f") == 9
        assert parse("[a=3;b=[a=2;c=1;d=[e=5;f=a+c+e]]]").evaluate(key="b.d.f") == 8
        assert (
            parse("[a=3;b=[a=2;c=1;d=[e=5;f=a+b+c]]]").evaluate(key="b.d.f") == Error()
        )
        assert parse("[a=2;b=[a=1;d=.a]]").evaluate(key="b.d") == 2
        assert parse("[a=3;b=[a=1;d=[a=5;f=a+.a]]]").evaluate(key="b.d.f") == 8
        assert parse("[a=2;b=[c=1;d=.c]]").evaluate(key="b.d") == Undefined()
        assert parse("[a=1;b=[c=5].c]").evaluate(key="b") == 5
        assert parse("[a=1;b=[c=5].a]").evaluate(key="b") == 1
        assert parse("[a=1;b=[a=2;c=[b=.a]];d=.b.c.a]").evaluate(key="d") == 2
        assert parse("[a=1;b=[a=2;c=[b=.a]];d=.b.c.b]").evaluate(key="d") == 1
        assert parse("[a=1;b=[a=2;c=[b=a]];d=.b.c.b]").evaluate(key="d") == 2
        assert parse("[a=1;b=[a=2;c=[b=.a]];d=.a.b.a.b]").evaluate(key="d") == Error()

        assert parse("[a=1;b=[c=2];d=[super=.b]].d.c").evaluate() == 2
        assert parse("[a=1;b=[a=7;c=super.a]]").evaluate(key="b.c") == 1

    def test_circularities(self):
        assert parse("[b=a;a=b].a").evaluate() == Undefined()
        assert parse("[a=[super=.b]; b=[super=.a]].x").evaluate() == Undefined()
