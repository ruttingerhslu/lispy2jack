from collections import defaultdict
import itertools

from .env import Env

class JackGenerator:
    def __init__(self):
        self.counters = defaultdict(lambda: itertools.count())
        self.lifted = {}

    def gensym(self, prefix="anon"):
        return f"{prefix}{next(self.counters[prefix])}"

    def indent(self, s, level=1):
        pad = "  " * level
        return "\n".join(pad + line if line.strip() else line for line in s.splitlines())

    def generate_expr(self, ast, env):
        if isinstance(ast, list):
            if not ast:
                return ""

            op = ast[0]

            if op == "if":
                cond = self.generate_expr(ast[1], env)
                then_branch = self.generate_block(ast[2], env)
                else_branch = self.generate_block(ast[3], env)
                return (
                    f"if ({cond}) {{\n{self.indent(then_branch)}\n}} "
                    f"else {{\n{self.indent(else_branch)}\n}}"
                )

            elif op == "let":
                bindings, body = ast[1], ast[2]
                new_env = Env(env)
                code_lines = []
                for name, val in bindings:
                    if isinstance(val, list) and val and val[0] == "let":
                        inner_code = self.generate_expr(val, new_env)
                        inner_lines = inner_code.splitlines()
                        *inner_assignments, final_expr = inner_lines
                        code_lines.extend(inner_assignments)
                        code_lines.append(f"let {name} = {final_expr.replace('return ', '').rstrip(';')};")
                    else:
                        rhs = self.generate_expr(val, env)
                        code_lines.append(f"let {name} = {rhs};")
                    new_env.define_var(name)
                code_lines.append(self.generate_expr(body, new_env))
                return "\n".join(code_lines)

            elif op in ["+", "-", "*", "/", ">", "<", "=", "and", "or"]:
                left = self.generate_expr(ast[1], env)
                right = self.generate_expr(ast[2], env)
                return f"({left} {op} {right})"

            elif op == "print":
                return f"do Output.printInt({self.generate_expr(ast[1], env)});"

            else:
                fn_binding = env.lookup_func(op)
                fn_name = fn_binding if fn_binding else op
                args = ", ".join(self.generate_expr(a, env) for a in ast[1:])
                return f"Main.{fn_name}({args})"
        else:
            return str(ast)

    def generate_block(self, ast, env):
        code = self.generate_expr(ast, env)
        code = code.strip()
        if not code.endswith(";"):
            code = "return " + code + ";"
        return code

    def generate_function(self, fn):
        _, name, params, body = fn
        env = Env()
        for p in params:
            env.define_var(p)
        body_code = self.generate_block(body, env)
        var_decls = "\n".join(f"var int {v};" for v in env.vars if v not in params)
        return (
            f"function int {name}({', '.join(f'int {p}' for p in params)}) {{\n"
            f"{self.indent(var_decls)}\n{self.indent(body_code)}\n}}"
        )

    def generate_main(self, ast):
        env = Env()
        code = self.generate_expr(ast, env)
        var_decls = "\n".join(f"var int {v};" for v in env.vars)
        return f"function void main() {{\n{self.indent(var_decls)}\n{self.indent(code)}\n  return;\n}}"

    def generate_jack(self, ast, lifted_funcs=None, class_name="Main"):
        if lifted_funcs is None:
            lifted_funcs = []

        self.lifted = {fn[1]: fn[2:] for fn in lifted_funcs}

        lifted_code = [self.generate_function(fn) for fn in lifted_funcs]
        main_code = self.generate_main(ast)
        class_body = "\n\n".join(lifted_code + [main_code])
        return f"class {class_name} {{\n{self.indent(class_body)}\n}}"
