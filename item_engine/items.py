from __future__ import annotations

from abc import ABC
from operator import xor
from typing import TypeVar, Tuple, Hashable, Type, Iterable, FrozenSet

from .utils import ArgsHashed
from python_generator import CONDITION, NE, EQ, NOT_IN, IN, VAR

__all__ = ["Item", "Group"]


class Item(ArgsHashed, ABC):
    @property
    def as_group(self) -> Group:
        raise NotImplementedError

    def __or__(self, other: Group) -> Group:
        return self.as_group | other

    __ior__ = __or__

    def __add__(self, other: Item) -> Group:
        return self.as_group + other

    __iadd__ = __add__


E = TypeVar("E", bound=Item)
T = TypeVar("T")


class Group(ArgsHashed):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), self.inverted, tuple(sorted(self.items))

    @classmethod
    def never(cls: Type[T]) -> T:
        """return ∅"""
        return cls(frozenset(), False)

    @classmethod
    def always(cls: Type[T]) -> T:
        """return Ω"""
        return cls(frozenset(), True)

    @property
    def is_never(self) -> bool:
        """return self == ∅"""
        return not self.inverted and not self.items

    @property
    def is_always(self) -> bool:
        """return self == Ω"""
        return self.inverted and not self.items

    def __init__(self, items: Iterable[Item] = None, inverted: bool = False):
        self.items: FrozenSet[Item] = frozenset() if items is None else frozenset(items)
        self.inverted: bool = inverted

    def __repr__(self) -> str:
        """return repr(self)"""
        return f"{self.__class__.__name__}({self.items!r}, {self.inverted!r})"

    @property
    def items_str(self) -> str:
        return str(self.items)

    def __str__(self) -> str:
        """return str(self)"""
        if self.items:
            return f"{'¬' if self.inverted else ''}{self.items_str}"
        else:
            return 'Ω' if self.inverted else '∅'

    def __contains__(self, item) -> bool:
        return xor(item in self.items, self.inverted)

    def __invert__(self: T) -> T:
        return self.__class__(self.items, not self.inverted)

    def __or__(self: T, other: T) -> T:
        if other.inverted:
            func = frozenset.intersection if self.inverted else frozenset.difference
            return self.__class__(func(other.items, self.items), True)
        else:
            func = frozenset.difference if self.inverted else frozenset.union
            return self.__class__(func(self.items, other.items), self.inverted)

    def __and__(self: T, other: T) -> T:
        if other.inverted:
            func = frozenset.union if self.inverted else frozenset.difference
            return self.__class__(func(self.items, other.items), self.inverted)
        else:
            func = frozenset.difference if self.inverted else frozenset.intersection
            return self.__class__(func(other.items, self.items), False)

    def __truediv__(self: T, other: T) -> T:
        if other.inverted:
            func = frozenset.difference if self.inverted else frozenset.intersection
            return self.__class__(func(other.items, self.items), False)
        else:
            func = frozenset.union if self.inverted else frozenset.difference
            return self.__class__(func(self.items, other.items), self.inverted)

    def __add__(self: T, other: Item) -> T:
        func = self.items.difference if self.inverted else self.items.union
        return self.__class__(func({other}), self.inverted)

    def __sub__(self: T, other: Item) -> T:
        func = self.items.union if self.inverted else self.items.difference
        return self.__class__(func({other}), self.inverted)

    __iand__ = __and__
    __ior__ = __or__
    __itruediv__ = __truediv__
    __iadd__ = __add__
    __isub__ = __sub__

    @property
    def code_factory(self) -> Type[CONDITION]:
        if len(self.items) == 1:
            if self.inverted:
                return NE
            else:
                return EQ
        else:
            if self.inverted:
                return NOT_IN
            else:
                return IN

    def condition(self, item: VAR) -> CONDITION:
        raise NotImplementedError
