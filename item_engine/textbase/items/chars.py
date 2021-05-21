from __future__ import annotations
from dataclasses import dataclass
from typing import TypeVar

from item_engine import Item, Group, Match, Element, T_STATE, CASE, INDEX
from python_generator import VAR, CONDITION

E = TypeVar("E", bound=Element)

__all__ = ["Char", "CharI", "CharG"]


class CharG(Group):
    @property
    def items_str(self) -> str:
        s = ''.join(sorted(repr(str(item))[1:-1] for item in self.items))
        s = s.replace('0123456789', r'\d')
        return repr(s).replace('\\\\', '\\')

    def condition(self, item: VAR) -> CONDITION:
        expr = ''.join(sorted(map(str, self.items)))
        return self.code_factory(item.GETATTR("value"), repr(expr))

    def match(self, action: str) -> Match:
        return Match(self, action)


@dataclass(frozen=True, order=True)
class CharI(Item):
    char: str

    def __str__(self):
        return self.char

    @property
    def as_group(self) -> CharG:
        return CharG(frozenset({self}))


@dataclass(frozen=True, order=True)
class Char(Element):
    @classmethod
    def make(cls, at: INDEX, char: str):
        return Char(at=at, to=at + 1, value=T_STATE(char))

    def develop(self: E, case: CASE, item: Element) -> E:
        raise Exception
