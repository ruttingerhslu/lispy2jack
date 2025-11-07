import unittest

from src.fjack import *
from src.ssa import *

class TestSSA(unittest.TestCase):
    def test_lambda(self):
        # input: (lambda (x y k) (k (+ x y)))
        input = ['lambda', ['x', 'y', 'k'], ['k', ['+', 'x', 'y']]]
        ssa_ast = g_proc(input)

        expected = ['proc', ['x', 'y'], ['return', ['x', '+', 'y'], ';']]

        self.assertEqual(ssa_ast, expected)

    def test_if(self):
        input = ['lambda', ['x', 'k'], ['if', ['>', 'x', 0], ['k', ['+', 'x', 1]], ['k', ['-', 'x', 1]]]]
        ssa_ast = g_proc(input)

        expected = ['proc', ['x'], ['if', ['>', 'x', 0], 'then', ['return', ['x', '+', 1], ';'], 'else', ['return', ['x', '-', 1], ';']]]

        self.assertEqual(ssa_ast, expected)
