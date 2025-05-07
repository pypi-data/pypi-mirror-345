import numpy as np
import random

chars = "xXqQGDCSoO0*+^?&%$#@"

def get_char():
   char_index = random.randint(1, len(chars)-1)
   return chars[char_index]

backchars = ".,'`"

def get_backchar():
   char_index = random.randint(1, len(backchars)-1)
   return  backchars[char_index]


def get_structures(x_pos, y_pos, z_pos, side_length, back_char, piece):
    structure_1 = np.full((side_length, side_length), back_char)
    structure_2 = np.full((side_length, side_length), back_char)
    structure_3 = np.full((side_length, side_length), back_char)
    structure_1[x_pos,y_pos] = piece
    structure_2[x_pos,z_pos] = piece
    structure_3[y_pos,z_pos] = piece
    return [structure_1, structure_2, structure_3]

###################################################################
def generate_3d_physics_puzzle():
    back_char = get_backchar()
    piece = get_char()
    side_length = random.randint(3,6)
    final_pos = side_length-1
    x_vel = random.randint(-1,1) 
    y_vel = random.randint(-1,1) 
    z_vel = random.randint(-1,1) 
    x_pos = random.randint(0,final_pos)
    y_pos = random.randint(0,final_pos)
    z_pos = random.randint(0,final_pos)
    structures = []
    structures.append(get_structures(x_pos, y_pos, z_pos, side_length, back_char, piece))
    for i in range(4):
        if x_pos==0 and x_vel==-1:
           x_vel = 1
        if y_pos==0 and y_vel==-1:
           y_vel = 1
        if z_pos==0 and z_vel==-1:
           z_vel = 1
        if x_pos==final_pos and x_vel==1:
           x_vel = -1
        if y_pos==final_pos and y_vel==1:
           y_vel = -1
        if z_pos==final_pos and z_vel==1:
           z_vel = -1
        x_pos+=x_vel
        y_pos+=y_vel
        z_pos+=z_vel
        structures.append(get_structures(x_pos, y_pos, z_pos, side_length, back_char, piece))
    return piece, structures
  
###################################################################
def get_out_str(row_data):
    out = "|"
    for i in range(0, len(row_data)):
        if i>0:
            out = out + "|-|"
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



