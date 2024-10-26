# Automatically name rotations

To improve interpretability of AI solves and ease of use of the simulator, named rotations are better than numbered rotations.

Many puzzles, especially official WCA (World Cubing Association) puzzles, have a standard color scheme. Regulations often state the default orientation as white face on top, green in the front.
We use this standard to name rotations. Locating two faces is sufficient to uniquely determine the orientation of the puzzle (unless it has multiple faces of the same color).
Therefore a rotation can be described by the two colors of faces that are moved to the top and front faces respectively.
By assuming a default orientation (white top, green front) and carefully choosing color names, we can shorten the rotation names to two letters, each describing one color.

We use face-color based naming instead of move-based naming because, deviating from WCA conventions, for many edge- or corner turning puzzles we use move names with more than one letter. Especially for non-WCA puzzles, move names are often not standardized and can be more ambiguous than color names.

## Examples:
### Rubik's Cube (3x3x3)
- Rotating 90° clockwise (same as U move) around the top face, moves the red face to where the green face was while keeping the white face in place. This rotation is named `rot_wr`, because after applying it to the default orientation, the white face is on top and the red face is in front.

- Rotating 180° clockwise around the red face (same as R2 move) moves the yellow face to where the white face was and the blue face to where the green face was. This rotation is named `rot_yb`, because after applying it to the default orientation, the yellow face is on top and the blue face is in front.

## Automatic rotation naming
The simulator only knows the moves as named permutations acting on the set of colored 3D points. The colors are given as RGB tuples.

So to name a rotation, we need to:
1. Find which points are white and green.
2. Find the colors of the points that are moved to the white and green points' positions when the rotation is applied.
3. Convert RGB color tuples to color names with unique starting letters.

To support legacy puzzles with different color choices (different shades of the standard colors), we need to find the closest matching color from a list of default colors and cannot simply find exact matches.

### Implementation
1. Define lists of default colors (name + rgb value) for puzzles with 4, 6, 8, 12 faces. `dict[str, Tuple[float, float, float]]`
2. Define function that, given a color as rgb tuple, finds the closest matching color from the list of default colors. `def find_closest_color(color: Tuple[float, float, float]) -> str`  
   Use maximum norm for distance? Try different norms.
