from __future__ import annotations

from typing import Union, TypeVar, Tuple, Hashable

from item_engine import Element, INCLUDE, CASE, EXCLUDE, INDEX, STATE
from .tokens import Token


class HashableDict(dict):
    def __hash__(self):
        return hash((type(self), tuple(sorted(self.items(), key=lambda item: item[0]))))

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__()})"


E = TypeVar("E", bound=Element)

__all__ = ["Lemma", "HashableDict"]


class Lemma(Element):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return (*super().__args__, self.data)

    def __init__(self, at: INDEX, to: INDEX, value: STATE, data: dict = None, _at: INDEX = None, _to: INDEX = None):
        super().__init__(at, to, value, _at, _to)
        if data is None:
            data = {}
        self.data: HashableDict = HashableDict(data)

    def __str__(self):
        childs = []
        for k, v in self.data.items():
            if isinstance(v, list):
                for i, e in enumerate(v):
                    childs.append(f'{k!s}[{i!s}]={e!s}')
            else:
                childs.append(f'{k!s}={v!s}')
        body = '\n'.join(childs)
        return str(self.value) + '(\n' + '\n'.join('    ' + l for l in body.split('\n')) + '\n)'

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"at={self.at!r}, " \
               f"to={self.to!r}, " \
               f"value={self.value!r}, " \
               f"_at={self._at!r}, " \
               f"_to={self._to!r}," \
               f"data={self.data!r}" \
               f")"

    def develop(self: E, case: CASE, item: Union[Token, Lemma]) -> E:
        action, value = case
        data = HashableDict(self.data)
        if action == INCLUDE:
            return self.__class__(
                at=self.at,
                to=item.to,
                value=value,
                data=data,
                _at=self._at,
                _to=item._to,
            )
        elif action == EXCLUDE:
            return self.__class__(
                at=self.at,
                to=self.to,
                value=value,
                data=data,
                _at=self._at,
                _to=self._to,
            )
        elif ":" in action:
            action, name = action.split(":", 1)
            if action == "as":
                data[name] = item
            elif action == "in":
                data.setdefault(name, [])
                data[name].append(item)
            else:
                raise ValueError(name)
            return self.__class__(
                at=self.at,
                to=item.to,
                value=value,
                data=data,
                _at=self._at,
                _to=item._to,
            )
        else:
            raise ValueError(action)
