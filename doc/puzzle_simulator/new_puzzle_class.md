
For each puzzle, we want to store the following information:
- `str` puzzle name
- `list[vec3]` color list
- colored 3D points
  - `vec3` coordinates
  - `int` color
- state space size (upper bound & lower bound)
  - `bool` tag whether this was set manually or automatically computed
- moves:
  - base moves
    - `str` name
    - `list[list[int]]` permutation
    - (`vec3` rotation axis)?
  - spatial rotations
    - `str` name
    - `list[list[int]]` permutation
    - `vec3` rotation axis
  - algorithms
    - `str` name
    - `list[list[int]]` permutation
    - `list[str]` base move sequence
    - `str` text description
- `str` solution text instructions

- `dict[str, float]` default scale for different shapes?

dtypes: `str`, `vec3`, `list[list[int]]`, `list[str]`, `bool`, `int`

use `json` instead of `xml`?
