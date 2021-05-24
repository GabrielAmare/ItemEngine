from abc import ABC

from item_engine import Item, Group, Match, ACTION, INCLUDE, EXCLUDE, AS, IN

__all__ = ["BaseItem", "BaseGroup"]


class Base:
    def match(self, action: ACTION) -> Match:
        raise NotImplementedError

    def include(self) -> Match:
        return self.match(INCLUDE)

    def exclude(self) -> Match:
        return self.match(EXCLUDE)

    def include_as(self, key: str) -> Match:
        return self.match(AS.format(key))

    def include_in(self, key: str) -> Match:
        return self.match(IN.format(key))

    inc = include
    exc = exclude
    as_ = include_as
    in_ = include_in


class BaseItem(Item, Base, ABC):
    def match(self, action: ACTION) -> Match:
        return Match(self.as_group, action)


class BaseGroup(Group, Base, ABC):
    def match(self, action: str) -> Match:
        return Match(self, action)
