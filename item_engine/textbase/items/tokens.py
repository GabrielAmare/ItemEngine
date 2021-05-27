from __future__ import annotations

from typing import Union, List, TypeVar, Tuple, Hashable, FrozenSet

from python_generator import VAR, CONDITION, TUPLE

from item_engine import Match, Element, INCLUDE, CASE, EXCLUDE, INDEX, STATE
from .base import BaseItem, BaseGroup
from .chars import Char

E = TypeVar("E", bound=Element)

__all__ = ["TokenI", "TokenG", "Token"]


class TokenG(BaseGroup):
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


class TokenI(BaseItem):
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


class Token(Element):
    def __str__(self):
        return repr(self.content)

    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return (*super().__args__, self.content)

    def __init__(self, at: INDEX, to: INDEX, value: STATE, content: str = "", _at: INDEX = None, _to: INDEX = None):
        super().__init__(at, to, value, _at, _to)
        self.content: str = content

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"at={self.at!r}, " \
               f"to={self.to!r}, " \
               f"value={self.value!r}, " \
               f"_at={self._at!r}, " \
               f"_to={self._to!r}" \
               f"content={self.content!r}, " \
               f")"

    def develop(self: E, case: CASE, item: Char) -> E:
        action, value = case
        if action == INCLUDE:
            return self.__class__(
                at=self.at,
                to=item.to,
                value=value,
                content=self.content + str(item.value),
                _at=self._at,
                _to=item._to
            )
        elif action == EXCLUDE:
            return self.__class__(
                at=self.at,
                to=self.to,
                value=value,
                content=self.content,
                _at=self._at,
                _to=self._to
            )
        else:
            raise ValueError(action)
