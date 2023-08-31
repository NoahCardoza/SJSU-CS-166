import copy
import itertools
import string
from collections import Counter

from .n_grams import Frequencies, NGrams


class Ciphie:
    alphabet = string.ascii_lowercase

    def __init__(self, ciphertext):
        for ch in ciphertext.lower().replace('\n', '').replace('\r', ''):
            if ch not in Ciphie.alphabet:
                raise ValueError('Ciphertext contains non-alphabetic characters')
            
        self.best_key = string.ascii_lowercase
        
        self.ciphertext = ciphertext
        self.n_grams = NGrams()

    def guess_key_with_permutations(self):
        frequencies = Frequencies(self.ciphertext)
        initial_ciphertext_frequency_key = list(frequencies[1].keys())

        for ch in string.ascii_lowercase:
            if ch not in initial_ciphertext_frequency_key:
                initial_ciphertext_frequency_key.append(ch)
        initial_putative_key_order = list(self.n_grams[1].grams.keys())

        best_key = str.maketrans(
            ''.join(initial_ciphertext_frequency_key),
            ''.join(initial_putative_key_order)
        )
        decoded = self.ciphertext.translate(best_key)
        best_score = self.n_grams.score(Frequencies(decoded))
        
        print(decoded)
        print('initial score:', best_score)
        print(initial_putative_key_order)
        
        chunk_size = 7
        step = 3

        for index in reversed(range(0, len(initial_putative_key_order), step)):
            chunk = initial_putative_key_order[index:index + chunk_size]
            freq_chunk = initial_ciphertext_frequency_key[index:index + chunk_size]
            for perm in itertools.permutations(chunk):
                putative_key = copy.deepcopy(best_key)
                for (ch1, ch2) in zip(freq_chunk, perm):
                    putative_key[ord(ch1)] = ord(ch2)
                mc = Counter(best_key.values()).most_common()[0]
                if mc[1] > 1:
                    print('more than 1 val', chr(mc[0]))
                    return 0, {}
                decoded = self.ciphertext.translate(putative_key)
                score = self.n_grams.score(Frequencies(decoded))
                if score > best_score:
                    best_score = score
                    best_key = copy.deepcopy(putative_key)

                    _best_key_order = ''.join(chr(c) for c in best_key.keys())
                    _best_key = ''.join(chr(c) for c in best_key.values())
                    print('best_score:', best_score)
                    print(_best_key_order)
                    print(_best_key)
                    print(decoded)
        return best_score, best_key
    
    def guess_key_with_swaps(self, best_score, best_key_translations):
        best_key_order = ''.join(chr(c) for c in best_key_translations.keys())
        best_key = ''.join(chr(c) for c in best_key_translations.values())

        improvement = True
        while improvement:
            improvement = False
            for index in range(len(string.ascii_lowercase)):
                for i in range(index + 1, len(string.ascii_lowercase)):
                    current_key = list(best_key)
                    current_key[index], current_key[i] = current_key[i], current_key[index]
                    # print(current_key[index], current_key[i])
                    current_key = ''.join(current_key)

                    decoded = self.ciphertext.translate(str.maketrans(best_key_order, current_key))
                    score = self.n_grams.score(Frequencies(decoded))
                    if score > best_score:
                        improvement = True
                        best_score = score
                        best_key = current_key
                        # print(score)
                        # print(decoded)
        
        return best_score, str.maketrans(best_key_order, current_key)

    def decode(self):
        self.best_score, self.best_key = self.guess_key_with_permutations()
        print('best score after reverse permutations:', self.best_score)
        print(self.best_key)
        print(self.best_score)
        # self.best_score = 0.29097707100591713
        # self.best_key = {115: 101, 103: 116, 107: 97, 117: 111, 99: 105, 101: 110, 113: 115, 104: 114, 98: 104, 122: 108, 97: 100, 105: 99, 110: 109, 108: 102, 120: 117, 112: 103, 114: 121, 111: 119, 119: 98, 118: 118, 102: 107, 109: 112, 100: 106, 116: 122, 106: 120, 121: 113}

        # print(Counter(self.best_key.values()).most_common())
        
        # best_key_order = ''.join(chr(c) for c in self.best_key.keys())
        # best_key = ''.join(chr(c) for c in self.best_key.values())
        # print(best_key_order)
        # print(best_key)

        # self.best_score, self.best_key = self.guess_key_with_swaps(self.best_score, self.best_key)
        # print('best score after random swaps:', self.best_score)
        # best_key_order = ''.join(chr(c) for c in self.best_key.keys())
        # best_key = ''.join(chr(c) for c in self.best_key.values())
        # print(best_key_order)
        # print(best_key)

        return self.best_key


# ciphertext = """
# GBSXUCGSZQGKGSQPKQKGLSKASPCGBGBKGUKGCEUKUZKGGBSQEICA
# CGKGCEUERWKLKUPKQQGCIICUAEUVSHQKGCEUPCGBCGQOEVSHUNSU
# GKUZCGQSNLSHEHIEEDCUOGEPKHZGBSNKCUGSUKUASERLSKASCUGB
# SLKACRCACUZSSZEUSBEXHKRGSHWKLKUSQSKCHQTXKZHEUQBKZAEN
# NSUASZFENFCUOCUEKBXGBSWKLKUSQSKNFKQQKZEHGEGBSXUCGSZQ
# GKGSQKUZBCQAEIISKOXSZSICVSHSZGEGBSQSAHSGKHMERQGKGSKR
# EHNKIHSLIMGEKHSASUGKNSHCAKUNSQQKOSPBCISGBCQHSLIMQGKG
# SZGBKGCGQSSNSZXQSISQQGEAEUGCUXSGBSSJCQGCUOZCLIENKGCA
# USOEGCKGCEUQCGAEUGKCUSZUEGBHSKGEHBCUGERPKHEHKHNSZKGGKAD
# """

# Ciphie(ciphertext.lower()).decode()
