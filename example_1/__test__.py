# THIS MODULE HAVE BEEN GENERATED AUTOMATICALLY, DO NOT MODIFY MANUALLY
from typing import List

from item_engine.textbase import *

PATH_LIST = ['example_1']

__all__ = ['run']

try:
    __import__(name='spec', fromlist=PATH_LIST).engine.build(allow_overwrite=True)

except ImportError:
    raise Exception("[TEST GENERATION] : engine build failure !")

try:
    from example_1.engine import parse
    from example_1.engine.materials import *

except ImportError:
    raise Exception("[TEST GENERATION] : generated code failure !")


def get(text: str):
    *results, eof = list(parse(make_characters(text, eof=True)))
    return [build(result) for result in results if result.at == 0 and result.to == eof.to]

def test(text: str, expected: List[Element]):
    result = get(text)
    assert expected == result, f"\ntext = {text!r}\nexpected = {expected!r}\nresult   = {result!r}"


def run():
    test('x', [
        
    ])
    test('abc', [
        
    ])
    test('1', [
        
    ])
    test('123', [
        
    ])
    test('1.', [
        
    ])
    test('.2', [
        
    ])
    test('1.2', [
        
    ])
    test('12.', [
        
    ])
    test('.12', [
        
    ])
    test('12.34', [
        
    ])
    test('+', [
        
    ])
    test('*', [
        
    ])
    test('/', [
        
    ])
    test('-', [
        
    ])
    test('=', [
        
    ])


if __name__ == '__main__':
    run()
