import unittest
from item_engine.textbase import *


class TestTextBase(unittest.TestCase):
    def test_001(self):
        self.assertEqual(first=Token(0, 5, 46, "ckjzkjbz"), second=Token(0, 5, 46, "ckjzkjbz"))
        self.assertEqual(first=Token(0, 1, 46, "ckjzkjbz", 0, 5), second=Token(0, 1, 46, "ckjzkjbz", 0, 5))


if __name__ == '__main__':
    unittest.main()
