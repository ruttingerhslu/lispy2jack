import unittest

from src.fjack import *
from src.cps import *

class TestCPS(unittest.TestCase):
    def test_lambda(self):
        # input: (lambda (x y) (+ x y))
        input = ['lambda', ['x', 'y'], ['+', 'x', 'y']]
        cps_ast = v(input)

        # expected: (lambda (x y k) (k (+ x y)))
        expected = ['lambda', ['x', 'y', 'k'], ['k', ['+', 'x', 'y']]]

        self.assertEqual(cps_ast, expected)

    def test_if(self):
        # input: (lambda (x) (if (> x 0) (+ x 1) (- x 1)))
        input = ['lambda', ['x'], ['if', ['>', 'x', 0], ['+', 'x', 1], ['-', 'x', 1]]]
        cps_ast = v(input)

        # expected: (lambda (x, k) (if (> x 0) (k (+ x 1)) (k (- x 1))))
        expected = ['lambda', ['x', 'k'], ['if', ['>', 'x', 0], ['k', ['+', 'x', 1]], ['k', ['-', 'x', 1]]]]

        self.assertEqual(cps_ast, expected)
