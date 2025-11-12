from collections import defaultdict
import itertools

class JackGenerator:
    def __init__(self):
        self.counters = defaultdict(lambda: itertools.count())
        self.lifted = {}
        self.function_bindings = {}

    def gensym(self, prefix="anon"):
        return f"{prefix}{next(self.counters[prefix])}"

    def indent(self, s, level=1):
        pad = "  " * level
        return "\n".join(pad + line if line.strip() else line for line in s.splitlines())

    def collect_vars(self, ast, vars_set=None):
        if vars_set is None:
            vars_set = set()
        if not isinstance(ast, list):
            return vars_set
        op = ast[0]
        if op == 'let':
            bindings, body = ast[1], ast[2]
            for name, val in bindings:
                vars_set.add(name)
                self.collect_vars(val, vars_set)
            self.collect_vars(body, vars_set)
        elif op == 'if':
            for branch in ast[1:4]:
                self.collect_vars(branch, vars_set)
        elif op == 'lambda':
            params, body = ast[1], ast[2]
            vars_set.update(params)
            self.collect_vars(body, vars_set)
        else:
            for e in ast[1:]:
                self.collect_vars(e, vars_set)
        return vars_set

    def generate_expr(self, ast):
        if isinstance(ast, list):
            if len(ast) == 0:
                return ""
            op = ast[0]

            if op == 'if':
                cond = self.generate_expr(ast[1])
                then_branch = self.generate_block(ast[2])
                else_branch = self.generate_block(ast[3])
                return f"if ({cond}) {{\n{self.indent(then_branch)}\n}} else {{\n{self.indent(else_branch)}\n}}"

            elif op == 'let':
                bindings, body = ast[1], ast[2]
                code_lines = []
                for name, value in bindings:
                    if isinstance(value, list) and value[0] == 'let':
                        inner_bindings, inner_body = value[1], value[2]
                        for inner_name, inner_val in inner_bindings:
                            inner_code = self.generate_expr(['let', [[inner_name, inner_val]], []])
                            code_lines.append(inner_code)
                        final_expr = self.generate_expr(inner_body)
                        code_lines.append(f"let {name} = {final_expr};")
                    else:
                        if isinstance(value, str) and value in self.lifted:
                            self.function_bindings[name] = value
                        else:
                            code_lines.append(f"let {name} = {self.generate_expr(value)};")
                code_lines.append(self.generate_expr(body))
                return "\n".join([c for c in code_lines if c.strip()])

            elif op in ['+', '-', '*', '/', '>', '<', '=', 'and', 'or']:
                left = self.generate_expr(ast[1])
                right = self.generate_expr(ast[2])
                return f"({left} {op} {right})"

            elif op == "print":
                return f"do Output.printInt({self.generate_expr(ast[1])});"

            else:
                fn_name = ""
                if op in self.function_bindings:
                    fn_name = self.function_bindings[op]
                args = ", ".join(self.generate_expr(a) for a in ast[1:])
                return f"Main.{fn_name}({args})"
        else:
            if ast in self.function_bindings:
                return self.function_bindings[ast]
            return str(ast)

    def generate_block(self, expr):
        code = self.generate_expr(expr)
        if not code.strip().endswith(";"):
            code += ";"
        if not (code.strip().startswith("let") or code.strip().startswith("do")):
            code = "return " + code
        return code

    def generate_lifted_function(self, fn):
        _, orig_name, params, body = fn
        body_code = self.generate_block(body)
        name = self.lifted[orig_name]
        local_vars = self.collect_vars(body)
        var_decls = "\n".join(f"var int {v};" for v in local_vars if v not in self.function_bindings)
        return f"function int {name}({', '.join(f'int {p}' for p in params)}) {{\n{self.indent(var_decls)}\n{self.indent(body_code)}\n}}"

    def generate_main(self, ast):
        code = self.generate_expr(ast)
        local_vars = self.collect_vars(ast)
        var_decls = "\n".join(f"var int {v};" for v in local_vars if v not in self.function_bindings)
        return f"function void main() {{\n{self.indent(var_decls)}\n{self.indent(code)}\n  return;\n}}"

    def generate_jack(self, ast, lifted_funcs=None, class_name="Main"):
        if lifted_funcs is None:
            lifted_funcs = []

        self.lifted = {fn[1]: fn[1] for fn in lifted_funcs}
        self.function_bindings = {}

        lifted_code = [self.generate_lifted_function(fn) for fn in lifted_funcs]

        main_code = self.generate_main(ast)

        class_body = "\n\n".join(lifted_code + [main_code])
        return f"class {class_name} {{\n{self.indent(class_body)}\n}}"
