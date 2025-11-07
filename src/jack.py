import itertools

gensym_counter = itertools.count()

def gensym(prefix="f"):
    return f"{prefix}{next(gensym_counter)}"

def anf_to_jack(anf):
    # binary operation
    if isinstance(anf, list) and anf[0] in ['+', '-', '/', '*', '=']:
        op, e1, e2 = anf
        return f"{anf_to_jack(e1)} {op} {anf_to_jack(e2)}"

    # atomic values
    if isinstance(anf, (int, float, bool, str)) and not isinstance(anf, list):
        return str(anf)

    # let expression: ['let', ['x', e1], e2]
    if isinstance(anf, list) and anf[0] == "let":
        _, [x, e1], e2 = anf
        return f"var {x} = {anf_to_jack(e1)};\n{anf_to_jack(e2)}"

    # if expression: ['if', cond, then, else]
    elif isinstance(anf, list) and anf[0] == "if":
        _, cond, t, e = anf
        return f"if ({anf_to_jack(cond)}) {{ {anf_to_jack(t)} }} else {{ {anf_to_jack(e)} }}"

    # lambda abstraction: ['lambda', ['x'], body]
    elif isinstance(anf, list) and anf[0] == "lambda":
        _, params, body = anf
        param_list = ", ".join(params)
        return f"function void {gensym()} ({param_list}) {{ return {anf_to_jack(body)}; }}"

    # function or operator application: ['+', 't0', 't1'], ['f', 'x'], etc.
    elif isinstance(anf, list):
        fn, *args = anf
        args_str = ", ".join(anf_to_jack(a) for a in args)
        return f"{anf_to_jack(fn)}({args_str})"

    else:
        raise ValueError(f"Unrecognized ANF form: {anf}")
