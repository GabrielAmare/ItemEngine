# THIS MODULE HAVE BEEN GENERATED AUTOMATICALLY, DO NOT MODIFY MANUALLY
from typing import List

from item_engine.textbase import *

PATH_LIST = ['example_2']

__all__ = ['run']

try:
    __import__(name='spec', fromlist=PATH_LIST).engine.build(allow_overwrite=True)

except ImportError:
    raise Exception("[TEST GENERATION] : engine build failure !")

try:
    from example_2.engine import parse
    from example_2.engine.materials import *

except ImportError:
    raise Exception("[TEST GENERATION] : generated code failure !")


def get(text: str):
    *results, eof = list(parse(make_characters(text, eof=True)))
    return [build(result) for result in results if result.at == 0 and result.to == eof.to]

def test(text: str, expected: list):
    result = get(text)
    assert expected == result, f"\ntext = {text!r}\nexpected = {expected!r}\nresult   = {result!r}"


def run():
    test('{X !x}', [
        MatchAs('X', 'x')
    ])
    test('{X *x}', [
        MatchIn('X', 'x')
    ])
    test('{X !x} {Y !y}', [
        And(MatchAs('X', 'x'), MatchAs('Y', 'y'))
    ])
    test('{X !x} | {Y !y}', [
        Or(MatchAs('X', 'x'), MatchAs('Y', 'y'))
    ])
    test("'literal'", [
        Literal("'literal'")
    ])
    test("'sep'.{I *i}", [
        Enum(Literal("'sep'"), MatchIn('I', 'i'))
    ])
    test('{X !x} {Y !y} | {Z !z} {T !t}', [
        Or(And(MatchAs('X', 'x'), MatchAs('Y', 'y')), And(MatchAs('Z', 'z'), MatchAs('T', 't')))
    ])
    test("Add = {Expr !left} ' + ' {Term !right}", [
        Operator('Add', And(And(MatchAs('Expr', 'left'), Literal("' + '")), MatchAs('Term', 'right')))
    ])
    test("Mul = {Expr !left} ' * ' {Term !right} | {Expr !left} {Term !right}", [
        Operator('Mul', Or(And(And(MatchAs('Expr', 'left'), Literal("' * '")), MatchAs('Term', 'right')), And(MatchAs('Expr', 'left'), MatchAs('Term', 'right'))))
    ])


if __name__ == '__main__':
    run()
