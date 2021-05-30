from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar, Tuple, Hashable, FrozenSet

from python_generator import VAR, CONDITION

from item_engine import Match, Element, T_STATE, CASE, INDEX, EOF
from .base import BaseItem, BaseGroup

E = TypeVar("E", bound=Element)

__all__ = ["Char", "CharI", "CharG"]


class CharG(BaseGroup):
    items: FrozenSet[CharI]

    @property
    def items_str(self) -> str:
        s = ''.join(sorted(repr(item.char)[1:-1] for item in self.items))
        s = s.replace('0123456789', r'0-9').replace('\t', '\\t').replace('\n', '\\n')
        return repr(s)

    def condition(self, item: VAR) -> CONDITION:
        expr = ''.join(sorted(map(str, self.items)))
        return self.code_factory(item.GETATTR("value"), repr(expr))

    def match(self, action: str) -> Match:
        return Match(self, action)


class CharI(BaseItem):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), self.char

    def __init__(self, char: str):
        assert len(char) == 1 or char == EOF
        self.char: str = char

    def __repr__(self):
        return f"{self.__class__.__name__}({self.char!r})"

    def __str__(self):
        return self.char

    @property
    def as_group(self) -> CharG:
        return CharG(frozenset({self}))


class Char(Element):
    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"at={self.at!r}, " \
               f"to={self.to!r}, " \
               f"value={self.value!r}, " \
               f"_at={self._at!r}, " \
               f"_to={self._to!r}" \
               f")"

    @classmethod
    def make(cls, at: INDEX, char: str):
        return Char(at=at, to=at + 1, value=T_STATE(char))

    def develop(self: E, case: CASE, item: Element) -> E:
        raise Exception
