from typing import Iterator, Union
from tools37 import ReprTable
from .items import Token, Lemma

__all__ = ["rt_tokens", "rt_lemmas"]


def rt_tokens(tokens: Iterator[Token]) -> ReprTable:
    return ReprTable.from_items(tokens, {
        "span": lambda token: repr(token.span),
        "value": lambda token: str(token.value),
        "content": lambda token: repr(token.content)
    })


def get_level(obj: Union[Token, Lemma]):
    if isinstance(obj, Token):
        return 0
    elif isinstance(obj, Lemma):
        level = 0
        for v in obj.data.values():
            if isinstance(v, list):
                for e in v:
                    level = max(level, get_level(e))
            else:
                level = max(level, get_level(v))
        return level + 1
    else:
        return -1


def rt_lemmas(lemmas: Iterator[Lemma]) -> ReprTable:
    return ReprTable.from_items(lemmas, {
        "span": lambda lemma: repr(lemma.span),
        "level": lambda lemma: repr(get_level(lemma)),
        "value": lambda lemma: str(lemma.value),
        "childs": lambda lemma: str(lemma)
    })
