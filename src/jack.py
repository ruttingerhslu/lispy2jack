def jack_expr(e):
    """Translate SSA expressions to Jack syntax"""
    if isinstance(e, list) and len(e) == 3 and e[1] in ['+', '-', '*', '/', '>', '<', '=']:
        return f"({jack_expr(e[0])} {e[1]} {jack_expr(e[2])})"
    elif isinstance(e, list):
        # Nested expressions (like lambda or proc calls)
        return " ".join(jack_expr(x) if isinstance(x, list) else str(x) for x in e)
    return str(e)


def jack_block(b, indent=1):
    """Translate SSA body to Jack statements"""
    tab = "    " * indent

    if not isinstance(b, list):
        return tab + f"// {b}\n"

    # let
    if len(b) >= 5 and b[1] == '<-' and b[3] == ';':
        x, _, e, _, rest = b
        stmt = f"{tab}let {x} = {jack_expr(e)};\n"
        return stmt + jack_block(rest, indent)

    # if
    elif b[0] == 'if':
        _, cond, _, then_b, _, else_b = b
        cond_str = jack_expr(cond)
        then_block = jack_block(then_b, indent + 1)
        else_block = jack_block(else_b, indent + 1)
        return (
            f"{tab}if ({cond_str}) {{\n{then_block}{tab}}} else {{\n{else_block}{tab}}}\n"
        )

    # return
    elif b[0] == 'return' and b[-1] == ';':
        return tab + f"return {jack_expr(b[1])};\n"

    return tab + f"// Unhandled SSA node: {b}\n"


def jack_proc(proc, name="Main"):
    """Translate SSA proc into Jack function"""
    if not (isinstance(proc, list) and proc[0] == 'proc'):
        return "// Not a proc"
    _, params, body = proc
    params_str = ", ".join(params)
    block_str = jack_block(body)
    return (
        f"function void {name}({params_str}) {{\n"
        f"{block_str}"
        f"}}"
    )
