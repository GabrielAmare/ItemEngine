from .lexer import lexer
from .materials import *
from .parser import parser
from item_engine.textbase.items.chars import Char
from item_engine.textbase.items.lemmas import Lemma
from typing import Iterator


__all__ = ['parse']


def parse(src: Iterator[Char]) -> Iterator[Lemma]:
    return parser(lexer(src))
