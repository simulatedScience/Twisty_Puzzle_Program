# Twisty_Puzzle_Program
A Program to digitalize twisty puzzles, save algorithms as well as solving strategies for them and solve them with an AI based on Q-Learning and Neural Networks.

An overview of all implemented and many planned features can be found in the following document:
[feature overview](https://docs.google.com/spreadsheets/d/1wllITKTaytmOBHMQu9dV0tIj7YtT3UqvB0RRak2qMqk/edit?usp=sharing)

An overview of known issues, planned features and what's currently being worked on can be found on meistertask: [meistertask-twisty-puzzle-analysis](https://www.meistertask.com/app/project/yy5iFYIE/twisty-puzzle-analysis)

# Requirements
The program requires `python 3.x`. It is written and tested in python version `3.8.5`. Backwards compatibility is not guarantied.

Additionally some libraries are required. Those are:
- `vpython` - for 3D visualisation
  - requires older version of `txaio` and `autobahn`. Some working versions are:
    - autobahn v. 20.7.1
    - txaio v. 20.4.1
    latest working versions:
    - autobahn 22.3.2
    - txaio 22.2.1
- `colored` - for colored console output
- `lxml` - for saving and loading the puzzles
- `sympy` - for some automatic analysis of puzzles
- `scipy` - for calculating the 3d puzzle pieces
- `keras` - for training and using neural networks
- `tensorflow` - for training and using neural networks
- `matplotlib` - for visualizing training process of the AI

All of them can be easily installed with `pip install ... `.

# Documentation
The repository has a folder `Documentation` which should include links to markdown files with explanation of the implementation of many features. There is no user manual yet.

Currently the program is supposed to be used via a command-line interface. A proper user interface soon is planned but can still take a long time as I still need to find a better way to implement that.