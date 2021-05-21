from __future__ import annotations
from dataclasses import dataclass
from typing import TypeVar, Generic, FrozenSet, Iterable, Type, Dict, List
from functools import reduce
from operator import or_

__all__ = ["GenericItem", "GenericItemSet", "optimized"]


@dataclass(frozen=True, order=True)
class GenericItem:
    @property
    def as_group(self) -> GenericItemSet:
        raise NotImplementedError

    def __or__(self, other: GenericItemSet) -> GenericItemSet:
        return self.as_group | other

    __ior__ = __or__

    def __add__(self, other: GenericItem):
        return self.as_group + other

    __iadd__ = __add__


K = TypeVar("K", bound=GenericItem)
V = TypeVar("V", bound=GenericItem)
T = TypeVar("T")


class GenericItemSet(Generic[K]):
    @classmethod
    def never(cls: Type[T]) -> T[K]:
        """return ∅"""
        return cls(frozenset(), False)

    @classmethod
    def always(cls: Type[T]) -> T[K]:
        """return Ω"""
        return cls(frozenset(), True)

    def __init__(self, items: Iterable[K] = None, inverted: bool = False):
        if items is None:
            items = frozenset()
        else:
            items = frozenset(items)
        self.items: FrozenSet[K] = items
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

    def __hash__(self) -> int:
        """return hash(self)"""
        return hash((type(self), self.items, self.inverted))

    def __contains__(self, obj: K) -> bool:
        """return obj in self"""
        if self.inverted:
            return obj not in self.items
        else:
            return obj in self.items

    def __eq__(self: T[K], other: T[K]) -> bool:
        return self.inverted == other.inverted and self.items == other.items

    def __ne__(self: T[K], other: T[K]) -> bool:
        """return self != other"""
        return not (self == other)

    def __lt__(self: T[K], other: T[K]) -> bool:
        """return self < other"""
        return self != other and self <= other

    def __le__(self: T[K], other: T[K]) -> bool:
        """return self <= other"""
        return (self / other).is_never

    def __gt__(self: T[K], other: T[K]) -> bool:
        """return self > other"""
        return other < self

    def __ge__(self: T[K], other: T[K]) -> bool:
        """return self >= other"""
        return other <= self

    def __or__(self: T[K], other: T[K]) -> T[K]:
        """return self | other"""
        if self.inverted:
            if other.inverted:
                items = self.items.intersection(other.items)
            else:
                items = self.items.difference(other.items)
        else:
            if other.inverted:
                items = other.items.difference(self.items)
            else:
                items = other.items.union(self.items)

        return self.__class__(items, self.inverted or other.inverted)

    __ior__ = __or__

    def __and__(self: T[K], other: T[K]) -> T[K]:
        """return self & other"""
        if self.inverted:
            if other.inverted:
                items = other.items.union(self.items)
            else:
                items = other.items.difference(self.items)
        else:
            if other.inverted:
                items = self.items.difference(other.items)
            else:
                items = self.items.intersection(other.items)

        return self.__class__(items, self.inverted and other.inverted)

    __iand__ = __and__

    def __truediv__(self: T[K], other: T[K]) -> T[K]:
        """return self / other"""
        if self.inverted:
            if other.inverted:
                items = other.items.difference(self.items)
            else:
                items = other.items.union(self.items)
        else:
            if other.inverted:
                items = self.items.intersection(other.items)
            else:
                items = self.items.difference(other.items)

        return self.__class__(items, self.inverted and not other.inverted)

    __itruediv__ = __truediv__

    def __add__(self: T[K], other: K) -> T[K]:
        """return self + other"""
        return self | other.as_group

    __iadd__ = __add__

    def __sub__(self: T[K], other: K) -> T[K]:
        """return self - other"""
        return self / other.as_group

    __isub__ = __sub__

    def __invert__(self: T[K]) -> T[K]:
        """return ~self"""
        return self.__class__(self.items, not self.inverted)

    @property
    def is_never(self) -> bool:
        """return self == ∅"""
        return not self.inverted and not self.items

    @property
    def is_always(self) -> bool:
        """return self == Ω"""
        return self.inverted and not self.items


ISK = TypeVar("ISK", bound=GenericItemSet)
ISV = TypeVar("ISV", bound=GenericItemSet)


def optimized(data: Dict[ISK, ISV]) -> Dict[ISK, ISV]:
    """
        For a given mapping of ItemSet[K] -> ItemSet[V]
        this function return an equivalent mapping where :
        - for all k: K, exist a unique ItemSet[K] in the new mapping which contains k
        - if there's two K items which are maps to the same ItemSet[V],
          then they are contained in the same ItemSet[K]

        this function basically make an optimized mapping equivalent to the initial one
        which avoid ambiguity and reduces the amount of item sets required
    """
    explicit: List = sorted(set(item for isk in data for item in isk.items))

    item_partition: Dict[GenericItem, ISV] = {
        item: reduce(or_, [isv for isk, isv in data.items() if item in isk])
        for item in explicit
    }
    default: ISV = reduce(or_, [isv for isk, isv in data.items() if isk.inverted])

    # this step makes sure to regroup all the K items that maps to the same ItemSet[V]
    reverted: Dict[ISV, ISK] = {}
    for v, isk in item_partition.items():
        if isk in reverted:
            reverted[isk] |= v.as_group
        else:
            reverted[isk] = v.as_group

    if default in reverted:
        # if there's an ItemSet[K] which maps to the default ItemSet[V]
        # (which is the map of all the non-explicit items)
        # then we revert the ItemSet[K] using all the explicit items
        reverted[default] = ~reduce(or_, [item.as_group for item in explicit if item not in reverted[default]])
    else:
        # else, it just revert the whole explicit (as default ItemSet[V] is mapped from no explicit item)
        reverted[default] = ~reduce(or_, [item.as_group for item in explicit])

    item_set_partition: Dict[ISK, ISV] = {isk: isv for isv, isk in reverted.items()}

    return item_set_partition
