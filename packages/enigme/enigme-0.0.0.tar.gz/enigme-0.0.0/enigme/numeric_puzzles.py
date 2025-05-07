import numpy as np
import random

chars = "^*%$#@"

###################################################################
def get_char():
   char_index = random.randint(1, len(chars)-1)
   char = chars[char_index]
   return char


###################################################################
def generate_1d_numeric_text_puzzle():
    """ 
    First numeric puzzle is designed to test how well an agent can use language
    as simultaneously the source of puzzle semantics, 
    as well as a set of abstract entities which
    need to be reasoned about numerically.
    """
    char = get_char()
    text_content = get_1d_numeric_text_puzzle_text()
    wds = text_content.split(" ")
    index = random.randint(0,int(len(wds)/3))
    answer = ""
    complete = False
    while not complete:
        word = wds[index]
        letter_index = random.randint(0,len(word)-1)
        while not word[letter_index].isalnum():
            letter_index = random.randint(0,len(word)-1)
        new_word = word[0:letter_index] + char + word[letter_index+1:]
        answer += str(letter_index+1)
        wds[index] = new_word
        if (len(wds)-index) < 4:
            complete = True
        else:
            index = random.randint(index+1,len(wds)-1)
    return " ".join(wds), answer
 

def generate_1d_numeric_text_puzzle_v2():
    """
    A variation numeric puzzle that is designed to illustrate how well an 
    agent can use language as simultaneously the source of semantics, as well 
    as a set of abstract entities which
    need to be reasoned about numerically. This version introduces the additional complexity
    of needing to understand and maintain a mental model of the mapping between characters 
    and numbers.
    """
    char = get_char()
    text_content = "In this block of text you will find an additional character inserted into some of the words to replace a letter. Each letter has a numeric value coming from its position in the alphabet, letter a is one, letter b is two, etc. Add each of these number together to get the final number. Write that number below."
    wds = text_content.split(" ")
    index = random.randint(0,int(len(wds)/3))
    answer = 0
    complete = False
    while not complete:
        word = wds[index]
        letter_index = random.randint(0,len(word)-1)
        this_char = word[letter_index:letter_index+1].upper()
        value = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".find(this_char)+1 
        new_word = word[0:letter_index] + char + word[letter_index+1:]
        answer += value
        wds[index] = new_word
        if (len(wds)-index) < 4:
            complete = True
        else:
            index = random.randint(index+1,len(wds)-1)
    return " ".join(wds), answer


def get_1d_numeric_text_puzzle_text():
    """
    Function for creating subtle variations of the puzzle text content so that the problem
    space is increased while the semantics remain the same.
    """
    variations = {
        "VAR1":["your will find", "there is", "you will see"],
        "VAR2":["inserted into some of", "inserted inside some of", "placed within some of"],
        "VAR3":["replace a letter", "replace one of the letters", "substitute for a letter"],
        "VAR4":["position", "location"],
        "VAR5":["determines", "defines", "reveals"],
        "VAR6":["digits", "numerals"],    
    }   
    text_content = "In this block of text <VAR1> a non-alphabetic character <VAR2> the words to <VAR3>. The <VAR4> of this character within each word <VAR5> its numeric value. These numbers are <VAR6> in a sequence that forms a larger number. Write that number below."
    for key in variations.keys():
        subs = variations[key]
        index = random.randint(0, len(subs)-1)
        subbie = subs[index]
        target = "<" + key + ">"
        text_content = text_content.replace(target, subbie)
    return text_content


#############################################################################
def generate_2d_numeric_text_puzzle():
    char = get_char()
    text_content = get_2d_numeric_text_puzzle_text()
    wds = text_content.split(" ")
    index = random.randint(0,len(wds)-1)
    answer = ""
    word = wds[index]
    letter_index = random.randint(0,len(word)-1)
    new_word = word[0:letter_index] + char + word[letter_index+1:]
    answer = (index+1) - (letter_index+1)
    answer = str(answer)
    wds[index] = new_word
    return " ".join(wds), answer



