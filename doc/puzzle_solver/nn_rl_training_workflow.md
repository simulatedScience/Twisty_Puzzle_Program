1. create puzzle  
    option 1: Use existing puzzle  
    option 2: Create new puzzle from Geogebra file and existing UI for adding moves  
    option 3: Use `src/puzzles/cuboid_generator.py` to generate any non-shapeshifting cuboid puzzle with its moves
2. generate and save algorithms using `tests/algorithm_generator.py`  
   1. *run `algorithm_generator.py`* the CLI will prompt for the puzzle name
   2. *generate algorithms using the CLI of the program*  
   3. *export generated algorithms to a new version of the puzzle using the CLI of the program*
3. calculate symmetries using `tests/symmertry_detection/rotations_to_permutations.py`  
   1. *set puzzle to calculate symmetries for within main-guard of `rotations_to_permutations.py`*
   2. *run `rotations_to_permutations.py`, making sure to save the output*
4. add symmetries to the puzzle using `tests/symmetry_detection/permutations_to_cycles.py`  
   1. *define new method with symmetry permutations from text output of `tests/symmertry_detection/rotations_to_permutations.py`*
   2. *set puzzle to add moves to and new puzzle name within main-guard of `permutations_to_cycles.py`*
   3. *run `permutations_to_cycles.py`*
