from collections import defaultdict
import itertools

lambda_functions = []

counters = defaultdict(lambda: itertools.count())

def gensym(prefix="anon"):
    return f"{prefix}{next(counters[prefix])}"

def indent(s, level=1):
    pad = "  " * level
    return "\n".join(pad + line if line.strip() else line for line in s.splitlines())

def collect_vars(ast, vars_set=None):
    """Recursively set all let-bound variable names."""
    if vars_set is None:
        vars_set = set()
    if isinstance(ast, list):
        op = ast[0]
        if op == 'let':
            bindings, body = ast[1], ast[2]
            for name, val in bindings:
                vars_set.add(name)
                collect_vars(val, vars_set)
            collect_vars(body, vars_set)
        elif op == 'if':
            collect_vars(ast[1], vars_set)
            collect_vars(ast[2], vars_set)
            collect_vars(ast[3], vars_set)
        elif op == 'lambda':
            collect_vars(ast[2], vars_set)
        else:
            for e in ast[1:]:
                collect_vars(e, vars_set)
    return vars_set

def generate_expr(ast):
    """Generate Jack expressions"""
    if isinstance(ast, list):
        if len(ast) == 0:
            return ""
        op = ast[0]

        # if expression
        if op == 'if':
            cond = generate_expr(ast[1])
            then_branch = generate_block(ast[2])
            else_branch = generate_block(ast[3])
            return f"if ({cond}) {{\n{indent(then_branch)}\n}} else {{\n{indent(else_branch)}\n}}"

        # let expression
        elif op == 'let':
            bindings, body = ast[1], ast[2]
            code = ""
            for name, value in bindings:
                code += f"let {name} = {generate_expr(value)};\n"
            code += generate_expr(body)
            return code

        # lambda
        elif op == 'lambda':
            params = ", ".join(ast[1])
            body_code = generate_block(ast[2])
            fname = gensym("lambda")
            # store the function for top-level generation
            lambda_functions.append(f"function int {fname}({params}) {{\n{indent(body_code)}\n}}")
            return fname  # return function name so calls can use it

        # binary operation
        elif op in ['+', '-', '*', '/', '>', '<', '=', 'and', 'or']:
            left = generate_expr(ast[1])
            right = generate_expr(ast[2])
            return f"({left} {op} {right})"

        # quote
        elif op == "print":
            return f"do Output.printInt({generate_expr(ast[1])})"

        # function call
        else:
            args = ", ".join(generate_expr(a) for a in ast[1:])
            return f"{op}({args})"
    else:
        # variable or constant
        return str(ast)

def generate_block(expr):
    """Ensure block structure for nested expressions."""
    code = generate_expr(expr)
    if not code.strip().endswith(";"):
        code += ";"
    print(code)
    if not (code.strip().startswith("let") or code.strip().startswith("do")):
        code = "return " + code
    return code

def generate_function(name, params, body):
    """Generate a top-level Jack function."""
    local_vars = collect_vars(body)
    body_code = generate_block(body)
    var_decls = "\n".join(f"var int {v};" for v in local_vars)
    return f"function int {name}({', '.join(params)}) {{\n{indent(var_decls)}\n{indent(body_code)}\n}}"

def generate_jack(ast, class_name="Main"):
    """Generate a complete Jack class from AST"""
    global lambda_functions
    lambda_functions = []

    main_vars = collect_vars(ast)
    code = generate_expr(ast)
    var_decls = "\n".join(f"var int {v};" for v in main_vars)
    main_func = f"function void main () {{\n{indent(var_decls)}\n{indent(code)}\n  return;\n}}"

    class_body = "\n\n".join(lambda_functions + [main_func])

    return f"class {class_name} {{\n{indent(class_body)}\n}}"