def get_2d_numeric_text_puzzle_text():
    """
    Function for creating subtle variations of the puzzle text content so that the problem
    space is increased while the semantics remain the same.
    """
    variations = {
        "VAR1":["your will find", "there is", "you will see"],
        "VAR2":["inserted into", "inserted inside", "placed within"],
        "VAR3":["replace a letter", "replace one of the letters", "substitute for a letter"],
        "VAR4":["position", "location"],
        "VAR5":["determine", "define", "reveal"],
        "VAR6":["derived", "determined"],
    }
    text_content = "In this block of text <VAR1> an additional character <VAR2> one of the words to <VAR3>. The <VAR4> of this character will <VAR5> two numerical values. The first value is <VAR6> from the number of the word within the sequence of words in this paragraph, where the first word has value one, the second word value two, etc. The second value comes from the position of the character within the word, if it replaces the first letter it has value one, the second letter value two, etc. You need to subtract the second number from the first and then write the resulting number below."
    for key in variations.keys():
        subs = variations[key]
        index = random.randint(0, len(subs)-1)
        subbie = subs[index]
        target = "<" + key + ">"
        text_content = text_content.replace(target, subbie)
    return text_content



operations = {
   "minus": "subtraction",
   "add": "addition"
}
opkeys = list(operations.keys())

def get_alphabetic_value(char):
    return ord(char.lower()) - 96

#############################################################################
def generate_3d_numeric_text_puzzle():
    """
    Extension of the above framework, but we now replace characters in three different words
    the instructions are to use the word position of the first, the letter position of the
    second and the alphabetic position of the third. We then combine them with either a series
    of addition subtraction or multiplication operations.
    """
    char = get_char()
    if random.uniform(0,1) > 0.5:
        opkey = opkeys[1]
    else:
        opkey = opkeys[0]   

    opname = operations[opkey]
    text_content = get_3d_numeric_text_puzzle_text(opname, opkey)
    wds = text_content.split(" ")
    index = random.randint(0,len(wds)-1)
    answer = ""
    word = wds[index]
    letter_index = random.randint(0,len(word)-1)
    replaced = word[letter_index]
    new_word = word[0:letter_index] + char + word[letter_index+1:]
    alpha_index = get_alphabetic_value(replaced)

    if opname=="addition": 
        answer = (index+1) + (letter_index+1) + alpha_index
   
    if opname=="subtraction": 
        answer = (index+1) - (letter_index+1) - alpha_index
   
    answer = str(answer)
    wds[index] = new_word
    return " ".join(wds), answer

#############################################################################
def get_3d_numeric_text_puzzle_text_var():
    return ""

#############################################################################
def get_3d_numeric_text_puzzle_text(op1="subtraction", op2="subtract"):
    """
    Function for creating subtle variations of the puzzle text content so that the problem
    space is increased while the semantics remain the same.
    """
    variations = {
        "VAR1":["your will find", "there is", "you will see"],
        "VAR2":["inserted into", "inserted inside", "placed within"],
        "VAR3":["replace a letter", "replace one of the letters", "substitute for a letter"],
        "VAR4":["position", "location"],
        "VAR5":["determine", "define", "reveal"],
        "VAR6":["derived", "determined"],
        "VAR7":["replaced", "substituted", "changed"],
    }
    text_content = "In this block of text <VAR1> an additional character <VAR2> one of the words to <VAR3>. This character and its <VAR4> will <VAR5> three numerical values. The first value is <VAR6> from the number of the word within the sequence of words in this paragraph, where the first word has value one, the second word value two, etc. The second value comes from the position of the character within the word, if it replaces the first letter it has value one, the second letter value two, etc. The final value comes from the position of <VAR7> letter in the alphabet, a is 1, b is 2, etc. You need to combine these numbers using " + op1 + ". First calculate number 1 " + op2 + " number 2, then take the result and " + op2 + " number 3. Write the resulting number below."
    for key in variations.keys():
        subs = variations[key]
        index = random.randint(0, len(subs)-1)
        subbie = subs[index]
        target = "<" + key + ">"
        text_content = text_content.replace(target, subbie)
    return text_content



