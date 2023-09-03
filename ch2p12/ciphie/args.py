import os
import sys
from argparse import ArgumentParser


def get_ciphertext(args):
    if args.input:
        if not os.path.exists(args.input):
            return None
        with open(args.input, 'r') as f:
            return f.read()
    else:
        return sys.stdin.read()

def create_arg_parser():
    arg_parser = ArgumentParser(prog='ciphie', description='Ciphie')
    arg_parser.add_argument('-i', '--input', help='File input (default: stdin)')
    arg_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    arg_parser.add_argument('-d', '--decode', action='store_true', help='Attempt to break ciphertext before entering REPL')

    return arg_parser

def get_args():
    args = create_arg_parser().parse_args()

    ciphertext = get_ciphertext(args)
    if ciphertext is None:
        print('Error: file does not exist')
        sys.exit(1)
    
    return args, ciphertext 
