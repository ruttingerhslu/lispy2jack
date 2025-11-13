class Env:
    """Environment to track variables and lifted function bindings with proper scoping."""
    def __init__(self, parent=None):
        self.parent = parent
        self.vars = set()
        self.func_bindings = {}

    def define_var(self, name):
        self.vars.add(name)

    def define_func(self, name, lifted_name):
        self.func_bindings[name] = lifted_name

    def lookup_func(self, name):
        if name in self.func_bindings:
            return self.func_bindings[name]
        if self.parent:
            return self.parent.lookup_func(name)
        return None

    def all_vars(self):
        result = set(self.vars)
        if self.parent:
            result |= self.parent.all_vars()
        return result
