from item_engine.textbase import make_characters, Token

try:
    from example_1.test_pckg.make import engine
    engine.build(allow_overwrite=True)

except ImportError:
    raise Exception("[TEST APPLICATION] : engine build failure !")

try:
    from example_1.test_pckg.engine import parse

except ImportError:
    raise Exception("[TEST APPLICATION] : generated code failure !")


def get(text: str):
    return parse(make_characters(text, eof=True))


def test(text: str, expected):
    result = list(get(text))
    assert expected == result, f"\ntext = {text!r}\nexpected = {expected!r}\nresult = {result!r}"


def main():
    test('x', [Token(at=0, to=1, value='VAR', content='x'), Token(at=1, to=1, value='EOF', content='')])
    test('1', [Token(at=0, to=1, value='INT', content='1'), Token(at=1, to=1, value='EOF', content='')])
    test('abc', [Token(at=0, to=1, value='VAR', content='abc'), Token(at=1, to=1, value='EOF', content='')])
    test('123', [Token(at=0, to=1, value='INT', content='123'), Token(at=1, to=1, value='EOF', content='')])
    test('+', [Token(at=0, to=1, value='PLUS', content='+'), Token(at=1, to=1, value='EOF', content='')])
    test('*', [Token(at=0, to=1, value='STAR', content='*'), Token(at=1, to=1, value='EOF', content='')])
    test('/', [Token(at=0, to=1, value='SLASH', content='/'), Token(at=1, to=1, value='EOF', content='')])
    test('-', [Token(at=0, to=1, value='DASH', content='-'), Token(at=1, to=1, value='EOF', content='')])
    test('=', [Token(at=0, to=1, value='EQUAL', content='='), Token(at=1, to=1, value='EOF', content='')])
    test('1.', [Token(at=0, to=1, value='FLOAT', content='1.'), Token(at=1, to=1, value='EOF', content='')])
    test('.2', [Token(at=0, to=1, value='FLOAT', content='.2'), Token(at=1, to=1, value='EOF', content='')])
    test('1.2', [Token(at=0, to=1, value='FLOAT', content='1.2'), Token(at=1, to=1, value='EOF', content='')])
    test('12.', [Token(at=0, to=1, value='FLOAT', content='12.'), Token(at=1, to=1, value='EOF', content='')])
    test('.12', [Token(at=0, to=1, value='FLOAT', content='.12'), Token(at=1, to=1, value='EOF', content='')])
    test('12.34', [Token(at=0, to=1, value='FLOAT', content='12.34'), Token(at=1, to=1, value='EOF', content='')])


if __name__ == '__main__':
    main()
