def g(m):
    """Translate CPS M' -> imperative style B"""

    # Binary operators
    if isinstance(m, list) and len(m) == 3 and m[0] in ['+', '-', '*', '/', '>', '<', '=']:
        return [g(m[1]), m[0], g(m[2])]

    # let binding
    elif isinstance(m, list) and m[0] == 'let':
        _, bindings, body = m
        if not bindings:
            return g(body)
        (x, e), *rest = bindings
        next_body = ['let', rest, body] if rest else body
        return [x, '<-', g(e), ';', g(next_body)]

    # if expression
    elif isinstance(m, list) and m[0] == 'if':
        _, cond, then_m, else_m = m
        return ['if', cond, 'then', g(then_m), 'else', g(else_m)]

    # continuation call (k E)
    elif isinstance(m, list) and m[0] == 'k' and len(m) == 2:
        return ['return', g(m[1]), ';']

    return m

def g_proc(p):
    """Translate CPS lambda -> procedure"""
    if not (isinstance(p, list) and p[0] == 'lambda'):
        return p
    _, params, body = p

    # Remove continuation param 'k'
    if params and params[-1] == 'k':
        params = params[:-1]

    return ['proc', params, g(body)]
