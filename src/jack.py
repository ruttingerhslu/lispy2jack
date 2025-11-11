import itertools

gensym_counter = itertools.count()

def gensym(prefix="f"):
    return f"{prefix}{next(gensym_counter)}"

class ANFtoJack:
    def anf_to_jack(self, anf, declared_vars=None, target_var=None, declared_funcs=None):
        if declared_vars is None:
            declared_vars = set()
        if declared_funcs is None:
            declared_funcs = []

        code_lines = []
        local_vars = set()

        # binary op
        if isinstance(anf, list) and anf[0] in ['+', '-', '*', '/', '=', '<', '>']:
            expr = self._expr_to_str(anf)
            if target_var:
                code_lines.append(f"let {target_var} = {expr};")
            return local_vars, "\n".join(code_lines) if code_lines else expr

        # lambda handling
        if isinstance(anf, list) and anf[0] == 'lambda':
            _, params, body = anf

            func_name = gensym("lambda")
            declared_funcs.append((func_name, params, body))

            if target_var:
                code_lines.append(f"let {target_var} = Main.{func_name};")
                return local_vars, "\n".join(code_lines)
            return local_vars, func_name

        # let
        if isinstance(anf, list) and anf[0] == 'let':
            _, bindings, body = anf
            if len(bindings) != 1:
                raise ValueError("ANF let can only have one binding")
            x, e = bindings[0]

            # bind lambda to variable
            if isinstance(e, list) and e[0] == 'lambda':
                _, params, lam_body = e
                declared_funcs.append((x, params, lam_body))
            else:
                e_vars, e_code = self.anf_to_jack(e, declared_vars, target_var=None, declared_funcs=declared_funcs)
                local_vars.update(e_vars)

                if x not in declared_vars:
                    local_vars.add(x)
                    declared_vars.add(x)

                if isinstance(e_code, str) and not e_code.startswith("let "):
                    code_lines.append(f"let {x} = {e_code};")
                else:
                    code_lines.append(e_code)

            body_vars, body_code = self.anf_to_jack(body, declared_vars, target_var, declared_funcs)
            local_vars.update(body_vars)
            code_lines.append(body_code)

            return local_vars, "\n".join(code_lines)

        # if
        if isinstance(anf, list) and anf[0] == 'if':
            _, cond, t_branch, e_branch = anf
            t_vars, t_code = self.anf_to_jack(t_branch, declared_vars.copy(), target_var)
            e_vars, e_code = self.anf_to_jack(e_branch, declared_vars.copy(), target_var)
            local_vars.update(t_vars)
            local_vars.update(e_vars)
            return local_vars, f"if ({self._expr_to_str(cond)}) {{\n{t_code}\n}} else {{\n{e_code}\n}}"

        if isinstance(anf, (int, float, str)):
            if target_var:
                code_lines.append(f"let {target_var} = {anf};")
                return local_vars, "\n".join(code_lines)
            return local_vars, str(anf)

        # function application
        if isinstance(anf, list) and len(anf) >= 1:
            fn = anf[0]
            args = anf[1:]

            # fn is a lambda expression
            if isinstance(fn, list) and fn[0] == 'lambda':
                _, params, body = fn
                func_name = gensym("lambda")
                declared_funcs.append((func_name, params, body))
                fn_name = func_name

            # fn is a variable or function name
            elif isinstance(fn, str):
                fn_name = fn
            else:
                raise ValueError(f"Unexpected function expression in application: {fn}")

            args_str = ", ".join(str(a) for a in args)
            expr = f"Main.{fn_name}({args_str})"

            if target_var:
                code_lines.append(f"let {target_var} = {expr};")
                return local_vars, "\n".join(code_lines)
            return local_vars, expr

        raise ValueError(f"Unrecognized ANF form: {anf}")

    def _expr_to_str(self, expr):
        if isinstance(expr, (int, float)):
            return str(expr)
        elif isinstance(expr, str):
            return expr
        elif isinstance(expr, list) and expr[0] in ['+', '-', '*', '/', '=', '>', '<'] and len(expr) > 2:
            op, e1, e2 = expr
            return f"({self._expr_to_str(e1)} {op} {self._expr_to_str(e2)})"
        elif isinstance(expr, list) and expr[0] in ['-', '~'] and len(expr) == 2:
            unOp, e = expr
            return f"({unOp} {self._expr_to_str(e)})"
        raise ValueError(f"Cannot convert expression to string: {expr}")

    def generate_class(self, anf):
        declared_vars, declared_funcs = set(), []
        _, body_code = self.anf_to_jack(anf, declared_vars, target_var="result", declared_funcs=declared_funcs)

        var_decls = [f"var int {v};" for v in declared_vars]

        # generate lifted function definitions
        func_decls = []
        for fname, params, body in declared_funcs:
            body_vars, func_body = self.anf_to_jack(body, declared_vars=set(), target_var="retval")
            local_decls = [f"var int {v};" for v in body_vars]
            func_code = (
                f"function int {fname}({', '.join('int ' + p for p in params)}) {{\n"
                + "var int retval;\n"
                + "\n".join(local_decls) + "\n"
                + func_body + "\n"
                "return retval;\n}"
            )
            func_decls.append(func_code)

        class_code = (
            "class Main {\n"
            + "\n".join(func_decls) + "\n\n"
            "function void main() {\n"
            + "var int result;\n"
            + "\n".join(var_decls) + "\n"
            + body_code + "\n"
            "do Output.printInt(result);\n"
            "return;\n"
            "}\n"
            "}"
        )

        return class_code
