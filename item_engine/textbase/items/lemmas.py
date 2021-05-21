from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union, TypeVar
from item_engine import Element, INCLUDE, CASE, EXCLUDE
from .tokens import Token


class HashableDict(dict):
    def __hash__(self):
        return hash((type(self), tuple(sorted(self.items(), key=lambda item: item[0]))))


E = TypeVar("E", bound=Element)

__all__ = ["Lemma"]


@dataclass(frozen=True, order=True)
class Lemma(Element):
    data: HashableDict = field(default_factory=HashableDict)

    def develop(self: E, case: CASE, item: Union[Token, Lemma]) -> E:
        action, value = case
        data = HashableDict(self.data)
        if action == INCLUDE:
            return self.__class__(at=self.at, to=item.to, value=value, data=data)
        elif action == EXCLUDE:
            return self.__class__(at=self.at, to=self.to, value=value, data=data)
        elif ":" in action:
            action, name = action.split(":", 1)
            if action == "as":
                data[name] = item
            elif action == "in":
                data.setdefault(name, [])
                data[name].append(item)
            else:
                raise ValueError(name)
            return self.__class__(at=self.at, to=item.to, value=value, data=data)
        else:
            raise ValueError(action)
