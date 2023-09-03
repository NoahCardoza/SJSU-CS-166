import os
import string
import traceback
from collections import OrderedDict
from typing import Dict, Optional

from ciphie import colors
from ciphie.args import get_args
from ciphie.Ciphie import Ciphie
from ciphie.n_grams import Frequencies
from ciphie.utils import list_to_str

BAR = '-' * 80
INDENT = '  '
    
class Highlighter:
    def __init__(self):
        self.highlight_map = {}

    def get(self, key):
        return self.highlight_map.get(key.upper(), None)

    
    def highlight(self, key, color):
        self.highlight_map[key.upper()] = color
    
    def unhighlight(self, key):
        self.highlight_map.pop(key.upper(), None)

    def __call__(self, key, char):
        key = key.upper()
        highlight_color = self.highlight_map.get(key)
        if highlight_color:
            return highlight_color + char + colors.ENDC
        else:
            return char


class KeyChar(str):
    def __init__(self, key: str):
        self.key = key

    def __hash__(self):
        return hash(self.key.casefold())

    def __eq__(self, other):
        return self.key.casefold() == other.key.casefold()

    def __str__(self):
        return self.key

    def __repr__(self):
        return self.key

class Key:
    def __init__(self, translation: Optional[Dict[int, int]] = None):
        self.value = OrderedDict({
            KeyChar(ch): ch for ch in string.ascii_lowercase
        })

        if translation:
            for k, v in translation.items():
                self.update(chr(k), chr(v))

    def update(self, key: str, val: str):
        self.value[KeyChar(key)] = val.lower()

    def translate(self, ch: str):
        return self.value.get(KeyChar(ch), ch)

    def get_translations(self, ch: str):
        ch = ch.lower()
        keys = []
        for k, v in self.value.items():
            if v == ch:
                keys.append(k)
        return keys
    
    def __str__(self):
        return list_to_str(self.value.keys()) + os.linesep + list_to_str(self.value.values())


class Repl:
    help_text = """
[letter][replacement]: replace [letter] with [replacement] and print the partially decoded ciphertext
key: print the current key
overlay: print the ciphertext with the current key overlaid
freq: print the current ciphertext frequencies
+[.][letter...]: highlight [letter] in the ciphertext
-[.][letter...]
?[.][letter]
q: quit
"""

    def __init__(self, ciphie: Ciphie, translation: Optional[Dict[int, int]] = None):
        self.ciphertext = ciphie.ciphertext
        self.frequencies = Frequencies(ciphie.alphabetic_ciphertext)
        self.key = Key(translation)
        self.highlighter = Highlighter()

    def print_ciphertext(self):
        buffer = [f"{BAR}{os.linesep}"]
        for ch in self.ciphertext:
            buffer.append(self.highlighter(ch, self.key.translate(ch)))
        buffer.append(f"{os.linesep}{BAR}")
        print(list_to_str(buffer))

    def print_overlay(self):
        buffer = [BAR]
        for line in self.ciphertext.splitlines():
            buffer.append(f'{colors.UNDERLINE}{line}{colors.ENDC}')
            line_buffer = []
            for ch in line:
                line_buffer.append(self.highlighter(ch, self.key.translate(ch)))
            buffer.append(list_to_str(line_buffer))
        buffer.append(BAR)
        print(os.linesep.join(buffer))

    def run(self):
        self.print_ciphertext()    
        print('Upper case letters are the original letters, lower case letters are the putative replacements.')
        print('Map a letter (BA) to see A substituted for B:')

        while True:
            try:
                prompt = input('> ')
                if not self.process_input(prompt):
                    break
            except (KeyboardInterrupt, EOFError):
                break        
            except Exception:
                print('an unexpected error occurred parsing your input')
                print(BAR)
                traceback.print_exc()
                print(BAR)

    def update_key(self, key, val):
        for translation in self.key.get_translations(val):
            self.highlighter.highlight(translation, colors.FAIL)

        self.highlighter.highlight(key.upper(), colors.OK_CYAN)
        self.key.update(key, val)
        self.print_ciphertext()

    def print_ciphertext_with_highlight(self, char):
        original_color = self.highlighter.get(char)
        self.highlighter.highlight(char, colors.WARNING)
        self.print_ciphertext()
        if original_color:
            self.highlighter.highlight(char, original_color)
        else:
            self.highlighter.unhighlight(char)
    
    def highlight_values(self, modifier, values):
        for ch in values:
            keys = self.key.get_translations(ch)
            if len(keys) == 1:
                self.highlight_keys(modifier, keys)
            else:
                key_str = f'{os.linesep}{INDENT}'.join(keys)
                print(f'ambiguous. there are multiple keys pointing to value "{ch}":\n{key_str}')

    def highlight_keys(self, modifier, keys):
        for ch in keys:
            if modifier == '+':
                self.highlighter.highlight(ch, colors.OK_CYAN)
            else:
                self.highlighter.unhighlight(ch)

    def process_highlight(self, prompt):
        if prompt[1] == '.':
            self.highlight_values(prompt[0], prompt[2:])
        else:
            self.highlight_keys(prompt[0], prompt[1:])
        self.print_ciphertext()

    def process_dot(self, prompt):
        keys = self.key.get_translations(prompt[1])
        if len(prompt) == 2:
            print(os.linesep.join(keys))
        elif len(prompt) == 3:
            if len(keys) == 1:
                self.update_key(keys[0], prompt[2])
            else:
                print('ambiguous. there are multiple keys with this value: ', keys)
        else:
            print('invalid input')
            
    def process_input(self, prompt):
        if prompt == 'q':
            return False
        
        if prompt == 'key':
            print(self.key)
        elif prompt == 'overlay':
            self.print_overlay()
        elif prompt == 'freq':
            self.frequencies.display()
        elif prompt == 'help':
            print(self.help_text)
        elif prompt.startswith('?'):
            self.print_ciphertext_with_highlight(prompt[1])
        elif prompt.startswith('+') or prompt.startswith('-'):
            self.process_highlight(prompt)
        elif prompt.startswith('.') and len(prompt) >= 2:
            self.process_dot(prompt)
        elif len(prompt) != 2 or not prompt.isalpha():
            print('input must be two letters')
        else:
            self.update_key(prompt[0], prompt[1])
        return True

def main():
    args, ciphertext = get_args()

    best_key = None
    ciphie = Ciphie(ciphertext, args.verbose)
    if args.decode:
        best_key = ciphie.decode()
    
    Repl(ciphie, best_key).run()

if __name__ == '__main__':
    main()