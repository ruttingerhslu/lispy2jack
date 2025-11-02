rec_bound = set()
labels = set()

# note: all expressions are wrapped within []
def f(m, c):
    """F: M × C → M'"""
    # F([(let ((x M_1)) M_2), C]) = F([M_1, (lambda(x) F([M_2, C]))])
    if m[0] == 'let':
        _, bindings, body = m
        (x, m1), = bindings
        return f(m1, ['lambda_cont', [x], f(body, c)])
    elif m[0] == 'if':
        _, cond, then_m, else_m = m
        # F([(if E M_1 M_2), k]) = (if E F([M_1, k]) F([M_2, k]))
        if isinstance(c, str):
            return ['if', cond, f(then_m, c), f(else_m, c)]
        # F([(if E M_1 M_2), (lambda_cont (x) M')]) =
        #     (letrec ((x (lambda_jump (x) M'))) (if E F([M_1, x]) F([M_2, x])))
        elif c[0] == 'lambda_cont':
            _, [x], cont_m = c
            rec_bound.add(x)
            return ['letrec',
                    [[x, ['lambda_jump', [x], cont_m]]],
                    ['if', cond, f(then_m, x), f(else_m, x)]
                ]

    # F([(loop l ((x E_initial) ...)M), C]) =
    #    (letrec ((l (λ_jump (x...) F([M, C])))) (l E_initial ...))
    elif m[0] == 'loop':
        _, l, bindings, body = m

        labels.add(l)

        params = [x for (x, _) in bindings]
        inits = [e for (_, e) in bindings]

        transformed_body = f(body, c)

        return [
            'letrec',
            [[l, ['lambda_jump', params, transformed_body]]],
            [l] + inits
        ]

    # F([(l E ...), C]) = (l E ...)
    elif isinstance(m[0], str) and m[0] in labels:
        return [m[0]] + [m[1:]]

    # F([(E...), C]) = (let ((v (E ...))) (j v)) if C = x and x is bound by letrec
    elif isinstance(c, str) and c in rec_bound:
        return ['let', [['v', m]], [c, 'v']]

    # F([E, k]) = (k E)
    elif isinstance(c, str):
        return [c, m]

    # F([(E, (lambda_cont (x) M'))]) = (let ((x E)) M')
    elif isinstance(c, list) and c[0] == 'lambda_cont':
        _, [x], body = c
        return ['let', [[x, m]], body]

    return m

def v(p):
    """
        Entry function for transforming from Scheme to CPS
        V: P → P'
    """
    # V([(lambda(x...) M)]) = (lambda_proc (x...k) F([M, k]))
    if isinstance(p, list) and p[0] == 'lambda':
        _, params, body = p
        return ['lambda_proc', params + ['k'], f(body, 'k')]
    return p
