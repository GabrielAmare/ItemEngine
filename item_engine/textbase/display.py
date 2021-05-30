from typing import Iterator
from tools37 import ReprTable
from .items import Token, Lemma

__all__ = ["rt_tokens", "rt_lemmas"]


def rt_tokens(tokens: Iterator[Token]) -> ReprTable:
    return ReprTable.from_items(tokens, {
        "span": lambda token: repr(token.span),
        "value": lambda token: str(token.value),
        "content": lambda token: repr(token.content)
    })


def rt_lemmas(lemmas: Iterator[Lemma]) -> ReprTable:
    return ReprTable.from_items(lemmas, {
        "span": lambda lemma: repr(lemma.span),
        "value": lambda lemma: str(lemma.value),
        "childs": lambda lemma: str(lemma)
    })
