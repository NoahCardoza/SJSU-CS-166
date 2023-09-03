import os
import re
import zipfile
from collections import Counter, OrderedDict, namedtuple

path_to_parent_folder = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(path_to_parent_folder, 'data')

Frequency = namedtuple('Frequency', ['count', 'percentage'])


class Frequencies:
    def __init__(self, ciphertext):
        self.monograms = self.get_ciphertext_statistics(ciphertext, 1)
        self.diagrams = self.get_ciphertext_statistics(ciphertext, 2)
        self.trigrams = self.get_ciphertext_statistics(ciphertext, 3)
        self.quintgrams = self.get_ciphertext_statistics(ciphertext, 4)

        self.__dict__[1] = self.monograms
        self.__dict__[2] = self.diagrams
        self.__dict__[3] = self.trigrams
        self.__dict__[4] = self.quintgrams

    def __getitem__(self, index):
        return self.__dict__[index]
    
    @staticmethod
    def _display_n_gram(stats):
        for (ch, freq) in stats.items():
            if freq.percentage >= 0.01:
                print("{}: {:.2f}%".format(ch, freq.percentage))


    def display(self):
        print('Character frequencies:')
        self._display_n_gram(self.monograms)
        print('Digram frequencies:')
        self._display_n_gram(self.diagrams)
        print('Trigram frequencies:')
        self._display_n_gram(self.trigrams)
        print('Quintgrams frequencies:')
        self._display_n_gram(self.quintgrams)
        
    @staticmethod
    def get_ciphertext_statistics(ciphertext: str, group_size: int = 1):        
        l = len(ciphertext)
        groups = [ciphertext[i:i+group_size] for i in range(0, l, group_size)]
        c = Counter(groups)
        
        return OrderedDict(sorted(((ch, Frequency(freq, freq / l)) for ch, freq in c.items()), key=lambda x: x[1], reverse=True))


class NGramFile:
    def __init__(self, filename):
        self.filename = filename
        self.zp = None
        self.fp = None
        
    def __enter__(self):
        if self.filename.endswith('.zip'):  
            self.zp = zipfile.ZipFile(self.filename, 'r')
            self.fp = self.zp.open(self.zp.namelist()[0], 'r')
        else:
            self.fp = open(self.filename, 'rb')
        return self.fp
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.fp:
            self.fp.close()
        if self.zp:
            self.zp.close()
    

class NGram:
    def __init__(self, filename, max_entries=5000):
        self.db = self._load(filename, max_entries)
        self.set = set(self.db.keys())
    
    @staticmethod
    def _load(filename, max_entries):
        db = OrderedDict()
        with NGramFile(filename) as f:
            total = 0
            for line, _ in zip(f, range(max_entries)):
                line = line.strip()
                if line:
                    gram, raw_count = line.decode('ascii').lower().split(' ')
                    count = int(raw_count)
                    total += count
                    db[gram] = count
            
            for gram in db:
                db[gram] /= total
        return db

    def score(self, frequencies):
        total_keys = set(frequencies.keys())
        intersection = total_keys.intersection(self.set)
        return sum(self.db[gram] for gram in intersection)


class NGrams:
    files = (
        'english_monograms.txt',
        'english_bigrams.txt',
        'english_trigrams.txt.zip',
        'english_quintgrams.txt.zip',
    )
    
    db = {
        index + 1: NGram(os.path.join(data_folder, filename)) for index, filename in enumerate(files)
    }
    
    def __getitem__(self, index):
        return self.db[index]
    
    def get_common_alphabet_in_frequency_order(self):
        return self.db[1].db.keys()
    
    def score(self, ciphertext):
        # exclude remove monograms from score
        scores = {
            i: self.db[i].score(Frequencies.get_ciphertext_statistics(ciphertext, i)) 
            for i in [2, 3, 4]
        }
        return sum(scores.values()) / len(scores)
