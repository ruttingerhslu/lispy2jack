"""
    FJack - Rafael Uttinger
    Minimal Scheme parser from Peter Norvig’s Lispy
"""
############ FJack: Scheme transpiler to Jack

# AST nodes
Symbol = str
Number = int | float
Atom = Symbol | Number
Exp = Atom | list["Exp"]

def tokenize(s: str) -> list[str]:
    """Convert a Scheme string into a list of tokens."""
    return s.replace("(", " ( ").replace(")", " ) ").split()

def atom(token: str) -> Exp:
    """Numbers become numbers; every other token is a symbol."""
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)

def read_from_tokens(tokens: list[str]) -> Exp:
    """Read an expression from a sequence of tokens."""
    if not tokens:
        raise SyntaxError("unexpected EOF while reading")
    token = tokens.pop(0)
    if token == "(":
        L: list[Exp] = []
        while tokens and tokens[0] != ")":
            L.append(read_from_tokens(tokens))
        if not tokens:
            raise SyntaxError("missing closing parenthesis")
        _ = tokens.pop(0)  # pop off ')'
        return L
    elif token == ")":
        raise SyntaxError("unexpected ')'")
    else:
        return atom(token)

def parse(program: str) -> Exp:
    """Read a Scheme expression from a string."""
    return read_from_tokens(tokenize(program))
