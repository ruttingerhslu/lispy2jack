from .anf import normalize_term, reset_gensym
from .jack import anf_to_jack
from .fjack import *

def main(prompt: str = "fjack.py> "):
    """A prompt read-eval-print loop."""
    while True:
        fjack_code = input(prompt)
        ast = parse(fjack_code)
        anf = normalize_term(ast)
        print("ANF: ", anf)
        jack_code = anf_to_jack(anf)
        print(jack_code)

if __name__ == "__main__":
    main()
