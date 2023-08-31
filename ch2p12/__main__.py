import os
import string
import sys
from argparse import ArgumentParser
from collections import Counter, OrderedDict, namedtuple

from .Ciphie import Ciphie

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
    ciphertext = ciphertext.replace('\n', '').replace('\r', '')
    l = len(ciphertext)
    groups = [ciphertext[i:i+group_size] for i in range(0, l, group_size)]
    c = Counter(groups)
    
    return sorted(((ch, freq / l * 100) for ch, freq in c.items()), key=lambda x: x[1], reverse=True)

def print_ciphertext_with_substitutions(ciphertext, substitutions):
    print('-' * 80)
    buffer = []
    for ch in ciphertext:
        l = ch.upper()
        t = substitutions.get(l, l)
        if highlight_map.get(l):
            buffer.append(highlight_map[l] + t + bcolors.ENDC)
        else:
            buffer.append(t)
    print(''.join(buffer))
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

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

highlight_map = {

}

def print_frequencies(frequencies):
    print('Character frequencies:')
    print_ciphertext_statistics(frequencies.character)
    print('Digram frequencies:')
    print_ciphertext_statistics(frequencies.diagram)
    print('Trigram frequencies:')
    print_ciphertext_statistics(frequencies.trigram)

def update_current_key(key, val, ciphertext):
    for k, v in char_map.items():
        if v == val.lower():
            highlight_map[k] = bcolors.FAIL
    highlight_map[key.upper()] = bcolors.OKGREEN
    char_map[key.upper()] = val.lower()
    print_ciphertext_with_substitutions(ciphertext, char_map)

def main():
    ciphertext = get_ciphertext(args)
    frequencies = Frequencies(
        character=get_ciphertext_statistics(ciphertext),
        diagram=get_ciphertext_statistics(ciphertext, 2),
        trigram=get_ciphertext_statistics(ciphertext, 3)
    )
    
    print_frequencies(frequencies)

    c = Ciphie(ciphertext.lower()).decode()
    for ch, val in c.items():
        char_map[chr(ch).upper()] = chr(val).lower()

    print(Counter(char_map.values()).most_common())


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
            elif prompt.startswith('?'):
                key = prompt[1].upper()
                original_color = highlight_map.get(key, None)
                highlight_map[key] = bcolors.WARNING
                print_ciphertext_with_substitutions(ciphertext, char_map)
                if original_color:
                    highlight_map[key] = original_color
                else:
                    del highlight_map[key]
            elif prompt.startswith('+'):
                highlight_map[prompt[1].upper()] = bcolors.OKCYAN
                print_ciphertext_with_substitutions(ciphertext, char_map)
            elif prompt.startswith('-'):
                highlight_map.pop(prompt[1].upper(), None)
                print_ciphertext_with_substitutions(ciphertext, char_map)
            elif prompt.startswith('.'):
                if len(prompt) == 2:
                    for k, v in char_map.items():
                        if v == prompt[1].lower():
                            print(k)
                elif len(prompt) == 3:
                    keys = []
                    for k, v in char_map.items():
                        if v == prompt[1].lower():
                            keys.append(k)
                    if len(keys) == 1:
                        update_current_key(keys[0], prompt[2], ciphertext)
                    else:
                        print('ambiguous. there are multiple keys with this value: ', keys)
                else:
                    print('invalid')
            else:
                update_current_key(prompt[0], prompt[1], ciphertext)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()