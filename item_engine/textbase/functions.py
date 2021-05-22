from typing import Iterator

from item_engine import *
from .items import *

__all__ = ["charset", "string", "make_characters"]


def charset(s: str) -> CharG:
    """convert a str into a Group"""
    return CharG(frozenset(map(CharI, s)))


def string(s: str) -> Rule:
    """Make a Rule that matches the specified string ``s``"""
    return All.join(map(include, map(charset, s)))


def make_characters(text: str, eof: bool = False) -> Iterator[Char]:
    """This function generates a Char stream"""
    index = -1
    for index, char in enumerate(text):
        yield Char.make(index, char)

    if eof:
        yield Char.EOF(index + 1)
