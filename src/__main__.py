from .fjack import *

def main(prompt: str = "fjack.py> "):
    """A prompt read-eval-print loop."""
    while True:
        ast = parse(input(prompt))
        cps = v(ast)
        collect_phi_assignments(cps)
        ssa = g_proc(v(ast))

        print(f'Scheme: {ast}')
        print(f'CPS: {cps}')
        # print(f'Phi assignments: {phi_assignments}')
        print(f'SSA: {ssa}')

if __name__ == "__main__":
    main()
