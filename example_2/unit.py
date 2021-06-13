from example_2.engine.lexer import lexer

from item_engine.textbase import make_characters, rt_tokens


def main():
    while True:
        text = input('input : ')
        if not text:
            break

        chars = list(make_characters(text, eof=True))
        tokens = list(lexer(chars))

        print(rt_tokens(tokens))


if __name__ == '__main__':
    main()
