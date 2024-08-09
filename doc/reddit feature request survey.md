Posted on r/twistypuzzles:  
https://www.reddit.com/r/twistypuzzles/comments/1en6v28/would_you_be_interested_in_a_general_puzzle/

## Would you be interested in a General Puzzle Solver Program?


I have been working on a program using Machine Learning to solve various twisty puzzles without having to input human-made algorithms and solutions.

So you would input a puzzle with its basic moves, then the program automatically creates algorithms that could be useful (e.g. cycle three corners) and then trains an AI to use these algorithms along with the base moves to solve the puzzle.

**What features would you like in such a program? Are you interested at all?**

My program cannot solve bandaged puzzles and most likely will never work on jumbling puzzles due to the way I wrote my simulator and some mathematics that work differently on these puzzles (they aren't permutation groups).

### Context:
**Existing Simulators:**  
There are several existing puzzle simulators out there with vast digital puzzle libraries (pCubes, Ruwix, Permuzzle). However, I don't know any simulator that includes a general solver as well.

**Exisiting Solvers:**  
Existing solvers I know only work for a very small set of puzzles. As far as I know, these use either brute force methods to find solutions or rely on handcrafted algorithms, specifically coded for each puzzle. (ksolve+, cube explorer, Trangium Batch Solver, nissy)

**Existing ML solvers:**  
Puzzles like the 3x3 Rubiks Cube have been solved with machine learning before. At least in:
- 2019 DeepCubeA (https://doi.org/10.1038/s42256-019-0070-z)
- 2023 EfficientCube (https://openreview.net/pdf?id=bnBeNFB27b)

These try to find shortest solutions (fewest number of moves) to solve a puzzle. They also tend to need a lot of compute power and I don't expect them to scale well for larger puzzles.

### My Motivation:
When I get new puzzles, figuring out how to solve them is tricky and I don't like looking up existing solutions (if any exist). Having a program that works for many different puzzles and could provide a "reset to solved" option for my physical puzzles as well as less punishing experimentation on digital puzzles can be handy.

This program could also help find solutions for new puzzles.

I already veryfied that my goals are pretty realistic. My program can solve several small puzzles with Reinforcement learning and has helped me find algorithms with which I was able to solve the geared mixup cube. I am working on combining these parts.