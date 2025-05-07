import numpy as np
import random

#chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890&%$#@"

chars = "~_<>{}ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()"

def get_char():
   char_index = random.randint(1, len(chars)-1)
   return chars[char_index]

backchars = " .,'-"

def get_backchar():
   char_index = random.randint(1, len(backchars)-1)
   return  backchars[char_index]

###################################################################
def generate_fraction_puzzle():
    back_char = get_backchar()
    fore_char = get_char()
    width = random.randint(4,5)
    height = random.randint(3,5)
    structure_1 = np.full((height, width), back_char)
    prob_of_fore = random.randint(20,70)/100
    denom = width * height
    numerator = 0
    for i in range(0, height):
        for j in range(0, width):
            temp = random.random()
            if temp<prob_of_fore:
                structure_1[i,j] = fore_char
                numerator += 1
    return fore_char, structure_1, numerator, denom


###################################################################
def generate_rotation_puzzle():
    back_char = get_backchar()
    side_length = random.randint(2,6)
    structure_1 = np.full((side_length, side_length), back_char)
    prob_of_fore = random.randint(20,80)/100
    empty = True
    while empty:
        for i in range(0, side_length):
            for j in range(0, side_length):
                temp = random.random()
                if temp<prob_of_fore:
                    structure_1[i,j] = get_char()
                    empty = False
    reverse = (random.random() < 0.5)
    structure_2 = np.rot90(structure_1)
    structure_3 = np.rot90(structure_2)
    structure_4 = np.rot90(structure_3)
    if reverse:
        tempy = structure_2
        structure_2 = structure_4
        structure_4 = tempy
    return structure_1, structure_2, structure_3, structure_4
  
###################################################################
def get_out_str(row_data):
    out = "|"
    for i in range(0, len(row_data)):
        if i>0:
            #out = out + "|-|"
            out = out + "|"
        out = out + row_data[i]
    out = out + "|"
    return out

###################################################################
def get_separator(side_length):
    return "-"*(side_length*2+1)


###################################################################
def grid_print_string(str_in, indent=5):
    """
    Create a print string for a grid of chars
    """
    output = ""
    indent_spacer = " " * indent
    rows = str_in.shape[0]
    for row in range(0,rows):
        out1 =  " ".join(str_in[row,:])
        output += indent_spacer + out1 + "\n"
    return output

###################################################################
def structure_print_string(str1, str2, str3):
    """
    Create a print string for a set of structures
    """
    output = ""
    spacer = "     "
    indent = 3
    indent_spacer = " " * indent
    data_temp = get_out_str(str1[0,:])
    width = len(data_temp)
    extra_spacer = " " * (width-2)
    output += indent_spacer + "1" + extra_spacer + spacer + "2" + extra_spacer + spacer + "3" + extra_spacer + "\n"
    separ = get_separator(side_length)
    for row in range(0,side_length):
        out1 = get_out_str(str1[row,:])
        out2 = get_out_str(str2[row,:])
        out3 = get_out_str(str3[row,:])
        output += indent_spacer + out1 + spacer + out2 + spacer + out3 + "\n"
    return output


###################################################################
def get_structure_print_string(structs: list[np.array], index_start=1):
    """
    Create a print string for a set of structures
    """
    output = ""
    spacer = "     "
    indent = 3
    indent_spacer = " " * indent
    str1 = structs[0]
    side_length = len(str1[0,:])
    data_temp = get_out_str(str1[0,:])
    width = len(data_temp)
    extra_spacer = " " * (width-2)
    output += indent_spacer 
    for i in range(len(structs)):
        output += str(i+index_start) + extra_spacer + spacer 
    output += "\n"
    separ = get_separator(side_length)
    for row in range(0,side_length):
        output += indent_spacer
        for i in range(len(structs)):
            temp = get_out_str(structs[i][row,:])
            output += temp + spacer
        output += "\n"
    return output



