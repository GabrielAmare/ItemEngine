from typing import Iterator

from .. import *
from .items import *

__all__ = ["charset", "string", "make_characters", "make_branch_set"]


def charset(s: str) -> CharG:
    """convert a str into a Group"""
    return CharG(frozenset(map(CharI, s)))


def string(s: str) -> All:
    """Make a Rule that matches the specified string ``s``"""
    return All(tuple(charset(c).inc() for c in s))


def make_characters(text: str, eof: bool = False) -> Iterator[Char]:
    """This function generates a Char stream"""
    index = -1
    for index, char in enumerate(text):
        yield Char.make(index, char)

    if eof:
        yield Char.EOF(index + 1)


def make_branch_set(*branches: Branch) -> BranchSet:
    return BranchSet(frozenset(branches))
