import os
import string
from collections import OrderedDict
from typing import Dict, Optional

from ciphie.utils import list_to_str


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