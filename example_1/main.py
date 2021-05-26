from example_1.spec import engine

engine.build(allow_overwrite=True)

from example_1.engine import parse
from item_engine.textbase import make_characters, rt_tokens


def get(text: str):
    return parse(make_characters(text, eof=True))


def main():
    while True:
        text = input("enter your text : ")
        if not text:
            break

        print(rt_tokens(get(text)))


if __name__ == '__main__':
    main()
