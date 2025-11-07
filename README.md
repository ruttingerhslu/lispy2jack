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

## Minimized functionality
This minimized version of the lispy2jack transpiler covers the following functionalities:
- lambda expressions: (lambda (x) (+ x x))
- if expressions: (if (cond) (m1) (m2))
- let expressions: (let ((x 5)) x)

We start by minimizing the formal translation described in [Kelsey](https://dl.acm.org/doi/pdf/10.1145/202530.202532)

First, from Scheme (our subset with limited abilities):
- M ::= E | (E E*) | (if E M M) | (let ((x M)) M)
- E ::= x | (op E E)
- P ::= (lambda (x*) M)
where x ∈ variables
      op ∈ [+, -, *, /, =, ..]

Translated using transformations to CPS:
- F : M x k -> M'
- F([(E, k)]) = (k E)
- F([(E...), k]) = (E ... k)
- F([(let ((x M_1)) M_2), k]) = F([M_1, (lambda (x) F([M_2, k]))])
- F([(if E M_1 M_2), k]) = (if E F([M_1, k]) F([M_2, k]))
- F([(lambda (x...) M)]) = (lambda (x...k) F([M, k]))

- V : P -> P'
- V([(lambda (x...) M)]) = (lambda (x...k) F([M, k]))

This of course would mean altering the CPS definition as well:
- M' ::=  (E E* C) |
          (E E*) |
          (k E) |
          (if E M' M') |
          (let ((x E)) M')
- C  ::=  k | (λ_cont (x) M')
- P' ::=  (λ_proc (x* k) M')
where x ∈ variables

And translating that to SSA:
- G: M' -> B
- G([(let ((x E)) M')]) = x <- E; G([M'])
- G([(k E)]) = return E;
- G([(if E M_1' M_2')]) = if E then G([M_1']) else G([M_2'])
<!--- G([(letrec (...) M')]) = G([M'])-->
- G_proc : P' -> P
- G_proc([(λ_proc (x ...) M')]) = proc(x ... k) { G([M']) ... }

Altering the definition:
- P ::= proc(x*) {B}
- B ::= x <- E; B | x <- E(E*); B |
              return E; | if E then B else B
- E ::= x | E + E | ...
where x ∈ variables
