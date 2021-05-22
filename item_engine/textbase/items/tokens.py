from __future__ import annotations
from dataclasses import dataclass
from typing import Union, List, TypeVar, Tuple, Hashable, FrozenSet
from item_engine import Item, Group, Match, Element, INCLUDE, CASE, EXCLUDE
from python_generator import VAR, CONDITION, TUPLE
from .chars import Char

E = TypeVar("E", bound=Element)

__all__ = ["TokenI", "TokenG", "Token"]


class TokenG(Group):
    items: FrozenSet[TokenI]

    @property
    def items_str(self) -> str:
        return '\n'.join(map(repr, sorted([item.name for item in self.items])))

    def condition(self, item: VAR) -> CONDITION:
        items = tuple(sorted(map(str, self.items)))
        grp = items[0] if len(self.items) == 1 else TUPLE(items)
        return self.code_factory(item.GETATTR("value"), grp)

    def match(self, action: str) -> Match:
        return Match(self, action)

    @classmethod
    def grp(cls, names: Union[str, List[str]]) -> TokenG:
        if isinstance(names, str):
            names = [names]
        return cls(frozenset(map(TokenI, names)))


class TokenI(Item):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), self.name

    def __init__(self, name: str):
        self.name: str = name

    def __str__(self):
        return repr(self.name)

    @property
    def as_group(self) -> TokenG:
        return TokenG(frozenset({self}))


@dataclass(frozen=True, order=True)
class Token(Element):
    content: str = ""

    def __str__(self):
        return repr(self.content)

    def develop(self: E, case: CASE, item: Char) -> E:
        action, value = case
        if action == INCLUDE:
            return self.__class__(at=self.at, to=item.to, value=value, content=self.content + str(item.value))
        elif action == EXCLUDE:
            return self.__class__(at=self.at, to=self.to, value=value, content=self.content)
        else:
            raise ValueError(action)
