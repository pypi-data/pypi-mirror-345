import pandas as pd
import numpy as np
import argparse
import textwrap 
import sys
import os

# -*- coding: utf-8 -*-
  
"""
   enigme.cli: Command line interface for enigme puzzle generation.
"""

from enigme import __version__
from .gridbased import generate_fraction_puzzle
from .gridbased import grid_print_string
from .gridbased import generate_rotation_puzzle
from .seqbased import generate_sequence_puzzle

from .seqbased import generate_2d_physics_puzzle
from .gridbased import get_structure_print_string
from .physics_puzzle_3d import generate_3d_physics_puzzle
from .seq_puzzle_3d import generate_3d_seq_puzzle
from .numeric_puzzles import generate_1d_numeric_text_puzzle
from .numeric_puzzles import generate_1d_numeric_text_puzzle_v2
from .numeric_puzzles import generate_2d_numeric_text_puzzle
from .numeric_puzzles import generate_3d_numeric_text_puzzle

##########################################################################################
def print_usage(prog):
    """ Command line application usage instructions. """
    print(" USAGE ")
    print(" ", prog, "[OPTIONS] <PUZZLE> <DIMENSION> ")
    print("   <PUZZLE>            - PUZZLE CLASS [ numeric | sequence | physics ]")
    print("   <DIMENSION>         - PUZZLE CLASS [ 1d | 2d | 3d ]")
    print("   [OPTIONS]")
    print("      -v, --version    - Print version")
    print("      -u, --usage      - Print detailed usage info")
    print("      -h, --help       - Get command help")
    print("")


##########################################################################################
def main():
   parser = argparse.ArgumentParser()
   parser.add_argument('-v', '--version', help='Print Version', action='store_true')
   parser.add_argument('-u', '--usage', help='More detailed usage information', action='store_true')
   parser.add_argument('puzzle', help='Puzzle class: [ numeric | sequence | physics ]')
   parser.add_argument('dimension', help='Puzzle class: [ 1d | 2d | 3d ]')

   args = parser.parse_args()

   if args.version:
       print(" Version:", __version__)
       exit(1)

   if args.usage:
       print_usage("enigme")
       exit(1)

   if args.puzzle=='numeric':
      if args.dimension=='1d':
         print_1d_numeric_puzzle()
      if args.dimension=='2d':
         print_2d_numeric_puzzle()
      if args.dimension=='3d':
         print_3d_numeric_puzzle()

   if args.puzzle=='physics':
      if args.dimension=='1d':
         print_seq_puzzle()
      if args.dimension=='2d':
         print_2d_physics_puzzle()
      if args.dimension=='3d':
         print_3d_physics_puzzle()

   if args.puzzle=='sequence':
      if args.dimension=='1d':
         print_seq_puzzle()
      if args.dimension=='2d':
         print_grid_puzzle()
      if args.dimension=='3d':
         print_3d_seq_puzzle()

def print_clean_cli_text(toprint):
   wrapper = textwrap.TextWrapper(width=70)
   string = wrapper.fill(text=toprint) 
   print(string)


def print_1d_numeric_puzzle():
   text, answer = generate_1d_numeric_text_puzzle_v2()
   print()
   print_clean_cli_text(text)
   print()
   print("Press a key when you are ready to continue and see the answer...")
   print()
   input()
   print(answer)


def print_2d_numeric_puzzle():
   text, answer = generate_2d_numeric_text_puzzle()
   print()
   print_clean_cli_text(text)
   print()
   print("Press a key when you are ready to continue and see the answer...")
   print()
   input()
   print(answer)


def print_3d_numeric_puzzle():
   text, answer = generate_3d_numeric_text_puzzle()
   print()
   print_clean_cli_text(text)
   print()
   print("Press a key when you are ready to continue and see the answer...")
   print()
   input()
   print(answer)



