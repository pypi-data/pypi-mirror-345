import numpy as np
import random

chars = "~_-<>{}ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()"

def get_char():
   char_index = random.randint(1, len(chars)-1)
   char = chars[char_index]
   return char


###################################################################
def generate_3d_seq_puzzle():
    back_char = " "
    pat_len = random.randint(11,19)
    length = random.randint(pat_len-8,pat_len-5)
    structure_1 = np.full((length), back_char)
    structure_2 = np.full((length), back_char)
    structure_3 = np.full((length), back_char)
    shown = np.full((pat_len), 0)
    pattern = ""
    for i in range(0, pat_len):
        pattern = pattern + get_char()
    start_pos = 0 
    for i in range(0, length):
        structure_1[i] = pattern[i]
        shown[i] = 1
    start_pos = random.randint(0, pat_len-1)
    for i in range(0, length):
        pat_index = i + start_pos
        if pat_index>=pat_len:
            pat_index = pat_index%pat_len
        structure_2[i] = pattern[pat_index]
        shown[pat_index] = 1
    start_pos = random.randint(0, pat_len-1)
    for i in range(0, length):
        pat_index = i + start_pos
        if pat_index>=pat_len:
            pat_index = pat_index%pat_len
        structure_3[i] = pattern[pat_index]
        shown[pat_index] = 1
    answer = pattern
    for i in range(0, pat_len):
        if shown[i]==0:
            answer = answer[0:i] + "?" + answer[i+1:]
    return pattern, [structure_1, structure_2, structure_3], answer 

