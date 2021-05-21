import unittest
from typing import List, Tuple, Callable, Iterator, FrozenSet

from item_engine.base import *


class FakeRule(Rule):
    def __init__(self, name: str):
        self.name: str = name

    def __eq__(self, other):
        return type(self) is type(other) and self.name == other.name

    def __hash__(self):
        return hash((type(self), self.name))

    def __lt__(self, other):
        if type(self) is type(other):
            return self.name < other.name
        else:
            raise NotImplementedError

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name!r})"

    def __str__(self):
        return self.name

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return frozenset()

    @property
    def is_non_terminal(self) -> bool:
        return True

    @property
    def is_terminal(self) -> bool:
        return False

    @property
    def is_valid(self) -> bool:
        return False

    @property
    def is_error(self) -> bool:
        return False

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

        self.assertEqual(first=Optional(All(A, B)), second=OPTIONAL(All(A, B)))
        self.assertEqual(first=Optional(Any(A, B)), second=OPTIONAL(Any(A, B)))
        self.assertEqual(first=Repeat(A), second=OPTIONAL(Repeat(A)))
        self.assertEqual(first=Optional(A), second=OPTIONAL(Optional(A)))
        self.assertEqual(first=Optional(A), second=OPTIONAL(A))
        self.assertEqual(first=VALID, second=OPTIONAL(VALID))
        self.assertEqual(first=VALID, second=OPTIONAL(ERROR))

    def test_REPEAT(self):
        """Testing the REPEAT fabric"""
        A, B = FakeRule("A"), FakeRule("B")

        self.assertEqual(first=Repeat(All(A, B)), second=REPEAT(All(A, B)))
        self.assertEqual(first=Repeat(Any(A, B)), second=REPEAT(Any(A, B)))
        self.assertEqual(first=Repeat(A), second=REPEAT(Repeat(A)))
        self.assertEqual(first=Repeat(A), second=REPEAT(Optional(A)))
        self.assertEqual(first=Repeat(A), second=REPEAT(A))
        self.assertEqual(first=VALID, second=REPEAT(VALID))
        self.assertEqual(first=VALID, second=REPEAT(ERROR))

    def test_ALL(self):
        """Testing the ALL fabric"""
        A, B = FakeRule("A"), FakeRule("B")

        self.assertEqual(first=All(A, B), second=ALL(All(A, B)))
        self.assertEqual(first=Any(A, B), second=ALL(Any(A, B)))
        self.assertEqual(first=Repeat(A), second=ALL(Repeat(A)))
        self.assertEqual(first=Optional(A), second=ALL(Optional(A)))
        self.assertEqual(first=A, second=ALL(A))
        self.assertEqual(first=VALID, second=ALL(VALID))
        self.assertEqual(first=ERROR, second=ALL(ERROR))
        self.assertEqual(first=All(A, A), second=ALL(A, A))
        self.assertEqual(first=All(A, B), second=ALL(A, B))

    def test_ANY(self):
        """Testing the ANY fabric : All, Any, Repeat, Optional, Match, Empty"""
        A, B = FakeRule("A"), FakeRule("B")

        self.assertEqual(first=All(A, B), second=ANY(All(A, B)))
        self.assertEqual(first=Any(A, B), second=ANY(Any(A, B)))
        self.assertEqual(first=Repeat(A), second=ANY(Repeat(A)))
        self.assertEqual(first=Optional(A), second=ANY(Optional(A)))
        self.assertEqual(first=A, second=ANY(A))
        self.assertEqual(first=VALID, second=ANY(VALID))
        self.assertEqual(first=ERROR, second=ANY(ERROR))
        self.assertEqual(first=A, second=ANY(A, A))
        self.assertEqual(first=Any(A, B), second=ANY(A, B))


if __name__ == '__main__':
    unittest.main()
