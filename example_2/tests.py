from typing import Iterator, Set, TypeVar

from example_2.engine.lexer import _lexer
from example_2.engine.parser import _parser

from item_engine.textbase import Char, Token, Lemma, make_characters, rt_tokens, rt_lemmas, INDEX, Element

from item_engine.ParserModel import ParserModel


def main():
    tokenizer = ParserModel(
        input_cls=Char,
        output_cls=Token,
        propagator=lambda cur, old: [_lexer(cur, old)],
        keep_longest=True
    )
    lemmatizer = ParserModel(
        input_cls=Token,
        output_cls=Lemma,
        propagator=_parser,
        reflexive=True,
        keep_longest=True
    )

    from item_engine.ParserModel import ParserInstance

    tokenizer = ParserInstance(tokenizer)
    lemmatizer = ParserInstance(lemmatizer)

    chars = list(make_characters("Add = {TERM !left}' + '{EXPR !right}"))

    def ignore_whitespace(src: Iterator[Token]) -> Iterator[Token]:
        pos = 0
        for old in src:
            if old.value == 'WHITESPACE':
                continue

            new = old.replace(at=pos, to=pos + 1)
            pos += 1
            yield new

    def keep_complete(src: Iterator[Lemma]) -> Iterator[Lemma]:
        kept = []
        for old in src:
            if old.value == 'EOF':
                for new in kept:
                    if new.to == old.at:
                        yield new
                break

            if old.at == 0:
                kept.append(old)

    def chain(*funcs):
        def f(arg):
            for func in funcs:
                arg = func(arg)
            return arg

        return f

    full_tokenizer = chain(
        tokenizer,
        ignore_whitespace,
        list
    )

    full_lemmatizer = chain(
        tokenizer,
        ignore_whitespace,
        lemmatizer,
        keep_complete,
        list
    )

    tokens = full_tokenizer(chars)

    lemmas = full_lemmatizer(chars)

    print(rt_tokens(tokens))
    print(rt_lemmas(lemmas))

    # print(rt_lemmas(lemmas))

    # # data = [['to'], ['CTV-T'], ['CTD-NT'], ['CTD-T']]
    # data = [['to', 'CTV-T', 'CTD-NT', 'CTD-T']]
    #
    # for to, curs in tokenizer.curs.items():
    #     for char in chars:
    #         if char.to == to:
    #             break
    #     else:
    #         char = '?'
    #
    #     ctd_t = [token for token in tokens if token.to == to]
    #     data.append([
    #         str(to),
    #         str(char),
    #         str(rt_tokens(curs)),
    #         str(rt_tokens(ctd_t)) if ctd_t else ''
    #     ])
    #     # data[0].append(str(to))
    #     # data[1].append(str(char))
    #     # data[2].append(str(rt_tokens(curs)))
    #     # data[3].append(str(rt_tokens(ctd_t)) if ctd_t else '')
    #
    # from tools37 import ReprTable
    # print(ReprTable(data))


if __name__ == '__main__':
    main()
