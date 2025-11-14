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

Next, normalize using the algorithm described in "The essence of Compiling with Continuations".

To make code generation simpler, we go through multiple passes of the CoreScheme ast:
- normalize_term,
- optimize_direct_call
- flatten_nested_lets
- lambda_lift

``normalize-term``: takes the current ast representation and translates it to A-normalization form.

``optimize_direct_call``: transforms (if possible) a lambda into a simpler let expression, this is much easier to translate, since there isnt a need for an entirely different function

``flatten_nested_lets``: this pass makes translation even easier, since we don't need to check for nested let expressions in our generate_jack function

``lambda_lift``: this might be the most important pass, as it gives us functions along with scheme ast, these functions represent lambdas that have been lifted out of the abstract syntax tree and have been replaced with the name of the lifted function (always the same as the bound variable; this might be a design flaw, but it makes code generation easier, since we only need to check if a variable is named after a lifted function to check for function bindings):
```
(let (square (lambda (x) (*x x))) (print (square 5)))
# translated to
(let (square square) (print (square 5))), {function square: (x), (x * x)}
```
Later on, when we see the binding square f0, we know that f0 is a function, and so square is only here to guide further uses of the function to f0 instead

In Jack, Variables have to be declared at the top of the function they're used in.

One weakness that comes with this transpiler is that closures are not supported, Jack doesn't inherently support binding a variable to a function, thus implementing closures is not trivial.

## Code examples
lambda with 2 args:
```
(print ((lambda (x y) (+ x y)) 1 2))
```

not allowed, x and y are unknown:
```
((lambda (x y) (+ x y)))
```

if test:
```
(let (x (+ 1 2)) (if (= x 3) (print 10) (print 20)))
```

if test (not allowed, x is unknown):
```
(if (> x 0) (x) (- x))
```

if lambda:
```
(print ((lambda (x) (> x 1)) 2))
```

square lambda:
```
(print ((lambda (x) (* x x)) 5))
```

named lambda (supported):
```
(let (square (lambda (x) (* x x))) (if (> (square 3) 5) (print (square 10)) (print (square 2))))
```

nested lambda (closures are not supported):
```
(let (add (lambda (x) (lambda (y) (+ x y)))) (print ((add 2) 3)))
```

nested lambda (closures are not supported):
```
(print ((lambda (x) (lambda (y) (lambda (z) (+ x (+ y z)))) 1) 2 3))
```
