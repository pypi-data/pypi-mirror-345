import numpy as np
import random

chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890&%$#@"

phys_chars = "0IOo-=><Xx"

back_chars = ".,_'`"

def get_char(back_char):
   char_index = random.randint(1, len(chars))
   if char_index==len(chars):
       return back_char
   char = chars[char_index]
   return char

def get_back_char():
   char_index = random.randint(1, len(back_chars)-1)
   char = back_chars[char_index]
   return char

def get_phys_char(back_char):
   char_index = random.randint(1, len(phys_chars)-1)
   char = phys_chars[char_index]
   return char

###################################################################
def generate_2d_physics_puzzle():
    back_char = get_back_char()
    pat_len = random.randint(1,4)
    length = random.randint(pat_len+9,23)
    structure_1 = np.full((length), back_char)
    structure_2 = np.full((length), back_char)
    structure_3 = np.full((length), back_char)
    structure_4 = np.full((length), back_char)
    structure_5 = np.full((length), back_char)
    pattern = ""
    increment = random.randint(1,5)
    for i in range(0, pat_len):
        pattern = pattern + get_phys_char(back_char)
    start_pos = random.randint(0, length-pat_len-1)
    forward = (random.uniform(0,1) <= 0.6)
    direc = np.where(forward, 1, -1)
    variable = (random.uniform(0,1) <= 0.6)
    rebound = (random.uniform(0,1) <= 0.6)
    if increment<3:
        variable=False
    positions = [start_pos]*5
    for p in range(0, pat_len):
        structure_1[start_pos+p] = pattern[p]

    structures = [structure_1, structure_2, structure_3, structure_4, structure_5]
    for i in range(1,5):
        structure = structures[i]
        starter = positions[i-1]
        changer = direc * increment
        new_pos = starter + changer
        if rebound:
            if (new_pos < 0):
                new_pos = 0 - new_pos
                direc = 1
            if (new_pos > (length-pat_len)):
                new_pos = length - (new_pos-(length-pat_len))
                direc = -1
        else:
            if (new_pos < 0):
                new_pos = length + new_pos - 1
            if (new_pos >= length):
                new_pos = (new_pos-length)
        positions[i] = new_pos
        for p in range(0, pat_len):
            if (new_pos+p)<length:
               location = new_pos+p
            else:
               location = (new_pos+p)-length
            structure[location] = pattern[p]
        # Now make adjustments before the next pattern.             
        if variable:
            if increment>0:
                increment -= 1
    return structure_1, structure_2, structure_3, structure_4, structure_5


###################################################################
def generate_sequence_puzzle():
    back_char = get_back_char()
    pat_len = random.randint(3,7)
    length = random.randint(pat_len+7,29)
    structure_1 = np.full((length), back_char)
    structure_2 = np.full((length), back_char)
    structure_3 = np.full((length), back_char)
    structure_4 = np.full((length), back_char)
    pattern = ""
    increment = random.randint(1,3)
    for i in range(0, pat_len):
        pattern = pattern + get_char(back_char)
    start_pos = random.randint(0, length-pat_len-(3*increment))
    if random.uniform(0,1) < 0.5:
        for i in range(0, pat_len):
            structure_1[start_pos+i] = pattern[i] 
            structure_2[start_pos+i+(1*increment)] = pattern[i] 
            structure_3[start_pos+i+(2*increment)] = pattern[i] 
            structure_4[start_pos+i+(3*increment)] = pattern[i] 
    else:
        for i in range(0, pat_len):
            structure_1[start_pos+i+(3*increment)] = pattern[i]
            structure_2[start_pos+i+(2*increment)] = pattern[i]
            structure_3[start_pos+i+(1*increment)] = pattern[i]
            structure_4[start_pos+i] = pattern[i]
    return structure_1, structure_2, structure_3, structure_4
 
