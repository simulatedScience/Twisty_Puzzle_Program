# Validation of puzzle states

Every non-bandaging twisty puzzle can be mathematically represented as a permutation group.

By determining the permutation that leads from the solved state to the current state of the puzzle, we can check whether or not this permutation is part of the group specific for the puzzle. If that is the case, we know that the state of the puzzle is valid and therefor solvable.

-----

## Generating the permutation group

We already define all moves as permutations. By using the moves as generators, we can very easily generate the group using `sympy`.

More specifically we can convert the moves into permutations using `sympy.combinatorics.Permutation()` and then generate the group with `sympy.combinatorics.perm_groups.PermutationGroup()`.

-----

## Determining the current permutation

To check whether or not the current state of the puzzle is valid and therefor solveable, we need to convert the state into the permutation that would lead from the solved state to the current one.

### **Describing the problem**
The current state as well as the solved state are only given as a list of colors where it usually happens that the same color appears more than once in that list.

This means that we loose information about the puzzle state because, without additional information, there is no way to distinguish points with the same color.

To get this additional information we mimic how our brain does the same for real puzzles: we reconstruct the pieces of the puzzle. These pieces are (frozen) sets of point indices that never move relative to each other.

We can distinguish pieces with a few criteria:
1. number of points in the piece
2. number of different colors on each piece
3. the exact number how often each color appears on a piece
4. the arrangement of the colors (i.e. "abab" or "aabb")

However the fourth criterium only works if we know that the points on similar pieces are always in the same order.

### **Possible solutions**

How to calculate the pieces is described in `automatic piece detection.md` and implemented in `piece_detection.py` (or the respective second versions `_v2`).

Now we need to implement the rules above to determine the exact permutation. That means for every piece in the solved state we need to find the same piece in the current state.

We want to save a list of all correct puzzle pieces with their colors. However pieces can be rotated, which adds some computation time when trying to identify a piece. A rotation of one piece is equivalent to a cyclic permutation of the piece points.

We need this list to determine the permutation of the pieces, which is a crucial step in finding the point permutation, since it reduces the number of options drastically.

#### **Distinguishing pieces**

An alternative approach would be to just store how often each color appears in each piece. This is faster but can loose some information.

Consider the following example piece color layouts: $\left( \begin{array}{cc} 1&0\\ 1&0\end{array} \right) =$ `[1,0,1,0]` and $\left( \begin{array}{cc} 1&1\\ 0&0\end{array} \right) =$ `[1,1,0,0]`.

If we just save the number, how often each color appears, these pieces would be considered equal, even though they are not. Ideally we would automatically detect whether or not this could lead to information loss on a given puzzle and then use the appropriate algorithm to determine the correct permutation, because checking whether or not the dictionaries are the same is more efficient than comparing ordered piece lists

#### **Dealing with duplicate pieces**

Even if the pieces and points are sorted, it is still possible that two pieces are indistinguishable (i.e. two edges of the same colors on a 4x4x4 rubiks cube). In that case we would ideally consider all possible permutations and use them to calculate a probability that the state is valid. But since the number of possible permutations can be extremely large, we have to take shortcuts and risk not finding a valid permutation.

### **Actual implementation**
#### **Preparations/ one-time computations**
1. Calculate the pieces that make up the puzzle.</br>
   **Requirements:**
      - moves
2. Sort these pieces and the points within the pieces.</br>
   **Requirements:**
      - point positions
3. Determine, with the following steps, whether or not the order of the colors on a piece matters:</br>
   1. generate dictionaries for every piece in the solved state to count how often each color appears per piece. (`self.solved_piece_dicts`)
   2. generate the ordered color lists for each piece
   3. compare these dictionaries. If two dictionaries are the same, check whether or not the sets of all cyclic permutations of both pieces are equal. If so, order matters, otherwise we can keep the dictionaries.

   **Requirements:**
      - pieces
      - solved state

#### **Explanation for preparations**

1. As described before the state itself doesn't provide enough information to reconstruct the exact permutation as it is just a list of colors. The pieces carry information about the structure of that list that is given by the moves.

2. in order to calculate the permutation within one piece quicker, it is useful to know the exact order the colors have to be in.
   Consider a piece: $\left( \begin{array}{cc} a&b\\ b&b\end{array} \right)$. If we don't have any information except that these colors appear, we would only know the position of $a$ exactly, while the $b$'s could be in any of the $3! = 6$ permutations.
   If we know the order of the points, i.e. $abbb$, there are only the $4$ cyclic permutations of $abbb$ left. And knowledge about the position of $a$ immidiately determines the exact permutation.

   This is a huge advantage as usually there are many pieces like this. Therefor for each piece of this kind, the number of possible permutations gets multiplied by a factor of $6$, or even more for more identical stickers within a piece.

   Comparing the lists is always more efficient to find out the point permutation, as there are at most `len(piece)` possible options. Without sorting the pieces, there would be `factorial(len(piece))` options. And factorials are always bad for efficiency.

3. We need to check that every piece in the solved state still exists in the current state. However since at least some of the pieces have moved, we only get the pieces as a small list of colors. So we need to check if the list of pieces in the current state matches the list of pieces in the solved state. But since pieces can be rotated, the color lists of two identical pieces may not be equal.</br>
   $\left( \begin{array}{cc} 1&0\\ 1&0\end{array} \right) =$ `[1,0,1,0]` and $\left( \begin{array}{cc} 1&1\\ 0&0\end{array} \right) =$ `[1,1,0,0]`

   If there are no pieces with the same color dictionary, we can efficiently find the piece permutations by comparing the dictionaries. If the color lists provide additional information, we always want to use them to clear up any uncertainty in the case of equal color dicts.


#### **State validation**
1. count how often each color appears. </br>
   If that's different from the solved state, it can't be a valid state.

2. generate dictionaries for every piece in the current state to count how often each color appears per piece.</br>
   Looping over this list of dictionaries and the one generated for the solved state, we delete every pair of matching dicts. If a dictionary from the current state remains unpaired or one from the solved state is not found in the current state, the state is invalid.

   if a dictionary appears more than once, and the color lists provide additional information, 

3. If every piece is found, we need to calculate the permutation that transforms the solved state into the current one. To do that we first determine the permutation of the pieces and then determine the point permutations within those pieces. Together we should get the correct permutation except for cases with two identical pieces.

-----

## Validating a state

Once we have generated the group (`perm_group`) for the puzzle and determined the permutation leading to the current state (`current_perm`) we can simply use `sympy` to check `current_perm in perm_group`.

When defining all permutations, it is essential that we specify the size correct size of the permutation group. Otherwise we get wrong results. To make this clear, look at the following example:

```python
# define the permutation group S5
>>> P1 = Permutation(0,1,2,3,4)
>>> P2 = Permutation(0,1)
>>> S = PermutationGroup(P1, P2)

>>> Permutation(0,1) in S
False
>>> Permutation(0,1, size=5) in S
True
```