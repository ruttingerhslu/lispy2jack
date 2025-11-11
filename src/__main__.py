from .anf import normalize_term
from .passes import *
from .new_jack import generate_jack
from .fjack import *

def main(prompt: str = "fjack.py> "):
    """A prompt read-eval-print loop."""
    while True:
        fjack_code = input(prompt)
        ast = parse(fjack_code)

        passes = [
            normalize_term,
            optimize_direct_call,
            remove_anonymous_lambda,
        ]
        ast = run_pipeline(ast, passes, True)

        jack_code = generate_jack(ast, class_name="Main")
        print(jack_code)

def run_pipeline(ast, passes, printFlag):
    """Apply all passes in order."""
    for p in passes:
        ast = p(ast)
        if printFlag:
            print(f"Pass: {p.__name__}")
            print(ast)
    return ast

if __name__ == "__main__":
    main()
