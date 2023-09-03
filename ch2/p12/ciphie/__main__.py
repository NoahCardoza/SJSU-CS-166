
from ciphie.args import get_args
from ciphie.Ciphie import Ciphie
from ciphie.Repl import Repl


def main():
    args, ciphertext = get_args()

    best_key = None
    ciphie = Ciphie(ciphertext, args.verbose)
    if args.decode:
        best_key = ciphie.decode()
    
    Repl(ciphie, best_key).run()


main()