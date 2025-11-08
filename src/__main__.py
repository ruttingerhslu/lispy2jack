from .anf import normalize_term, reset_gensym
from .jack import anf_to_jack
from .fjack import *

def main(prompt: str = "fjack.py> "):
    """A prompt read-eval-print loop."""
    while True:
        reset_gensym()
        expr = input(prompt)
        ast = parse(expr)
        anf = normalize_term(ast)
        print("ANF:", anf)
        print(anf_to_jack(anf))

        # cps = v(ast)
        # collect_phi_assignments(cps)
        # ssa = g_proc(v(ast))

        # print(f'Scheme: {ast}')
        # print(f'CPS: {cps}')
        # print(f'SSA: {ssa}')

if __name__ == "__main__":
    main()
