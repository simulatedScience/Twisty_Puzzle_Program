# NN inputs for Twisty Puzzles

We plan to implement a two-step approach for solving twisty puzzles:
1. Generate algorithms (move sequences) that only change a few pieces at a time. (algorithm generator)
2. Learn to use these algorithms to solve the puzzle. (actor)

A motivation for these steps can be found in `doc/smarter_ai.md`.

With these steps we have two fundamental options:
1. First generate all algorithms we need, then learn solving the puzzle with a static action set.  
   Here, the main difficulty lies in determining, when we have reached a sufficient set of good algorithms, which could take a long time.
2. Generate algorithms while learning to solve the puzzle.  
   Here, the main difficulty lies within the action space changing over time as new algorithms are found.

In both cases we also face the difficult decision when to discard previously found algorithms to replace them fore new, more useful/ efficient ones.  
Both cases also require the puzzle state as an input to the NN. [Below](#puzzle-state-encodings), we describe different options to encode the puzzle state for that.

With a changing action space in option 2, we expect it to be beneficial to pass information about the available actions to the NN. [For this](#puzzle-action-encodings) we also describe different options to encode available actions (moves and algorithms).

## Puzzle state encodings

Here, we describe different options to encode the current state of a puzzle as input for a neural network (NN).

### 1. one neuron per colored sticker
**Idea:** One neuron per sticker, getting discrete values for each color.

**Input shape:** $n_s$ neurons with values $x_i \in [0, 1]$ for $n_s$ colored stickers on the puzzle.

Each sticker is represented by a single neuron. The neuron's value is the color of the sticker encoded as an integer in $[0, k] \cap \mathbb{N}$ or float in range $[0, 1]$.

**Example:** a Rubiks 3x3 has 54 stickers (9 stickers/face * 6 faces), so 54 neurons getting discrete values for each color.

### 1.1. one-hot encoded stickers
**Idea:** $k$ neurons per sticker one-hot encoding its color.

**Input shape:** $n_s \times k$ neurons with values $x_i \in \{0, 1\}$ for $n_s$ stickers and $k$ colors.

Each sticker's color is one-hot encoded. There is no 3D information about the puzzle's structure.

**Example:** a Rubiks 3x3 has 54 stickers (9 stickers/face * 6 faces), so 54*6 = 324 neurons getting 0-1 values for each color.

**Advantages:**
- very discrete input, easy to learn for NNs
- easy to implement & understand

**Disadvantages:**
- very large input size
- no information about the puzzle's structure

### 2. Piece permutations
**Idea:** Use permutations of pieces instead of permutations of stickers.

**Input shape:** $n_p \times (n_p+1)$ with discrete values $x_i \in [0, n_p]$ for $n_p$ pieces on the puzzle. The last column/ row may have continous values representing rotation angles.

Puzzles can be split into pieces by detecting groups of stickers (colored points), that are never split up by any move. Any move affecting one of the stickers also affects all other stickers of the same piece (For Details see `automatic piece detection.md`).

To encode the permutation of the pieces, we could use a row/column-wise one-hot matrix, where each row/column represents one piece. The matrix would have $n_p$ rows and columns, where $n_p$ is the number of pieces. The matrix would have $n_p^2$ neurons, but only $n_p$ of them would be active at any time. For efficient processing, a 1D convolutional layer could be used to reduce the number of weights in the NN.

To accurately describe a piece's state, we usually need more than it's position though. We also need to know it's orientation (e.g. rotation of corner pieces). Usually rotation around one axis pointed roughly at the COM of the puzzle is enough to describe a piece's orientation. These rotations also often have only very few discrete possible values (e.g. 3 possible orientations for a corner piece of a 3x3 Rubiks cube). So we could add one neuron per piece to encode the piece's orientation.

Only few puzzles like the planets puzzles by Oskar van Deventer have pieces that can be rotated around multiple axes.

**Example:** a Rubiks 3x3 has 26 pieces (8 corner pieces, 12 edge pieces, 6 center pieces), so 26*26 = 676 neurons getting 0-1 values for each piece. Adding one neuron per piece to encode the piece's orientation, we get 702 neurons.

**Advantages:**
- there are fewer pieces than stickers, so the relevant input size is smaller than option 1
- pieces are closer to the actual structure of the puzzle than stickers, possibly helping the NN to learn faster (better data quality)

**Disadvantages:**
- Clear one-hot encoding costs a lot of input neurons, forcing a larger (possibly slower) NN.
- Orientation of some pieces may not be relevant -> unnecessary input neurons

### 3. Visual input
**Idea:** use images as inputs that show the entire rendered puzzle
**Input shape:** $n_x \times n_y \times n_c$ image with $n_x \times n_y$ pixels and $n_c$ color channels, continous values $x_i \in [0, 1]$.

_Assuming convex puzzle shapes_, 2-4 images obtained through different projections should always be enough to see the entire puzzle state. (4 cameras can guarantee seeing every face of a convex puzzle with fixed positions, with 2 and 3 cameras we need to move the cameras to see every face to prevent faces being perfectly parallel to the camera's view direction)

**Advantages:**
- very general input, transferable to many different puzzles or completely different problems
- could benefit from pretrained vision models to quickly get a good latent space representation of the puzzle state

**Disadvantages:**
- very large input size
- extremely slow input generation since rendering is very slow compared to the other presented methods.

## Puzzle action encodings
Actions for the actor (step 2 of the solver) are moves and algorithms (move sequences). These can be understood as a permutation of the puzzle's stickers or pieces. Here, we describe different options to encode these permutations as input for a neural network (NN).

Importantly, we want to convey information about what each action does to the puzzle. Otherwise, the NN would have no information about what a new action does and would have to learn this from scratch through exploration.

### 1. One-hot permutation matrix per move
**Idea:** Use one-hot permutation matrices to encode moves. Similar to how piece permutations are encoded in option 2 of [puzzle state encodings](#2-piece-permutations).

**Output shape:** $n_p \times (n_p+1) \times n_a$ with discrete values $x_i \in \{0, 1\}$ for $n_p$ pieces on the puzzle and $n_a$ actions. The last column/ row may have continous values representing rotation angles of the pieces.

**Advantages:**
- very discrete input, tends to be easy to learn for NNs

**Disadvantages:**
- very large input size, especially for puzzles with many pieces/ stickers
- adding actions would require adding more input neurons


### 2.* text output for move/ algorithm names
**Idea:** Use text output for move/ algorithm names. This turns the actions space into a set of strings made up of characters from a given alphabet (a.g. `a-z`, `-`, `_` and `'` for inverse moves)

**Output shape:** output sequence: $n_{alph}$ neurons representing each character of the alphabet, including an `end` token. The output is a sequence of characters.

**Advantages:**
- very versatile output space can easily adapt to new available actions
- good reason to learn about transformers/ Mamba or similar NN architectures

**Disadvantages:**
- relatively huge output space with only a tiny portion of valid actions. What are valid actions depends on currently available moves and algorithms, which can change over time.
- Output _sequence_ for multi-character names requires some memory and is more difficult to learn for NNs than single-character output and expensive to generate.
- Likely requires valid action names to be given as input, increasing computation cost and complexity further.  
  Variable length action names as input also require input sequences.



## Variable actor outputs

Option 2 described [above](#nn-inputs-for-twisty-puzzles) generates algorithms while learning to solve the puzzle. This means that the action space changes over time as new algorithms are found. This is a problem for the actor, as it needs to be able to handle a changing action space. Here, we describe different options to handle this.

### 1. Adding actions through a second NN imitating the previous one
When an action is added, initialize a new NN with the modifcations to accommodate the new action. Then train the new NN to imitate the previous one through imitation learning. This should be much faster than training the new NN from scratch.

### 2. Adding actions by adding neurons with random/ 0-weight initializations
When an action is added, add new neurons to the network. Here, the key is to choose good initializations for the new neurons.  
- 0-initialization wouldn't affect the previous capabilities of the NN, but would likely lead to slow learning of the new action.  
- Random initialization would likely lead to faster learning of the new action, but could significantly addect the previous capabilities of the NN, leading to catastrophic decline in performance.

### 3.* general action space to accommodate all possible actions
Choose an action space that can accommodate all possible actions. For example, this could be a permutation of all pieces/ stickers or a move name.  
This needs to be combined with some form of masking to only allow valid actions for the current puzzle state and available actions.


## Additional ideas

### A. Add masks to the input(s)
**Idea:** Add masks to the input to highlight specific features

Add additional input neurons to highlight specific features of the puzzle state.
Masks can be stacked along the same dimension as one-hot encoded info or color channels.

Possible masks:
- Boolean arrays showing what inputs have changed because of the last action.  
  This should be combined with options B and/or C.
- Boolean array showing which pieces/ stickers are in the correct position and/or orientation.


### B. Add input(s) for the last action(s)
**Idea:** Add secondary input(s) for the last action(s)

This could improve actor's ability to learn algorithms itself as it would have information about the last action(s) and could learn to combine them.

Given the nature of most twisty puzzles, the last action is usually irrelevant for the next action. So this input is unlikely to be useful for the actor.

### C. Use Architecture with memory
**Idea:** Use NN Architecture with memory like LSTMs

This could improve the AI's ability to learn algorithms further than option B or could be used in combination with option B.

Given the nature of most twisty puzzles, the last actions are usually irrelevant for the next action. So this change is unlikely to be useful for the actor with most encodings of the puzzle.


### D. Supervised pretraining from reverse scrambles
**Idea:** Pretrain the NN with supervised learning on (shortened) reverse scrambles

This could massively speed up learning initially, as supervised learning has much denser and higher quality reward signals than reinforcement learning. However, reversed random scrambles won't always represent the best solution to a given state.  
Using RL for fine-tuning after some supervised training could still improve performance.

**Advantages:**
- Learning from reverse scrambles has been shown to be much faster than RL for twisty puzzles. [see here](https://arxiv.org/pdf/1805.07470.pdf)


### E. Instead of training a NN from scratch, use a pretrained Transformer
**Idea:** Fine tune a pretrained language model (Transformer) to solve twisty puzzles. We can cut down the action space of the language model to only include valid characters for twisty puzzle moves to reduce the size.

**Advantages:**
- pretrained transformers are very powerful and can be fine-tuned to solve many different problems, possible including twisty puzzles
- learning about fine-tuning transformers could be an immensely useful skill in the near future

**Disadvantages:**
- language models are very large and trained on text that is very different from the group notation we would use here. This could make it difficult to fine-tune the model to solve twisty puzzles.
- Models may have learnt internall state representations that are not useful for twisty puzzles, making it difficult to fine-tune the model to solve twisty puzzles.
- Models may have learnt a ton of information that is completely useless for twisty puzzles, increasing the size of the model a lot with no benefit for twisty puzzles.

### F. Use search to enhance success rate during training
**Idea:** Just like MCTS was used during training of AlphaZero, we can use NN-guided search to enhance the twisty puzzle solver during training, leading to stronger reward signals and faster learning.

**Advantages:**
- Using search enhances data quality for the agent, getting more rewards, leading to faster learning.

**Disadvantages:**
- Search is computationally expensive, so it would slow down training a lot. Considerations: Quality of episodes vs. number of episodes.