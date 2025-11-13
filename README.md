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

- ['let', ['x', e1], e2]    -> let x = emit(e1);\n emit(e2)
- ['if', cond, t, e]        -> if (cond) { emit(t) } else {emit(e)}
- [fn, arg1, arg2, ...]     -> f1(arg1, arg2, …)

Variables have to be declared at the top of the function they're used in.

Lambdas are supported by defining them as separate functions (similar to declaring variables at the top of the function), one can call them with their respective arguments. Say we have the following Scheme code:
```((lambda (x y) (+ x y)) 1 2)```
Is translated to Jack by taking the lambda definition, defining it as a function with a name, returning that name as a continuation and calling it with arguments: 1, 2
```
function int f0(int v0, int v1) {
  return v0 + v1;
}
...
function void main() {
  f0(1, 2)
}
```
The consequence of this is of course, that lambda expressions without arguments are not allowed, since the arguments are not known.

## Code examples
lambda with 2 args:
(print ((lambda (x y) (+ x y)) 1 2))

not allowed, x and y are unknown:
((lambda (x y) (+ x y)))

if test:
(let (x (+ 1 2)) (if (= x 3) (print 10) (print 20)))

if test (not allowed, x is unknown):
(if (> x 0) (x) (- x))

if lambda:
(print ((lambda (x) (> x 1)) 2))

square lambda:
(print ((lambda (x) (* x x)) 5))

named lambda (supported):
(let (square (lambda (x) (* x x))) (if (> (square 3) 5) (print (square 10)) (print (square 2))))

nested lambda (closures are not supported):
(let (add (lambda (x) (lambda (y) (+ x y)))) (print ((add 2) 3)))

nested lambda (closures are not supported):
(print ((lambda (x) (lambda (y) (lambda (z) (+ x (+ y z)))) 1) 2 3))
