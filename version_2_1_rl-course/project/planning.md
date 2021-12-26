# Goal
We want to create an AI, using deep Q-Networks, that is able to solve twisty puzzles.

Ideally this AI can be trained for quite general twisty puzzles without additional effort.


# Digital representation of twisty puzzles
## Restrictions
We are only considering non-bandaging puzzles for now. That means that at each possible state, the same moves are availiable.

Additionally puzzles like the _Brain String_ cannot be represented with the following system as this is a puzzle bandaged by the maximum tension on a rubber band. In addition the knots it forms as part of the puzzle cannot be represented here.

## Data representation
### For visualisation
We recreate twisty puzzles as a set of points in $\mathbb{R}^3$ which are saved in an array.

Each point is assigned a color and there is a specific arrangement of the colors in the array that counts as solved.

Moves can be represented as permutations acting on this array. Any move can consist of several disjoint cycles.

In practice one may think of each point as representing one color sticker on a real twisty puzzle. Although some puzzles require several points per sticker to fully describe their movement (i.e. the (geared) mixup cube).

### For the AI
The AI does not need to know where a point is in 3d space. Every possible state is uniquely defined by a list of colors which can be easily represented using integers.

Performing moves (permutations) on this array of color-integers yields all the information necessary for the AI.

To animate the solving process of the AI it is easiest to just save the moves performed and execute them in order. Alternatively we could map each array index to one of the points in 3d space and assign that point the color encoded by the integer.

The integers in the array can be easily obtained by counting the number of colors in the given puzzle and enumerating them. It's best to save this mapping somewhere.
One could also just interpret the hex-color code as a base 10 integer to get the color but that would result in unnecessarily large numbers.

It should not be necessary to vary between different difficulty levels explicitly as a harder scamble also requires to solve easier ones.
However this does depend on the state space. If there are too many possible moves in any given state, this may not be sufficient and harder scrambles may have to be alternated with easier scrambles.

# AI implementation

## Choice of algorithms
The state space of twisty puzzles can get very large even for quite simple puzzles (3x3x3 rubik's cube has $4.6\cdot 10^{19}$ states, a 2x2x2 rubik's cube still has around $8.8 \cdot 10^7$).

Therefor a simple Q-learning algorithm won't be able to solve any reasonably complex puzzles efficiently.

Twisty puzzles are completely deterministic with no random element in the solving process.

## Learning techniques
When solving a twisty puzzle there is neither an opposing player nor a clearly defined starting state.

Therefor any training example must be a randomly scrambled state.

Since most state spaces of twisty puzzles are so large, it would be impossible to train the AI on fully scrambled puzzles from the beginning.

To overcome this issue, we scramble the puzzles progressively more as the AI learns. Starting at a solved state we add more moves to the scrambling process, therefor making it harder to solve.

Since it is difficult to predict the learning rate and match the difficulty increase appropriately, this will be done via some evaluation function that makes the scrambled state harder every time the AI reaches a given threshhold of solving efficiency.

# Interesting side projects
The Skewb has just over 4000 possible states. Therefor it could be interesting to see how well a pure Q-learning algorithm could solve that.