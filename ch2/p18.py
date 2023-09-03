key = (
  (0b000, 'e',),
  (0b001, 'h',),
  (0b010, 'i',),
  (0b011, 'k',),
  (0b100, 'l',),
  (0b101, 'r',),
  (0b110, 's',),
  (0b111, 't',),
)

def char_to_bin(ch: str):
    for binary, c in key:
        if c == ch:
            return binary
        
def bin_to_char(binary: int):
    for b, char in key:
        if b == binary:
            return char

def find_key_for(ciphertext: str, plaintext: str):
    return ''.join(
        bin_to_char(char_to_bin(ci_char) ^ char_to_bin(pl_char)) 
        for ci_char, pl_char in zip(ciphertext, plaintext)
      )
        
ciphertext = 'KITLKE'
plaintexts = ['thrill', 'tiller',]

for plaintext in plaintexts:
    print(find_key_for(ciphertext.lower(), plaintext))