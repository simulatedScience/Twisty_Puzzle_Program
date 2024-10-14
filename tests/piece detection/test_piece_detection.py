"""
This module implements functions to visualize piece detection on a puzzle.

1. load a puzzle from a file
2. calculate pieces
3. visualize pieces in 3D plot (show points with a random unique color per piece)

Step 3 should be available to call from within the piece detection function(s) to monitor progress through the iterations.
"""

import os, sys, inspect
import random

import vpython as vpy

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir2 = os.path.dirname(parentdir)
sys.path.insert(0,parentdir2) 
from src.puzzle_class import Twisty_Puzzle
from src.interaction_modules.colored_text import colored_text

ALL_PUZZLES = [f for f in os.listdir(os.path.join("src", "puzzles")) if os.path.isdir(os.path.join("src", "puzzles", f))]

COMMAND_COLORS = {
    "command": "#ff8800", # orange
    "arguments": "#5588ff", # blue
    "headline": "#22dd22", # green
}

PIECE_COLORS: list[tuple[int, int, int]] = list()

def load_puzzle() -> Twisty_Puzzle:
    """
    Load a puzzle from a puzzle name given by the user through a CLI input.
    
    `load_puzzle` code copied from `tests/algorithm_generator.main()`
    
    Returns:
        (Twisty_Puzzle): the loaded puzzle object
    """
    print(f"Available puzzles: {colored_text(', '.join(ALL_PUZZLES), COMMAND_COLORS['arguments'])}")


    # print(f"Enter {colored_text('exit', COMMAND_COLORS['command'])} to quit the program.")

    puzzle: Twisty_Puzzle = Twisty_Puzzle()
    puzzle_name = input("Enter a puzzle name: ")
    # puzzle_name = "rubiks_2x2"
    # puzzle_name = "geared_mixup"
    puzzle.load_puzzle(puzzle_name)
    return puzzle

def show_pieces_on_puzzle(puzzle: Twisty_Puzzle, pieces: list[set[int]]) -> list[tuple[int, int, int]]:
    """
    Show given pieces on a given puzzle by coloring the points associated with each piece in a random color. Any points with the same color belong to the same piece, points with different colors belong to different pieces.

    Args:
        puzzle (Twisty_Puzzle): the puzzle object
        pieces (list[set[int]]): list of sets of points that represent the pieces

    Returns:
        list[tuple[int, int, int]]: list of colors assigned to each piece
    """
    # get vpy points from puzzle
    vpy_objects = puzzle.vpy_objects
    assert len(vpy_objects) == sum([len(piece) for piece in pieces]), "Number of points in pieces does not match number of points in puzzle."

    # assign colors to each piece and apply to vpy_objects
    for i, piece in enumerate(pieces):
        if i < len(PIECE_COLORS):
            color = PIECE_COLORS[i]
        else:
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            PIECE_COLORS.append(color)
        vpy_color = vpy.vector(color[0]/255, color[1]/255, color[2]/255)
        for point in piece:
            # apply color to point
            vpy_objects[point].color = vpy_color

    print(f"Colored {len(pieces)} pieces in 3D viewport")

    return PIECE_COLORS

if __name__ == "__main__":
    load_puzzle()
