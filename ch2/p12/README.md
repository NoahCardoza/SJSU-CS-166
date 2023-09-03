# Ciphie

## Introduction

This is a simple program that will help decrypt simple substitution ciphers. It uses a frequency analysis to determine
the most likely mapping of letters to other letters. It also provides a REPL for manual decryption.

## Usage

```bash
$ python -m ciphie -h
usage: ciphie [-h] [-i INPUT] [-v] [-d]

Ciphie

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        File input (default: stdin)
  -v, --verbose         Verbose output
  -d, --decode          Attempt to break ciphertext before entering REPL
```

# Credits

Word lists found at http://practicalcryptography.com/cryptanalysis/letter-frequencies-various-languages/english-letter-frequencies/
