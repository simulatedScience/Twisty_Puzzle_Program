# Digitalizing Twisty Puzzles

## Information to save for each puzzle

- puzzle definition:
  - `str` puzzle name
  - `list[vec3]` 3D points of the puzzle
  - `list[int]` colors of 3D points as indices of a color palette
  - `list[vec3]` color palette for puzzle (define defaults for 4, 6, 8, 12 sides)
  - `int` number of points
  - `int` number of pieces
  - `?` solved state

- puzzle pieces (for visualization, calculated during runtime, optionally saved to files):
  - `set[int]` set of points (as indices of 3D points)
  - `Polyhedron` 3D object per piece
  - `int` number of points in piece
  - `vec3` current piece COM
  - `vec3` current piece orientation
  - `vec3` solved state COM
  - `vec3` solved state orientation

- moves:
  - `list[tuple[int]]` move cycles (permutation on indices of 3D points)
  - `vec3` move rotation axis
  - `vec3` move COM
  - `int` order of move
  - `int` number of pieces affected by move

- algorithms:
  - `str` algorithm name
  - `str` algorithm description
  - `str` or `list[str]` algorithm move sequence
  - `list[tuple[int]]` algorithm cycles (permutation on indices of 3D points)
  - `int` order of algorithm
  - `int` number of pieces affected by algorithm

- puzzle state:
  - `list[int]` current permutation of 3D points
  - `list[str]` list of moves made so far
  - 

