def list_to_str(lst):
    return ''.join(lst)

def chr_list_to_str(chr_list):
    return list_to_str(chr(c) for c in chr_list)