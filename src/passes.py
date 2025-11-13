import itertools

gensym_counter = itertools.count()

def gensym(prefix="f"):
    return f"{prefix}{next(gensym_counter)}"

def optimize_direct_call(ast):
    """((lambda (x*) body) e* ...) => (let ([x* e*] ...) body)"""
    if not isinstance(ast, list):
        return ast

    if len(ast) >= 1 and isinstance(ast[0], list):
        first = ast[0]
        if isinstance(first, list) and len(first) >= 3 and first[0] == 'lambda':
            params, body = first[1], first[2]
            args = ast[1:]
            if len(params) == len(args):
                bindings = [[p, optimize_direct_call(a)] for p, a in zip(params, args)]
                return ['let', bindings, optimize_direct_call(body)]

    op = ast[0]
    if op == 'let':
        bindings, body = ast[1], ast[2]
        new_bindings = [[x, optimize_direct_call(e)] for x, e in bindings]
        return ['let', new_bindings, optimize_direct_call(body)]
    elif op == 'if':
        return ['if', optimize_direct_call(ast[1]), optimize_direct_call(ast[2]), optimize_direct_call(ast[3])]
    else:
        return [optimize_direct_call(e) for e in ast]

def remove_anonymous_lambda(ast, top=True):
    """Add let binding to any anonymous lambdas"""
    if not isinstance(ast, list):
        return ast
    if len(ast) >= 3 and ast[0] == 'lambda' and top:
        params, body = ast[1], remove_anonymous_lambda(ast[2], top=False)
        t = gensym('f')
        return ['let', [[t, ['lambda', params, body]]], t]
    else:
        return [remove_anonymous_lambda(e, top=False) for e in ast]

def flatten_nested_lambdas(expr):
    """Recursively flatten nested lambdas inside other lambdas."""
    if not isinstance(expr, list):
        return expr

    expr = [flatten_nested_lambdas(e) for e in expr]

    if len(expr) == 3 and expr[0] == 'lambda':
        args = expr[1]
        body = expr[2]

        if isinstance(body, list) and len(body) == 3 and body[0] == 'lambda':
            inner_args = body[1]
            inner_body = body[2]
            return ['lambda', args + inner_args, inner_body]

    return expr

def lambda_lift(ast, lifted=None):
    """Convert lambdas into named top-level functions."""
    if lifted is None:
        lifted = []

    if isinstance(ast, list) and len(ast) >= 3 and ast[0] == 'lambda':
        params, body = ast[1], ast[2]
        fname = gensym("fun")
        lifted.append(['function', fname, params, body])
        return fname, lifted

    if isinstance(ast, list):
        new_ast = []
        for e in ast:
            lifted_expr, lifted = lambda_lift(e, lifted)
            new_ast.append(lifted_expr)
        return new_ast, lifted

    return ast, lifted

def flatten_nested_lets(expr):
    """Flatten nested let expressions by removing unnecessary temporary bindings."""
    if not isinstance(expr, list):
        return expr

    if len(expr) == 3 and expr[0] == 'let':
        bindings, body = expr[1], expr[2]
        new_bindings = []
        new_body = flatten_nested_lets(body)

        for var, val in bindings:
            val = flatten_nested_lets(val)
            # If val is a let, pull its bindings into the outer let
            if isinstance(val, list) and len(val) == 3 and val[0] == 'let':
                inner_bindings, inner_body = val[1], val[2]
                new_bindings.extend(inner_bindings)
                # Use inner body in place of the original binding variable
                new_body = replace_var(new_body, var, inner_body)
            else:
                new_bindings.append([var, val])

        return ['let', new_bindings, new_body]

    # Otherwise recursively process sub-expressions
    return [flatten_nested_lets(e) for e in expr]

def replace_var(expr, var, val):
    """Recursively replace occurrences of var in expr with val."""
    if isinstance(expr, list):
        return [replace_var(e, var, val) for e in expr]
    elif expr == var:
        return val
    else:
        return expr
