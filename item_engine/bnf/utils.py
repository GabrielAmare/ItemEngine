from __future__ import annotations
from typing import List, Iterator


class ClassBuild:
    def __init__(self, name: str):
        self.name: str = name
        self.direct_sups: List[ClassBuild] = []
        self.direct_subs: List[ClassBuild] = []

    @property
    def sub_level(self):
        """Return the inheritance level from the bottom"""
        if self.direct_subs:
            return max(sub.sub_level for sub in self.direct_subs) + 1
        else:
            return 0

    @property
    def sup_level(self):
        """Return the inheritance level from the top"""
        if self.direct_sups:
            return max(sup.sup_level for sup in self.direct_sups) + 1
        else:
            return 0

    def all_subs(self) -> Iterator[ClassBuild]:
        if self.direct_subs:
            for cls in self.direct_subs:
                yield from cls.all_subs()
        else:
            yield self

    def add_sup(self, sup: ClassBuild):
        assert sup not in self.direct_sups, 'duplicate'
        assert sup not in self.all_subs(), 'tautology'
        self.direct_sups.append(sup)
        sup.direct_subs.append(self)

    def get_herits(self) -> List[str]:
        return [sup.name for sup in self.direct_sups]
