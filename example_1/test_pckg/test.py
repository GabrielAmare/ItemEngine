from example_1.test_pckg.make import engine

engine.build(allow_overwrite=True)

from example_1.test_pckg.engine import parse
from item_engine.textbase import make_characters, Token


def get(text: str):
    return parse(make_characters(text, eof=True))


def test(text: str, expected):
    result = list(get(text))
    assert expected == result, f"\ntext = {text!r}\nexpected = {expected!r}\nresult = {result!r}"
    # print(f"    test({text!r}, {result!r})")


def main():
    test('myVariable', [Token(at=0, to=10, value='VAR', content='myVariable'), Token(at=10, to=10, value='EOF', content='')])
    test('12345', [Token(at=0, to=5, value='INT', content='12345'), Token(at=5, to=5, value='EOF', content='')])
    test('12.34', [Token(at=0, to=5, value='FLOAT', content='12.34'), Token(at=5, to=5, value='EOF', content='')])
    test('1', [Token(at=0, to=1, value='INT', content='1'), Token(at=1, to=1, value='EOF', content='')])
    test('.1', [Token(at=0, to=2, value='FLOAT', content='.1'), Token(at=2, to=2, value='EOF', content='')])
    test('1.', [Token(at=0, to=2, value='FLOAT', content='1.'), Token(at=2, to=2, value='EOF', content='')])


if __name__ == '__main__':
    main()
