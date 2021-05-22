import os
from item_engine.textbase import make_characters

try:
    from example_1.test_pckg.make import engine

    engine.build(allow_overwrite=True)

except ImportError:
    raise Exception("[TEST GENERATION] : engine build failure !")

try:
    from example_1.test_pckg.engine import parse

except ImportError:
    raise Exception("[TEST GENERATION] : generated code failure !")


def get(text: str):
    return parse(make_characters(text, eof=True))


def generate(*inputs: str) -> str:
    tests = "\n".join(f"    test({text!r}, {list(get(text))!r})" for text in inputs)
    return f"""from item_engine.textbase import make_characters, Token

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
    assert expected == result, f"\\ntext = {{text!r}}\\nexpected = {{expected!r}}\\nresult = {{result!r}}"


def main():
{tests}


if __name__ == '__main__':
    main()
"""


def main():
    content = generate(
        'x',
        '1',
        'abc',
        '123',
        '+',
        '*',
        '/',
        '-',
        '=',
        '1.',
        '.2',
        '1.2',
        '12.',
        '.12',
        '12.34',
    )
    with open('test_preview.py', mode='w', encoding='utf-8') as file:
        file.write(content)
    try:
        test_preview = __import__(name="test_preview", fromlist=["example_1", "test_pack"])

        test_preview.main()

        with open('test.py', mode='w', encoding='utf-8') as file:
            file.write(content)

    finally:
        if os.path.exists('test_preview.py'):
            os.remove('test_preview.py')



if __name__ == '__main__':
    main()
