from .lexer import lexer
from .materials import *
from item_engine.textbase.items.chars import Char
from item_engine.textbase.items.tokens import Token
from typing import Iterator


__all__ = ['parse']


def parse(src: Iterator[Char]) -> Iterator[Token]:
    return lexer(src)
