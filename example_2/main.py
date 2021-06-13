from typing import List, Iterator, TypeVar, Tuple, Dict

from example_2.spec import engine

engine.build(allow_overwrite=True)

from example_2.engine import parse
from example_2.engine.lexer import lexer_propagator
from example_2.engine.parser import parser_propagator
from example_2.engine.materials import build

# from item_engine.textbase.generators import tokenizer_wrapper, lemmatizer_wrapper
from item_engine.textbase.items import Token
from item_engine import Element, INDEX


def value_ignore(skips: List[str]):
    def step(src: Iterator[Token]) -> Iterator[Token]:
        c_at: int = 0
        for old in src:
            assert c_at == old.at, 'elements of source must be consecutive'
            if old.value not in skips:
                yield old
            c_at = old.to

    return step


E = TypeVar("E", bound=Element)


def is_oes(msg: str = ""):
    def check(src: Iterator[E]) -> Iterator[E]:
        c_at: int = 0
        for old in src:
            assert c_at <= old.at, 'elements of source must be ordered. {!r}'.format(msg)
            yield old
            c_at = old.to

    return check


def is_ces(msg: str = ""):
    def check(src: Iterator[E]) -> Iterator[E]:
        c_at: int = 0
        for old in src:
            assert c_at == old.at, 'elements of source must be consecutive. {!r}'.format(msg)
            yield old
            c_at = old.to

    return check


def oes_to_ces(src: Iterator[Token]) -> Iterator[Token]:
    pos: int = 0
    for old in src:
        yield old.replace(at=pos, to=pos + 1)
        pos += 1


def config_match(a, b):
    return all(a.get(k) == v for k, v in b.items())


def config_reassign(assigns: List[Tuple[dict, dict]]):
    def step(src: Iterator[E]) -> Iterator[E]:
        for old in src:
            for at, to in assigns:
                if config_match(old.__dict__, at):
                    yield old.replace(**to)
                    break
            else:
                yield old

    return step


def keep_max_to(src: Iterator[E]) -> Iterator[E]:
    to: int = 0
    res: List[E] = []
    for old in src:
        if old.to > to:
            to = old.to
            res = [old]
        elif old.to == to:
            res.append(old)

    yield from res


def keep_min_at(src: Iterator[E]) -> Iterator[E]:
    data: Dict[INDEX, Tuple[INDEX, List[E]]] = {}
    for old in src:
        if old.to in data:
            at, olds = data[old.to]
            if old.at < at:
                data[old.to] = (old.at, [old])
            elif old.at == at:
                olds.append(old)
        else:
            data[old.to] = (old.at, [old])

    for to in sorted(data):
        yield from data[to][1]


def starting_at_0(src: Iterator[E]) -> Iterator[E]:
    for old in src:
        if old.at == 0:
            yield old


def chain(*funcs):
    def f(arg):
        for func in funcs:
            arg = func(arg)
        return arg

    return f


lexer = chain(
    is_ces('tokenizer 1'),
    tokenizer_wrapper(lexer_propagator),
    is_ces('tokenizer 2'),
    value_ignore(["WHITESPACE"]),
    is_oes('tokenizer 3'),
    oes_to_ces,
    is_ces('tokenizer 4'),
    config_reassign([
        (dict(value="VAR", content="as"), dict(value="AS")),
        (dict(value="VAR", content="in"), dict(value="IN")),
        (dict(value="VAR", content="match"), dict(value="MATCH")),
    ]),
    is_ces('tokenizer 5'),
)
parser = chain(
    # is_ces('lemmatizer 1'),
    lemmatizer_wrapper(parser_propagator),
    starting_at_0,
    keep_max_to,
    # keep_min_at
)

from item_engine.textbase import make_characters, rt_tokens, rt_lemmas, Token

from tools37 import ReprTable, Console

console = Console(show_count=False, show_times=False)


def get(text: str):
    return parse(make_characters(text, eof=True))


def builder(lemmas):
    try:
        *lemmas, eof = lemmas
        return [build(lemma) for lemma in lemmas if lemma.at == 0 and lemma.to == eof.to]
    except:
        return []


if __name__ == '__main__':
    from item_engine.graphics import App

    app = App(
        tokenizer=lexer,
        lemmatizer=parser,
        builder=builder,
        default_text="""
Match = '{' {VAR !name} '}'
MatchAs = '{' {VAR !name} ' !' {VAR !key} '}'
MatchIn = '{' {VAR !name} ' *' {VAR !key} '}'
Literal = {STR !content}
And = ' '.{S2 *childs}
Or = ' | '.{S1 *childs}
Operator = {VAR !name} ' = ' {S0 !rule}
Grammar = '\n'.{Operator *operators}
Group = {VAR !name} ' > ' ' | '.{VAR *args}
S2 > Literal | Match | MatchAs | MatchIn | Enum | Optional | Repeat
S1 > S2 | And
S0 > S1 | Or
""".strip(),
        show_lemmas=True
    )

    app.mainloop()