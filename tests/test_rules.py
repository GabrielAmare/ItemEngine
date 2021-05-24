import unittest
from typing import Tuple, Iterator, FrozenSet, Hashable

from item_engine.constants import EXCLUDE, INCLUDE

from item_engine.base import *


class FakeRule(Rule):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), \
               self.name, \
               self.alphabet, \
               self.is_skipable, \
               self.is_non_terminal, \
               self.is_terminal, \
               self.is_valid, \
               self.is_error

    def __init__(self, name: str,
                 is_skipable: bool = False,
                 is_non_terminal: bool = True,
                 is_terminal: bool = False,
                 is_valid: bool = False,
                 is_error: bool = False,
                 alphabet: FrozenSet[Item] = frozenset(),
                 ):
        self.name: str = name
        self._alphabet: FrozenSet[Item] = alphabet
        self._is_skipable: bool = is_skipable
        self._is_non_terminal: bool = is_non_terminal
        self._is_terminal: bool = is_terminal
        self._is_valid: bool = is_valid
        self._is_error: bool = is_error

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name!r})"

    def __str__(self):
        return self.name

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return self._alphabet

    @property
    def is_skipable(self) -> bool:
        return self._is_skipable

    @property
    def is_non_terminal(self) -> bool:
        return self._is_non_terminal

    @property
    def is_terminal(self) -> bool:
        return self._is_terminal

    @property
    def is_valid(self) -> bool:
        return self._is_valid

    @property
    def is_error(self) -> bool:
        return self._is_error

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        raise NotImplementedError


class FakeItem(Item):
    @property
    def __args__(self) -> Tuple[Hashable, ...]:
        return type(self), self.name

    def __init__(self, name: str):
        self.name: str = name

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name!r})"

    @property
    def as_group(self) -> Group:
        return Group({self})


class TestRules(unittest.TestCase):
    def test_001(self):
        """Testing Optional.make"""
        A, B = FakeRule("A"), FakeRule("B")

        self.assertEqual(first=Optional(All(A, B)), second=Optional.make(All(A, B)))
        self.assertEqual(first=Optional(Any(A, B)), second=Optional.make(Any(A, B)))
        self.assertEqual(first=Repeat(A), second=Optional.make(Repeat(A)))
        self.assertEqual(first=Optional(A), second=Optional.make(Optional(A)))
        self.assertEqual(first=Optional(A), second=Optional.make(A))
        self.assertEqual(first=VALID, second=Optional.make(VALID))
        self.assertEqual(first=VALID, second=Optional.make(ERROR))

    def test_002(self):
        """Testing Repeat.make"""
        A, B = FakeRule("A"), FakeRule("B")

        self.assertEqual(first=Repeat(All(A, B)), second=Repeat.make(All(A, B)))
        self.assertEqual(first=Repeat(Any(A, B)), second=Repeat.make(Any(A, B)))
        self.assertEqual(first=Repeat(A), second=Repeat.make(Repeat(A)))
        self.assertEqual(first=Repeat(A), second=Repeat.make(Optional(A)))
        self.assertEqual(first=Repeat(A), second=Repeat.make(A))
        self.assertEqual(first=VALID, second=Repeat.make(VALID))
        self.assertEqual(first=VALID, second=Repeat.make(ERROR))

    def test_003(self):
        """Testing All.make"""
        A, B = FakeRule("A"), FakeRule("B")

        self.assertEqual(first=All(A, B), second=All.make(All(A, B)))
        self.assertEqual(first=Any(A, B), second=All.make(Any(A, B)))
        self.assertEqual(first=Repeat(A), second=All.make(Repeat(A)))
        self.assertEqual(first=Optional(A), second=All.make(Optional(A)))
        self.assertEqual(first=A, second=All.make(A))
        self.assertEqual(first=VALID, second=All.make(VALID))
        self.assertEqual(first=ERROR, second=All.make(ERROR))
        self.assertEqual(first=All(A, A), second=All.make(A, A))
        self.assertEqual(first=All(A, B), second=All.make(A, B))

        self.assertEqual(first=ERROR, second=All.make(A, ERROR))
        self.assertEqual(first=ERROR, second=All.make(ERROR, A))

        self.assertEqual(first=A, second=All.make(A, VALID))
        self.assertEqual(first=A, second=All.make(VALID, A))

    def test_004(self):
        """Testing Any.make"""
        A, B = FakeRule("A"), FakeRule("B")

        self.assertEqual(first=All(A, B), second=Any.make(All(A, B)))
        self.assertEqual(first=Any(A, B), second=Any.make(Any(A, B)))
        self.assertEqual(first=Repeat(A), second=Any.make(Repeat(A)))
        self.assertEqual(first=Optional(A), second=Any.make(Optional(A)))
        self.assertEqual(first=A, second=Any.make(A))
        self.assertEqual(first=VALID, second=Any.make(VALID))
        self.assertEqual(first=ERROR, second=Any.make(ERROR))
        self.assertEqual(first=A, second=Any.make(A, A))
        self.assertEqual(first=Any(A, B), second=Any.make(A, B))

        self.assertEqual(first=A, second=Any.make(A, ERROR))
        self.assertEqual(first=A, second=Any.make(ERROR, A))

        self.assertEqual(first=VALID, second=Any.make(A, VALID))
        self.assertEqual(first=VALID, second=Any.make(VALID, A))

    def test_005(self):
        """Testing Group.never / Group.is_never / Group.always / Group.is_always"""
        self.assertTrue(Group.always().is_always)
        self.assertFalse(Group.always().is_never)
        self.assertTrue(Group.never().is_never)
        self.assertFalse(Group.never().is_always)

    def test_006(self):
        """Testing Rule.cast"""
        A, B = FakeRule("A"), FakeRule("B")
        x, y = FakeItem('X'), FakeItem('Y')
        X, Y = Group({x}), Group({y})

        # Test basic
        self.assertEqual(first=Any(A, B), second=Rule.cast(frozenset({A, B})))
        self.assertEqual(first=Any(A, B), second=Rule.cast({A, B}))
        self.assertEqual(first=All(A, B), second=Rule.cast((A, B)))
        self.assertEqual(first=All(A, B), second=Rule.cast([A, B]))
        self.assertEqual(first=Match(X, INCLUDE), second=Rule.cast(X))
        self.assertEqual(first=Match(X, INCLUDE), second=Rule.cast(x))

        # Test that Rule.cast works accordingly with All.make & Any.make
        self.assertEqual(first=Match(X, INCLUDE), second=Rule.cast(frozenset({X})))
        self.assertEqual(first=Match(X, INCLUDE), second=Rule.cast({X}))
        self.assertEqual(first=Match(X, INCLUDE), second=Rule.cast((X,)))
        self.assertEqual(first=Match(X, INCLUDE), second=Rule.cast([X]))

        # Test nested
        self.assertEqual(first=All(Match(X, INCLUDE), Match(Y, INCLUDE)), second=Rule.cast([X, Y]))
        self.assertEqual(first=Any(Match(X, INCLUDE), Match(Y, INCLUDE)), second=Rule.cast({X, Y}))

        # Test bigger nested
        self.assertEqual(
            first=Any(
                All(Match(X, INCLUDE), Match(Y, INCLUDE)),
                All(Match(Y, INCLUDE), Match(X, INCLUDE))
            ),
            second=Rule.cast({(Y, X), (X, Y)})
        )


if __name__ == '__main__':
    unittest.main()
