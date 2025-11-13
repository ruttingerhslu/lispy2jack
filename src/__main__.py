from .anf import normalize_term
from .passes import *
from .jack import JackGenerator
from .fjack import *

def main(prompt: str = "fjack.py> "):
    """A prompt read-eval-print loop."""
    while True:
        fjack_code = input(prompt)
        ast = parse(fjack_code)

        passes = [
            normalize_term,
            flatten_nested_lambdas,
            remove_anonymous_lambda,
            optimize_direct_call,
            flatten_nested_lets
        ]
        ast, lifted = run_pipeline(ast, passes, True)

        gen = JackGenerator()
        jack_code = gen.generate_jack(ast, lifted)
        print(jack_code)

def run_pipeline(ast, passes, printFlag):
    """Apply all passes in order."""
    for p in passes:
        ast = p(ast)
        if printFlag:
            print(f"Pass: {p.__name__}")
            print(ast)

    ast, lifted = lambda_lift(ast)
    if printFlag:
        print(f"Pass: lambda_lift")
        print(ast)
        print(lifted)
    return ast, lifted

if __name__ == "__main__":
    main()
