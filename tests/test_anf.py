import unittest

from src.fjack import parse
from src.anf import normalize_term

class TestANF(unittest.TestCase):
    def test_lambda(self):
        input = parse("((lambda (x) (> x 1)) 2)")

        expected = [['lambda', ['x'], ['>', 'x', 1]], 2]

        anf = normalize_term(input)

        self.assertEqual(anf, expected)
