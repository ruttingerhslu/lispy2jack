import pprint

from .fjack import parse
from .cps import f
from .ssa import g_proc
from .jack import jack_proc

def main(prompt: str = "fjack.py> "):
    """A prompt read-eval-print loop."""
    while True:
        ast = parse(input(prompt))
        print(ast)
        cps = f(ast, 'k')
        print("CPS: ", cps)
        ssa = g_proc(cps)
        print("SSA: ", ssa)

        # print("CPS:")
        # pprint.pprint(cps)
        # print("SSA:")
        # pprint.pprint(ssa)

        print(jack_proc(ssa, name="main"))

if __name__ == "__main__":
    main()
