import os
import traceback
from typing import Dict, Optional

from ciphie import colors
from ciphie.Ciphie import Ciphie
from ciphie.Highlighter import Highlighter
from ciphie.Key import Key
from ciphie.n_grams import Frequencies
from ciphie.strings import BAR, INDENT
from ciphie.utils import list_to_str

help_text = f"""
{colors.BOLD}[letter][replacement]{colors.ENDC}: replace [letter] with [replacement] and print the partially decoded ciphertext
{colors.BOLD}key{colors.ENDC}: print the current key
{colors.BOLD}overlay{colors.ENDC}: print the ciphertext with the current key overlaid
{colors.BOLD}freq{colors.ENDC}: print the current ciphertext frequencies
{colors.BOLD}+(.)[letter...]{colors.ENDC}: highlight [letter] in the ciphertext. if "." is present, highlight all ciphertext letters translated to this value
{colors.BOLD}-(.)[letter...]{colors.ENDC}: unhighlight [letter] in the ciphertext. if "." is present, unhighlight all ciphertext letters translated to this value
{colors.BOLD}?(.)[letter]{colors.ENDC}: highlight [letter] in the ciphertext with yellow only in the next print.
{colors.BOLD}[letter][replacement]{colors.ENDC}: replace [letter] in the ciphertext with [replacement] and print the partially decoded ciphertext
{colors.BOLD}.[letter][replacement]{colors.ENDC}: replace [letter] in the decoded ciphertext with [replacement] and print the partially decoded ciphertext
{colors.BOLD}q{colors.ENDC}: quit
"""

class Repl:
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
        print('Type help to see the menu of commands:')

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
            print(help_text)
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