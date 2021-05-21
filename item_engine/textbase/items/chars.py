from __future__ import annotations
from dataclasses import dataclass

from item_engine import Item, Group, Match
import python_generator as pg

__all__ = ["CharI", "CharG"]


class CharG(Group):
    @property
    def items_str(self) -> str:
        s = ''.join(sorted(repr(str(item))[1:-1] for item in self.items))
        s = s.replace('0123456789', r'\d')
        return repr(s).replace('\\\\', '\\')

    def condition(self, item: pg.VAR) -> pg.CONDITION:
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
