from .anf import normalize_term
from .jack import anf_to_jack
from .fjack import *

def main(prompt: str = "fjack.py> "):
    """A prompt read-eval-print loop."""
    while True:
        ast = parse(input(prompt))
        anf = normalize_term(ast)
        print("ANF: ", anf)
        jack_code = anf_to_jack(anf)
        print(jack_code)
        # cps = v(ast)
        # collect_phi_assignments(cps)
        # ssa = g_proc(v(ast))

        # print(f'Scheme: {ast}')
        # print(f'CPS: {cps}')
        # print(f'SSA: {ssa}')

if __name__ == "__main__":
    main()