##########################################################################################
def print_grid_puzzle():
   str1, str2, str3, str4 = generate_rotation_puzzle()
   print()
   print_clean_cli_text("Below you will see 3 patterns that form a sequence. Write down the expected 4th pattern in the sequence.")
   puzzle_str = get_structure_print_string([str1, str2, str3])
   print(puzzle_str) 
   print()
   print("Press enter when you are ready to continue and see the answer...")
   print()
   input()
   answer_str = get_structure_print_string([str4], 4)
   print(answer_str)

##########################################################################################
def print_frac_puzzle():
   fore, str1, numer, denom = generate_fraction_puzzle()
   print()
   print(f"What fraction of the characters in this grid are {fore}?")
   print()
   print(grid_print_string(str1))
   print()
   print("Press a key when you are ready to continue and see the answer...")
   input()
   answer_str = f"Answer:  {numer}/{denom}"
   print(answer_str)


##########################################################################################
def print_seq_puzzle():
   str1, str2, str3, str4 = generate_sequence_puzzle()
   print()
   print_clean_cli_text("Below you will see 3 strings of characters that form a pattern. What is the next pattern in the sequence?")
   print()
   print("1.    |" + ("".join(str1)) + "|")
   print()
   print("2.    |" + ("".join(str2)) + "|")
   print()
   print("3.    |" + ("".join(str3)) + "|")
   print()
   print("Press a key when you are ready to continue and see the answer...")
   print()
   input()
   print("      |" + ("".join(str4)) + "|" )
 
##########################################################################################
def print_3d_seq_puzzle():
   pattern, structs, answer = generate_3d_seq_puzzle()
   print()
   print_clean_cli_text(f"You are looking at a machine something like a slot machine. There is a sequence of characters printed onto the ege of a drum that spins inside the machine. You can only see a small window of this sequnce after every spin, but you know the whole pattern is {len(answer)} long. Below you will see the sequence of characters visible in the window after the first 3 spins. Write out the sequence as you can, using the ? character where you are not sure. Use the first visible sequence as the starting point.")
   print()
   print("1.    |" + ("".join(structs[0])) + "|")
   print()
   print("2.    |" + ("".join(structs[1])) + "|")
   print()
   print("3.    |" + ("".join(structs[2])) + "|")
   print()
   print("Press a key when you are ready to continue and see the answer...")
   print()
   input()
   print("      |" + ("".join(answer)) + "|" )

##########################################################################################
def print_3d_physics_puzzle():
   object, structures = generate_3d_physics_puzzle()
   print()
   print_clean_cli_text(f"You are hold a see through cube. There is an object inside the cube moving around with constant velocity and without losing momentum. Below you a sequence of grids. Each sequence of three represents 3 faces of the cube where you can see the object {object}. As the object moves its location insie the cube changes. It will bounce off the walls of the cube whenever it hits one of the edges. Draw the final set of three faces you would see after the next movement of the object.")
   print()
   for i in range(len(structures)-1):
      struct = structures[i]
      puzzle_str = get_structure_print_string(struct)
      print(f"At time {i} ")
      print(puzzle_str)
      print()
   print()
   print("Press a key when you are ready to continue and see the answer...")
   print()
   input()
   struct = structures[len(structures)-1]
   answer_str = get_structure_print_string(struct)
   print(answer_str)

##########################################################################################
def print_2d_physics_puzzle():
   str1, str2, str3, str4, str5 = generate_2d_physics_puzzle()
   print()
   print_clean_cli_text("Below you will see 4 strings of characters that represent physical objects moving in an enironment. Can you analyse the movement and determine the next pattern in the sequence?")
   print()
   print("1.    |" + ("".join(str1)) + "|")
   print()
   print("2.    |" + ("".join(str2)) + "|")
   print()
   print("3.    |" + ("".join(str3)) + "|")
   print()
   print("4.    |" + ("".join(str4)) + "|")
   print()
   print("Press a key when you are ready to continue and see the answer...")
   print()
   input()
   print("      |" + ("".join(str5)) + "|" )


##########################################################################################
if __name__ == '__main__':
    main()
