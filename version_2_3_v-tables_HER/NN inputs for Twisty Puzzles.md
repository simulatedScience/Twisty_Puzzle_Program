# NN inputs for Twisty Puzzles

## 1. one neuron colored per sticker
**Idea:** $n$ neurons for $n$ colored stickers on the puzzle.

e.g. a Rubiks 3x3 has 54 stickers (9 stickers/face * 6 faces), so 54 neurons getting discrete values for each color.

## 1.1. one-hot encoded stickers
**Idea:** $n \times k$ neurons for $n$ stickers and $k$ colors.

Each sticker's color is one-hot encoded.

e.g. a Rubiks 3x3 has 54 stickers (9 stickers/face * 6 faces), so 54*6 = 324 neurons getting 0-1 values for each color.

## 2. piece information
**Idea:** Use permutations of pieces instead of permutations of stickers:

Puzzles can be split into pieces by detecting groups of stickers (colored points), that are never split up by any move. Any move affecting one of the stickers also affects all other stickers of the same piece (For Details see `automatic piece detection.md`).

To accurately describe a piece's state, we usually need more than it's position. We also need to know it's orientation (e.g. for corner pieces). Usually rotation around one axis is enough to describe a piece's orientation.

## 3. visual input
**Idea:** use images as inputs that show the entire puzzle.

_Assuming convex puzzle shapes_, a few images obtained through different projections should be enough to describe the entire puzzle.

# Additional ideas

## A. Add masks to the input
**Idea:** Add masks to the input to highlight specific features

Masks can be stacked along the same dimension as one-hot encoded info or color channels.

Possible masks:
- Boolean arrays showing what inputs have changed because of the last action.  
  This should be combined with options B and/or C.
- Boolean array showing which pieces/ stickers are in the correct position and/or orientation.


## B. Add a secondary input(s) for the last action(s)
**Idea:** Add a secondary input(s) for the last action(s)

This could improve the AI's ability to learn algorithms.

## C. Use Architecture with memory
**Idea:** Use NN Architecture with memory like LSTMs

This could improve the AI's ability to learn algorithms further than option B or could be used in combination with option B.
