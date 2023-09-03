import os
import re
import string
import time
from typing import List

from ciphie.n_grams import Frequencies, NGrams
from ciphie.utils import chr_list_to_str, list_to_str

RE_NON_ALPHABETIC = re.compile(r'[^a-z]')

class Ciphie:
    alphabet = string.ascii_lowercase

    def __init__(self, ciphertext, verbose=False):
        self.best_key = string.ascii_lowercase
        self.verbose = verbose
        self.ciphertext = ciphertext.lower()
        self.alphabetic_ciphertext = RE_NON_ALPHABETIC.sub('', self.ciphertext)
        self.n_grams = NGrams()

    def _report(self, ciphertext, score, translation):
        if not self.verbose:
            return
        
        buffer = []

        best_key_order = chr_list_to_str(translation.keys())
        best_key = chr_list_to_str(translation.values())

        buffer.append(f'score: {score}')
        buffer.append('key:')
        buffer.append(f'  {best_key_order}')
        buffer.append(f'  {best_key}')
        buffer.append('decoded:')
        buffer.append(ciphertext.translate(translation))
        print(os.linesep.join(buffer))

    def report(self, score=None, key=None):
        self._report(self.ciphertext, score or self.best_score, key or self.best_key)

    @staticmethod
    def get_cipher_alphabet_in_frequency_order(ciphertext: str) -> List[str]:
        cipher_alphabet_in_frequency_order = list(Frequencies.get_ciphertext_statistics(ciphertext, 1).keys())

        # ensure all letters are present
        for ch in string.ascii_lowercase:
            if ch not in cipher_alphabet_in_frequency_order:
                cipher_alphabet_in_frequency_order.append(ch)
        
        return cipher_alphabet_in_frequency_order
    
    def guess_initial_key(self):
        cipher_alphabet_in_frequency_order = self.get_cipher_alphabet_in_frequency_order(self.alphabetic_ciphertext)
        common_alphabet_in_frequency_order = self.n_grams.get_common_alphabet_in_frequency_order()

        best_key = str.maketrans(
            list_to_str(cipher_alphabet_in_frequency_order),
            list_to_str(common_alphabet_in_frequency_order)
        )

        decoded = self.alphabetic_ciphertext.translate(best_key)
        best_score = self.n_grams.score(decoded)

        return best_score, best_key
        
    def guess_key_with_swaps(self, best_score, best_key_translations):
        cipher_alphabet = chr_list_to_str(best_key_translations.keys())
        best_key = chr_list_to_str(best_key_translations.values())
        alphabet_length = len(string.ascii_lowercase)
        improvement = True
        
        while improvement:
            improvement = False
            for i in range(alphabet_length):
                for j in range(i + 1, alphabet_length):
                    current_key = list(best_key)
                    current_key[i], current_key[j] = current_key[j], current_key[i]
                    current_key = ''.join(current_key)

                    translation = str.maketrans(cipher_alphabet, current_key)
                    decoded = self.alphabetic_ciphertext.translate(translation)
                    score = self.n_grams.score(decoded)
                    if score > best_score:
                        improvement = True
                        best_score = score
                        best_key = current_key
                        self.report(best_score, translation)
        
        return best_score, str.maketrans(cipher_alphabet, current_key)

    def decode(self):
        start = time.time()
        self.best_score, self.best_key = self.guess_initial_key()
        self.report()
        self.best_score, self.best_key = self.guess_key_with_swaps(self.best_score, self.best_key)
        self.report()
        end = time.time()
        if self.verbose:
            print(f'elapsed: {round(end - start, 2)}s')
        return self.best_key


if __name__ == '__main__':
    ciphertext = """GBSXUCGSZQGKGSQPKQKGLSKASPCGBGBKGUKGCEUKUZKGGBSQEICA
CGKGCEUERWKLKUPKQQGCIICUAEUVSHQKGCEUPCGBCGQOEVSHUNSU
GKUZCGQSNLSHEHIEEDCUOGEPKHZGBSNKCUGSUKUASERLSKASCUGB
SLKACRCACUZSSZEUSBEXHKRGSHWKLKUSQSKCHQTXKZHEUQBKZAEN
NSUASZFENFCUOCUEKBXGBSWKLKUSQSKNFKQQKZEHGEGBSXUCGSZQ
GKGSQKUZBCQAEIISKOXSZSICVSHSZGEGBSQSAHSGKHMERQGKGSKR
EHNKIHSLIMGEKHSASUGKNSHCAKUNSQQKOSPBCISGBCQHSLIMQGKG
SZGBKGCGQSSNSZXQSISQQGEAEUGCUXSGBSSJCQGCUOZCLIENKGCA
USOEGCKGCEUQCGAEUGKCUSZUEGBHSKGEHBCUGERPKHEHKHNSZKGGKAD
"""

    Ciphie(ciphertext).decode()
