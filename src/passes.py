import itertools

gensym_counter = itertools.count()

def gensym(prefix="f"):
    return f"{prefix}{next(gensym_counter)}"

def optimize_direct_call(ast):
    """
    Transform ((lambda (x*) body) e* ...) => (let ([x* e*] ...) body)
    """
    if isinstance(ast, list) and len(ast) >= 1:
        first = ast[0]
        if isinstance(first, list) and len(first) == 3 and first[0] == 'lambda':
            params, body = first[1], first[2]
            args = ast[1:]
            if len(params) == len(args):
                bindings = list(zip(params, args))
                return ['let', bindings, optimize_direct_call(body)]
        return [optimize_direct_call(e) for e in ast]
    else:
        return ast

def remove_anonymous_lambda(ast):
    if isinstance(ast, list):
        if len(ast) >= 3 and ast[0] == 'lambda':
            params, body = ast[1], ast[2]
            body = remove_anonymous_lambda(body)
            t = gensym('f')
            return ['let', [[t, ['lambda', params, body]]], t]
        else:
            return [remove_anonymous_lambda(e) for e in ast]
    else:
        return ast
