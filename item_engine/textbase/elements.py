from __future__ import annotations
from dataclasses import dataclass, field
from typing import TypeVar, Union

from .. import Element, INDEX, T_STATE, INCLUDE, EXCLUDE, CASE

__all__ = ["Char", "Token", "Lemma"]


class HashableDict(dict):
    def __hash__(self):
        return hash((type(self), tuple(sorted(self.items(), key=lambda item: item[0]))))


E = TypeVar("E", bound=Element)


@dataclass(frozen=True, order=True)
class Char(Element):
    @classmethod
    def make(cls, at: INDEX, char: str):
        return Char(at=at, to=at + 1, value=T_STATE(char))

    def develop(self: E, case: CASE, item: Element) -> E:
        raise Exception


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
