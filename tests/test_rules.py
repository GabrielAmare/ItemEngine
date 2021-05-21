import unittest
from typing import List, Tuple, Callable

from item_engine.base import *


class TestRules(unittest.TestCase):
    def _test_fabric(self, fabric: Callable, cases: List[Tuple[List[Rule], Rule]]):
        for inputs, output in cases:
            self.assertEqual(fabric(*inputs), output)

    def test_001(self):
        """Testing the OPTIONAL fabric"""
        mat = Match(Group.always())
        self._test_fabric(OPTIONAL, [
            ([mat], Optional(mat)),
            ([Optional(mat)], Optional(mat)),
            ([Repeat(mat)], Repeat(mat)),
            ([VALID], VALID),
            ([ERROR], VALID),
        ])

    def test_002(self):
        """Testing the REPEAT fabric"""
        mat = Match(Group.always())
        self._test_fabric(REPEAT, [
            ([mat], Repeat(mat)),
            ([Optional(mat)], Repeat(mat)),
            ([Repeat(mat)], Repeat(mat)),
            ([VALID], VALID),
            ([ERROR], VALID),
        ])

    def test_003(self):
        """Testing the ALL fabric"""
        mat = Match(Group.always())
        self._test_fabric(ALL, [
            ([mat], mat),
            ([mat, mat], All(mat, mat)),
            ([VALID], VALID),
            ([ERROR], ERROR),
        ])

    def test_004(self):
        """Testing the ANY fabric"""
        mat = Match(Group.always())
        self._test_fabric(ANY, [
            ([mat], mat),
            ([mat, mat], Any(mat, mat)),
            ([VALID], VALID),
            ([ERROR], ERROR),
        ])


if __name__ == '__main__':
    unittest.main()
