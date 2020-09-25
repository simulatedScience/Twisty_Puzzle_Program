# Twisty_Puzzle_Program
A Program to digitalize twisty puzzles, save algorithms as well as solving strategies for them and solve them with an AI based on Q-Learning and Neural Networks.

An Overview of all implemented and many planned features can be found in the following document:
https://docs.google.com/spreadsheets/d/1wllITKTaytmOBHMQu9dV0tIj7YtT3UqvB0RRak2qMqk/edit?usp=sharing

# Requirements
The program requires `python 3.x`. It is written and tested in python version `3.8.5`. Backwards compatibility is not guarantied.

Additionally some libraries are required. Those are:
- `vpython` - for 3D visualisation
- `colored` - for colored console output
- `lxml` - for saving and loading the puzzles
- `sympy` - for some automatic analysis of puzzles

All of them can be easily installed with `pip install ... `.

# Documentation
The repository has a folder `Documentation` which should include links to markdown files with explanation of the implementation of many features. There is no user manual yet.

Currently the program is supposed to be used via a command-line interface. A proper user interface soon is planned but can still take a long time as I still need to find a better way to implement that.