import os
from typing import List, Iterator

from item_engine.textbase import make_characters

__all__ = ["generate_tests"]


def generate_tests(pckg: str,
                   inputs: List[str],
                   __test__: str = '__test__',
                   spec: str = 'spec',
                   __test_preview__: str = '__test_preview__',
                   remove_preview: bool = True
                   ):
    PATH_LIST = pckg.split('.')

    try:
        __import__(name=spec, fromlist=PATH_LIST).engine.build(allow_overwrite=True)

    except ImportError:
        raise Exception("[TEST GENERATION] : engine build failure !")

    try:
        engine_module = __import__(name="engine", fromlist=PATH_LIST)
        parse = engine_module.parse
        build = engine_module.build

    except ImportError:
        raise Exception("[TEST GENERATION] : generated code failure !")

    def get(text: str):
        *results, eof = list(parse(make_characters(text, eof=True)))
        return [build(result) for result in results if result.at == 0 and result.to == eof.to]

    def indent(s: str) -> str:
        return '\n'.join('    ' + line for line in s.split('\n'))

    def indent_result(result: Iterator):
        return "[\n" + indent(",\n".join(map(repr, result))) + "\n]"

    tests = indent("\n".join(f"test({text!r}, {indent_result(list(get(text)))!s})" for text in inputs))

    content = f"""# THIS MODULE HAVE BEEN GENERATED AUTOMATICALLY, DO NOT MODIFY MANUALLY
from typing import List

from item_engine.textbase import *

PATH_LIST = {PATH_LIST!r}

__all__ = ['run']

try:
    __import__(name={spec!r}, fromlist=PATH_LIST).engine.build(allow_overwrite=True)

except ImportError:
    raise Exception("[TEST GENERATION] : engine build failure !")

try:
    from {'.'.join(PATH_LIST)}.engine import parse
    from {'.'.join(PATH_LIST)}.engine.materials import *

except ImportError:
    raise Exception("[TEST GENERATION] : generated code failure !")


def get(text: str):
    *results, eof = list(parse(make_characters(text, eof=True)))
    return [build(result) for result in results if result.at == 0 and result.to == eof.to]

def test(text: str, expected: List[Element]):
    result = get(text)
    assert expected == result, f"\\ntext = {{text!r}}\\nexpected = {{expected!r}}\\nresult   = {{result!r}}"


def run():
{tests}


if __name__ == '__main__':
    run()
"""
    try:
        with open(__test_preview__ + '.py', mode='w', encoding='utf-8') as file:
            file.write(content)

        try:
            __import__(name=__test_preview__, fromlist=PATH_LIST).run()
        except Exception as e:
            raise Exception("[TEST GENERATION] : preview error", e)

        with open(__test__ + '.py', mode='w', encoding='utf-8') as file:
            file.write(content)

    finally:
        if remove_preview:
            if os.path.exists(__test_preview__ + '.py'):
                os.remove(__test_preview__ + '.py')
