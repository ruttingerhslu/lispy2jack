from .anf import normalize_term
from .jack import ANFtoJack
from .fjack import *

def main(prompt: str = "fjack.py> "):
    """A prompt read-eval-print loop."""
    while True:
        fjack_code = input(prompt)
        ast = parse(fjack_code)
        anf = normalize_term(ast)
        print("ANF: ", anf)

        converter = ANFtoJack()
        jack_code = converter.generate_class(anf)
        print(jack_code)

if __name__ == "__main__":
    main()
