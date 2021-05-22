from __future__ import annotations

from typing import Tuple, Hashable

__all__ = ["ArgsHashed"]


class ArgsHashed(Hashable):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        raise NotImplementedError

    def __eq__(self, other: ArgsHashed):
        return self.__args__ == other.__args__

    def __hash__(self):
        return hash(self.__args__)

    def __lt__(self, other: ArgsHashed):
        tA, *A = self.__args__
        tB, *B = other.__args__
        if tA is tB:
            return A < B
        else:
            return tA.__name__ < tB.__name__
