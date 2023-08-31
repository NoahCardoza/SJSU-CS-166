import os
import zipfile
from collections import Counter, OrderedDict, namedtuple

path_to_parent_folder = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(path_to_parent_folder, 'data')

Frequency = namedtuple('Frequency', ['count', 'percentage'])


class Frequencies:
    def __init__(self, ciphertext):    
        self.monograms = Frequencies.get_ciphertext_statistics(ciphertext, 1)
        self.diagrams = Frequencies.get_ciphertext_statistics(ciphertext, 2)
        self.trigrams = Frequencies.get_ciphertext_statistics(ciphertext, 3)
        self.quadgrams = Frequencies.get_ciphertext_statistics(ciphertext, 4)
        self.__dict__ = {
            1: self.monograms,
            2: self.diagrams,
            3: self.trigrams,
            4: self.quadgrams,
        }

    def __getitem__(self, index):
        return self.__dict__[index]
        
    @staticmethod
    def get_ciphertext_statistics(ciphertext: str, group_size: int = 1):
        ciphertext = ciphertext.replace('\n', '').replace('\r', '')
        
        l = len(ciphertext)
        groups = [ciphertext[i:i+group_size] for i in range(0, l, group_size)]
        c = Counter(groups)
        
        return OrderedDict(sorted(((ch, Frequency(freq, freq / l)) for ch, freq in c.items()), key=lambda x: x[1], reverse=True))


class NGram:
    max_depth = 10000

    def __init__(self, filename):
        self.filename = filename
        self.grams = OrderedDict()
        self.load()
    
    def load(self):
        if self.filename.endswith('.zip'):  
            with zipfile.ZipFile(self.filename, 'r') as z:
                with z.open(z.namelist()[0], 'r') as f:
                    self._load(f)
        else:
            with open(self.filename, 'rb') as f:
                self._load(f)
    
    def _load(self, f):
        for line, _ in zip(f, range(self.max_depth)):
            line = line.strip()
            if line:
                gram, count = line.decode('ascii').lower().split(' ')
                self.grams[gram] = int(count)
        self.set = set(self.grams.keys())

    def score(self, frequencies):
        total_keys = set(frequencies.keys())
        intersection = total_keys.intersection(self.set)
        return len(intersection) / len(self.set)


class NGrams:
    files = (
        'english_monograms.txt',
        'english_bigrams.txt',
        'english_trigrams.txt.zip',
        'english_quintgrams.txt.zip',
    )
    
    n_grams = {
        index + 1: NGram(os.path.join(data_folder, filename)) for index, filename in enumerate(files)
    }
    
    def __getitem__(self, index):
        return self.n_grams[index]
    
    def _score(self, frequencies):
        return {index: gram.score(frequencies[index]) for index, gram in self.n_grams.items()}
    
    def score(self, frequencies):
        scores = self._score(frequencies)
        # scores.pop(1, None)
        return sum(scores.values()) / len(scores)
