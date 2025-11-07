## Core Scheme
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

- ['let', ['x', e1], e2]    -> x = emit(e1);\n emit(e2)
- ['if', cond, t, e]        -> if (cond) { emit(t) } else {emit(e)}
- ['lambda', params, body]  -> function [type] f1(params): return emit(body)
- [fn, arg1, arg2, ...]     -> f1(arg1, arg2, …)
