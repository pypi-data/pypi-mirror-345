
import sys
from pathlib import Path
from opensees import tcl

preamble = r"""

"""

def run(args):
    if len(args) == 1:
        files = Path(".").rglob("test*.tcl")
    else:
        files = (Path(arg) for arg in args[1:])

    for file in files:
        print()
        print(file.parents[0].name)
        try:
            with open(file, "r") as f:
                tcl.eval(preamble + f.read())

        except Exception as e:
            raise e
            continue


if __name__ == "__main__":

    run(sys.argv)
