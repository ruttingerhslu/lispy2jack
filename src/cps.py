def f(m, c):
    """Transform expression m into CPS using continuation c."""

    # --- LET ---
    if isinstance(m, list) and m[0] == 'let':
        _, bindings, body = m
        if not bindings:
            return f(body, c)
        (x, e), *rest = bindings
        new_body = ['let', rest, body] if rest else body
        return f(e, ['lambda', [x], f(new_body, c)])

    # --- IF ---
    elif isinstance(m, list) and m[0] == 'if':
        _, cond, then_m, else_m = m
        return ['if', cond,
                f(then_m, c),
                f(else_m, c)]

    # --- LAMBDA ---
    elif isinstance(m, list) and m[0] == 'lambda':
        _, params, body = m
        return ['lambda', params + ['k'], f(body, 'k')]

    # --- Primitive operations ---
    elif isinstance(m, list) and m[0] in ['+', '-', '*', '/', '>', '<', '=']:
        # compute operation first, bind result to v, call continuation
        return ['let', [['v', m]], [c, 'v']]

    # --- Function application ---
    elif isinstance(m, list):
        func = m[0]
        args = m[1:]
        if not args:
            return [func, c]

        first, *rest = args
        if rest:
            nested = [func] + rest
            return f(first, ['lambda', ['v'], f(nested, c)])
        else:
            return f(first, ['lambda', ['v'], [func, 'v', c]] if isinstance(func, list) else [func, first, c])

    # --- Variable / constant ---
    elif isinstance(c, list) and c[0] == 'lambda':
        _, [x], body = c
        return ['let', [[x, m]], body]

    elif isinstance(c, str):
        return [c, m]

    return m
