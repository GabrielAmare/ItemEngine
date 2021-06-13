from __future__ import annotations

from typing import Tuple, Hashable

from .constants import T_STATE, INDEX, STATE, CASE, NT_STATE, EOF
from .utils import ArgsHashed

__all__ = [
    "Element", "IE_SyntaxError",
]


class Element(ArgsHashed):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), self.at, self.to, self.value

    def replace(self, **cfg):
        data = self.__dict__.copy()
        data.update(**cfg)
        return self.__class__(**data)

    @classmethod
    def after(cls, element: Element, value: STATE = 0) -> Element:
        """Creates a new Element of ``cls`` at the end of this one"""
        return cls(
            at=element.to,
            to=element.to,
            value=value,
            _at=element._to,
            _to=element._to
        )

    def __init__(self, at: INDEX, to: INDEX, value: STATE, _at: INDEX = None, _to: INDEX = None):
        self.at: INDEX = at
        self.to: INDEX = to
        self.value: STATE = value
        self._at: INDEX = at if _at is None else _at
        self._to: INDEX = to if _to is None else _to

    @property
    def span(self) -> Tuple[INDEX, INDEX]:
        return self.at, self.to

    def lt(self, other: Element) -> bool:
        return self.to < other.at

    def le(self, other: Element) -> bool:
        return self.to <= other.at

    def gt(self, other: Element) -> bool:
        return self.to > other.at

    def ge(self, other: Element) -> bool:
        return self.to >= other.at

    def eq(self, other: Element) -> bool:
        return self.at == other.at and self.to == other.to

    def ne(self, other: Element) -> bool:
        return self.at != other.at or self.to != other.to

    def ol(self, other: Element) -> bool:
        if other.at < self.to:
            return other.to > self.at
        elif other.at > self.to:
            return other.to < self.at
        else:
            return False

    @classmethod
    def EOF(cls, at: INDEX):
        return cls(at=at, to=at, value=T_STATE(EOF))

    @classmethod
    def cursor(cls, at: INDEX) -> Element:
        return cls(at=at, to=at, value=0)

    def develop(self, case: CASE, item: Element) -> Element:
        raise NotImplementedError

    def eof(self):
        return self.__class__.EOF(self.to)

    @property
    def is_eof(self):
        return self.value == EOF

    @property
    def is_non_terminal(self) -> bool:
        return isinstance(self.value, NT_STATE)

    @property
    def is_terminal(self) -> bool:
        return isinstance(self.value, T_STATE)

    @property
    def is_valid(self) -> bool:
        return self.is_terminal and not self.value.startswith('!')

    @property
    def is_error(self) -> bool:
        return self.is_terminal and self.value.startswith('!')


class IE_SyntaxError(Exception):
    def __init__(self, new: Element, *args, **kwargs):
        self.new: Element = new
        self.args = args
        self.kwargs = kwargs
