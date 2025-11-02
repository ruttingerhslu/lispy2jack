import unittest

from src.fjack import *
from src.cps import *

class TestCPS(unittest.TestCase):
    def test_lambda(self):
        # input: (lambda (x y) (+ x y))
        input = ['lambda', ['x', 'y'], ['+', 'x', 'y']]
        cps_ast = v(input)

        # expected: (lambda_proc (x y k) (k (+ x y)))
        expected = ['lambda_proc', ['x', 'y', 'k'], ['k', ['+', 'x', 'y']]]

        self.assertEqual(cps_ast, expected)

    def test_if(self):
        # input: (lambda (x) (if (> x 0) (+ x 1) (- x 1)))
        input = ['lambda', ['x'], ['if', ['>', 'x', 0], ['+', 'x', 1], ['-', 'x', 1]]]
        cps_ast = v(input)

        # expected: (lambda_proc (x, k) (if (> x 0) (k (+ x 1)) (k (- x 1))))
        expected = ['lambda_proc', ['x', 'k'], ['if', ['>', 'x', 0], ['k', ['+', 'x', 1]], ['k', ['-', 'x', 1]]]]

        self.assertEqual(cps_ast, expected)

    def test_loop(self):
        # input: (lambda () (loop l ((x 2)) (if (= x 0) (x) (l (- x 1)))))
        input = ['lambda', [], ['loop', 'l', [['x', 2]], ['if', ['=', 'x', 0], ['x'], ['l', ['-', 'x', 1]]]]]

        cps_ast = v(input)

        # expected: (lambda_proc (k) (letrec ((l (lambda_jump (x) (if (= x 0) (k (x)) (l ((- x 1)))))))(l 2)))
        expected = ['lambda_proc', ['k'],
            ['letrec', [['l', ['lambda_jump',
                ['x'],
                ['if', ['=', 'x', 0], ['k', ['x']], ['l', [['-', 'x', 1]]]
                ]]]],
            ['l', 2]]]

        self.assertEqual(cps_ast, expected)
