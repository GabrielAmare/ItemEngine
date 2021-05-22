import unittest
from typing import List, Tuple, Callable, Iterator, FrozenSet

from item_engine.base import *


class FakeRule(Rule):
    alphabet: FrozenSet[Item] = frozenset()
    is_skipable: bool = False
    is_non_terminal: bool = True
    is_terminal: bool = False
    is_valid: bool = False
    is_error: bool = False

    @property
    def __args__(self):
        return type(self), self.name

    def __init__(self, name: str):
        self.name: str = name

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name!r})"

    def __str__(self):
        return self.name

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        raise NotImplementedError


class TestRules(unittest.TestCase):
    def _test_fabric(self, fabric: Callable, cases: List[Tuple[List[Rule], Rule]]):
        for inputs, output in cases:
            self.assertEqual(first=output, second=fabric(*inputs))

    def test_OPTIONAL(self):
        """Testing the OPTIONAL fabric"""
        A, B = FakeRule("A"), FakeRule("B")

        self.assertEqual(first=Optional(All(A, B)), second=Optional.make(All(A, B)))
        self.assertEqual(first=Optional(Any(A, B)), second=Optional.make(Any(A, B)))
        self.assertEqual(first=Repeat(A), second=Optional.make(Repeat(A)))
        self.assertEqual(first=Optional(A), second=Optional.make(Optional(A)))
        self.assertEqual(first=Optional(A), second=Optional.make(A))
        self.assertEqual(first=VALID, second=Optional.make(VALID))
        self.assertEqual(first=VALID, second=Optional.make(ERROR))

    def test_REPEAT(self):
        """Testing the REPEAT fabric"""
        A, B = FakeRule("A"), FakeRule("B")

        self.assertEqual(first=Repeat(All(A, B)), second=Repeat.make(All(A, B)))
        self.assertEqual(first=Repeat(Any(A, B)), second=Repeat.make(Any(A, B)))
        self.assertEqual(first=Repeat(A), second=Repeat.make(Repeat(A)))
        self.assertEqual(first=Repeat(A), second=Repeat.make(Optional(A)))
        self.assertEqual(first=Repeat(A), second=Repeat.make(A))
        self.assertEqual(first=VALID, second=Repeat.make(VALID))
        self.assertEqual(first=VALID, second=Repeat.make(ERROR))

    def test_ALL(self):
        """Testing the ALL fabric"""
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

    def test_ANY(self):
        """Testing the ANY fabric : All, Any, Repeat, Optional, Match, Empty"""
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


if __name__ == '__main__':
    unittest.main()
