
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
    - (`vec3` rotation axis)? -> no, improve automatic rotation detection instead
  - spatial rotations
    - `str` name
    - `list[list[int]]` permutation
    - (`vec3` rotation axis)? -> no, improve automatic rotation detection instead
  - algorithms
    - `str` name
    - `list[list[int]]` permutation
    - `list[str]` base move sequence
    - `str` text description
- `str` solution text instructions

- `dict[str, float]` default scale for different shapes?

dtypes: `str`, `vec3`, `list[list[int]]`, `list[str]`, `bool`, `int`

use `json` instead of `xml`.

Save base moves, rotations and algorithms in a shared format. Additionally, store lists `base_move_names`, `rotation_names`, `algorithm_names` to keep track of the order of the moves.

To store additional algorithm information, save algorithm objects in a separate `dict[str, Twisty_Puzzle_Algorithm]`. These objects should be able to save text descriptions and provide `to_dict` methods for saving to json.  
The UI can then implement methods to update the algorithm text or display the algorithm either as base moves or as single permutation.