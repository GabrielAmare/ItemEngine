from __future__ import annotations
from dataclasses import dataclass
from typing import Union, List

from item_engine import Item, Group, Match
import python_generator as pg

__all__ = ["TokenI", "TokenG"]


class TokenG(Group):
    @property
    def items_str(self) -> str:
        return '\n'.join(map(repr, sorted([item.name for item in self.items])))

    def condition(self, item: pg.VAR) -> pg.CONDITION:
        items = tuple(sorted(map(str, self.items)))
        grp = items[0] if len(self.items) == 1 else pg.TUPLE(items)
        return self.code_factory(item.GETATTR("value"), grp)

    def match(self, action: str) -> Match:
        return Match(self, action)

    @classmethod
    def grp(cls, names: Union[str, List[str]]) -> TokenG:
        if isinstance(names, str):
            names = [names]
        return cls(frozenset(map(TokenI, names)))


@dataclass(frozen=True, order=True)
class TokenI(Item):
    name: str

    def __str__(self):
        return repr(self.name)

    @property
    def as_group(self) -> TokenG:
        return TokenG(frozenset({self}))
