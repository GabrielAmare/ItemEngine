from __future__ import annotations

from typing import Tuple, List, Hashable

from .constants import T_STATE, INDEX, STATE, CASE, NT_STATE, EOF
from .utils import ArgsHashed

__all__ = ["Element", "OPTIONS", "IE_SyntaxError"]


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
    def __init__(self, cur: Element, old: Element, new: Element):
        self.cur: Element = cur
        self.old: Element = old
        self.new: Element = new


class OPTIONS:
    @staticmethod
    def ordered(elements: List[Element]) -> bool:
        """Return True when elements are in order, it implies that there's no overlapping"""
        return all(a.le(b) for a, b in zip(elements, elements[1:]))

    @staticmethod
    def consecutive(elements: List[Element]) -> bool:
        """Return True when elements are in order and conscutive, it implies that there's no overlapping"""
        return all(a.to == b.at for a, b in zip(elements, elements[1:]))

    @staticmethod
    def ordered_layers(layers: List[List[Element]]) -> bool:
        """Return True when elements from consecutive layers are in order (for all possible pairs)"""
        return all(all(a.le(b) for a in A for b in B) for A, B in zip(layers, layers[1:]))

    @staticmethod
    def simultaneous_end(elements: List[Element]) -> bool:
        return all(a.to == b.to for a in elements for b in elements)

    @staticmethod
    def simultaneous_start(elements: List[Element]) -> bool:
        return all(a.at == b.at for a in elements for b in elements)

    @staticmethod
    def non_overlaping(elements: List[Element]):
        return all(not a.ol(b) for a in elements for b in elements if a is not b)
