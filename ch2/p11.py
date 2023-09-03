import os
import re
import string
import sys
from argparse import ArgumentParser
from collections import Counter, OrderedDict, namedtuple

RE_NEWLINE = re.compile(r'\r?\n')

arg_parser = ArgumentParser(description='Cyphie')
arg_parser.add_argument('-i', '--input', help='File input')

args = arg_parser.parse_args()

def get_ciphertext(args):
    if args.input:
        if not os.path.exists(args.input):
            print('Error: file does not exist')
            sys.exit(1)
        with open(args.input, 'r') as f:
            return f.read()
    else:
        return sys.stdin.read()
    
def get_ciphertext_statistics(ciphertext: str, group_size: int = 1):
    ciphertext = RE_NEWLINE.sub('', ciphertext)
    l = len(ciphertext)
    groups = [ciphertext[i:i+group_size] for i in range(0, l, group_size)]
    c = Counter(groups)
    
    return sorted(((ch, freq / l * 100) for ch, freq in c.items()), key=lambda x: x[1], reverse=True)

def print_ciphertext_with_substitutions(ciphertext, substitutions):
    print('-' * 80)
    print(''.join(substitutions.get(ch.upper(), ch.upper()) for ch in ciphertext))
    print('-' * 80)

def print_ciphertext_with_substitutions_and_overlay(ciphertext, substitutions):
    print('-' * 80)
    for line in ciphertext.splitlines():
        print('original :', line)
        print('decoded  :', ''.join(substitutions.get(ch.upper(), ch.upper()) for ch in line))
    print('-' * 80)

def print_ciphertext_statistics(stats):
    for (ch, freq) in stats:
        print("{}: {:.2f}%".format(ch, freq))

char_map = OrderedDict({
    ch: ch for ch in string.ascii_uppercase
})

Frequencies = namedtuple('Frequencies', ['character', 'diagram', 'trigram'])

help_text = """
[letter][replacement]: replace [letter] with [replacement] and print the partially decoded ciphertext
key: print the current key
overlay: print the ciphertext with the current key overlaid
freq: print the current ciphertext frequencies
q: quit
"""

def print_frequencies(frequencies):
    print('Character frequencies:')
    print_ciphertext_statistics(frequencies.character)
    print('Digram frequencies:')
    print_ciphertext_statistics(frequencies.diagram)
    print('Trigram frequencies:')
    print_ciphertext_statistics(frequencies.trigram)

def main():
    ciphertext = get_ciphertext(args)
    frequencies = Frequencies(
        character=get_ciphertext_statistics(ciphertext),
        diagram=get_ciphertext_statistics(ciphertext, 2),
        trigram=get_ciphertext_statistics(ciphertext, 3)
    )
    
    print_frequencies(frequencies)

    print_ciphertext_with_substitutions(ciphertext, char_map)
    print('Upper case letters are the original letters, lower case letters are the putative replacements.')
    print('Map a letter (BA) to see A substituted for B:')
    try:
        while True:
            
            prompt = input('> ')
            if prompt == 'q':
                break
            if prompt == 'key':
                print(string.ascii_uppercase)
                print(''.join(char_map.values()))
            elif prompt == 'overlay':
                print_ciphertext_with_substitutions_and_overlay(ciphertext, char_map)
            elif prompt == 'freq':
                print_frequencies(frequencies)
            elif prompt == 'help':
                print(help_text)
            else:
                key, val = prompt[0], prompt[1]
                char_map[key.upper()] = val.lower()
                print_ciphertext_with_substitutions(ciphertext, char_map)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()