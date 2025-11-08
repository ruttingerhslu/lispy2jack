import itertools

gensym_counter = itertools.count()

def gensym(prefix="f"):
    return f"{prefix}{next(gensym_counter)}"

class ANFtoJack:
    def anf_to_jack(self, anf, declared_vars=None, target_var=None):
        if declared_vars is None:
            declared_vars = set()

        code_lines = []
        local_vars = set()

        # let
        if isinstance(anf, list) and anf[0] == 'let':
            _, bindings, body = anf
            if len(bindings) != 1:
                raise ValueError("ANF let can only have one binding")
            x, e = bindings[0]

            if x not in declared_vars:
                local_vars.add(x)
                declared_vars.add(x)

            code_lines.append(f"let {x} = {self._expr_to_str(e)};")
            body_vars, body_code = self.anf_to_jack(body, declared_vars, target_var)
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

        # binary op
        if isinstance(anf, list) and anf[0] in ['+', '-', '*', '/', '==', '=']:
            expr = self._expr_to_str(anf)
            if target_var:
                code_lines.append(f"let {target_var} = {expr};")
            return local_vars, "\n".join(code_lines) if code_lines else expr

        if isinstance(anf, (int, float, str)):
            if target_var:
                code_lines.append(f"let {target_var} = {anf};")
                return local_vars, "\n".join(code_lines)
            return local_vars, str(anf)

        raise ValueError(f"Unrecognized ANF form: {anf}")

    def _expr_to_str(self, expr):
        if isinstance(expr, (int, float)):
            return str(expr)
        if isinstance(expr, str):
            return expr
        if isinstance(expr, list) and expr[0] in ['+', '-', '*', '/', '==', '=']:
            op, e1, e2 = expr
            return f"({self._expr_to_str(e1)} {op} {self._expr_to_str(e2)})"
        raise ValueError(f"Cannot convert expression to string: {expr}")

    def generate_class(self, anf):
        declared_vars, body_code = self.anf_to_jack(anf, declared_vars=set(), target_var="result")

        # generate var decl at top
        var_decls = [f"var int {v};" for v in declared_vars]

        class_code = (
            "class Main {\n"
            "function void main() {\n"
            + "\n".join(var_decls) + "\n"
            + body_code + "\n"
            "do Output.printInt(result);\n"
            "return;\n"
            "}\n"
            "}"
        )
        return class_code
