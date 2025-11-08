# lispy2jack
A source-to-source compiler from Lispy to Jack.

## Setup
Use the following command in the root directory to start the REPL:
```
python -m src.__main__
```

To test this project run:
```
pytest
```

## Semantics
We first take the abstract syntax for Core Scheme

### Core Scheme
M ::= V
      | (let (x M_1) M_2)
      | (if M_1 M_2 M_3)
      | (M M_1 ... M_n)
      | (O M_1 ... M_n)
V ::= c | x | (lambda (x_1 ... x_n) M)
V ∈ Values
c ∈ Constants
x ∈ Variables
O ∈ Primitive Operations

where in lambda x_i are distinct and bound to M
also in let expr: x is bound to M_2,
any other variable is free

Next, normalize using the algorithm described in "The essence of Compiling with Continuations"

And finally transform the A-Normalization to Jack:

- ['let', ['x', e1], e2]    -> var [type] x;\nlet x = emit(e1);\n emit(e2)
- ['if', cond, t, e]        -> if (cond) { emit(t) } else {emit(e)}
- ['lambda', params, body]  -> function [type] f1(params) { return emit(body) }
- [fn, arg1, arg2, ...]     -> f1(arg1, arg2, …)

Factorial:
(define f (lambda (n) (let ((g1478 (= n 0))) (if g1478 1 (let ((g1479 (- n 1))) (let ((g1480 (f g1479))) (* n g1480))))))) (f 20)
