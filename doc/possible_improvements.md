# Possible Improvements
This is an incomplete list of the potential improvements to the program that I am aware of. It is not sorted by priority or feasibility. Almost every major aspect of this project can be improved in some way, but I need to prioritize which features to implement and which ones to leave out or postpone.

## Puzzle Simulator
### Puzzle Definition
- Enable user to define algorithms by entering a move sequence
- Support move definition process using geometry-based symmetry detection.  
  User can input a subset of moves and automatically generate the rest of the moves based on the rotational symmetries of the points. Symmetry detection is implemented. Adding this feature would mostly require concatenating the existing moves with rotations and filtering out duplicates.
- Define moves using cutting planes/ general surfaces and angle detection. All points beyond a user defined surfaces are moved. Valid angles are automatically detected and presented as choices to the user.  
  Very similar code is already used for the cuboid and megaminx puzzle generation. The main difficulty is a UI to define the cutting planes/ surfaces.  
  To enbale cutting planes where the normal isn't the move's rotation axis or enable general cutting surfaces, use geometry based symmetry detection to suggest rotation angles.
- Remove reliance on Geogebra and add tools directly to the viewport and CLI:
  - allow defining new and editing existing points
  - add mirroring options: let user define mirror planes or choose from list of symmetries/ toggle predefined mirror planes for cubic, octahedral, dodecahedral and icosahedral symmetry.
  - easy-coloring of points:
    1. select color, then click on points to color them or
    2. select points with mouse drawing a rectangle to select all points in the rectangle and color them.
    3. select points using cutting planes and color them all at once.
- add quick option to make all pieces directional.  
  Replace single points with ~4 points, possibly colored to reflect neighbouring faces

### Modelling
- Allow modelling of Bandaged Puzzles: Click two points to bandage them together. If any move would move some but not all bandaged points, the move is not allowed. If before and after a potential move, two bandaged points have different distances, the move is not allowed.
- Moves could be named automatically by predominant face color using the rotation-naming code.  
  Edge or corner turning moves in current puzzles are named using the first letter of the colors they affect. E.g. "wb" turns the white-blue edge 180°, "wgr" the white-green-red corner 120°, turning white towards green. This naming could be automated.
- Add support for invisible points to enable more shapeshifting puzzles.  
  E.g. shapeshifting cuboids where 90° turns are possible on non-square faces.
- Implement lower bound for state space size (computed from upper bound, partially done)
- Try to find a faster way to calculate state space size.

### Visuals
- Add more clip shapes to draw 3D pieces:  
  platonic solids, archimedean solids, custom imported shapes, etc.
- Enable custom rotation and translation of clipshapes before calculating 3D piece shapes.
- Option to customize colorscheme of a puzzle: change shades of the colors.
- Implement a standardized (customizable) color scheme for puzzles and option to convert a puzzle to this scheme.
- Toggleable option for algorithm visualization: short form (current, only show algorithm permutation directly) or long form (show each move of the algorithm).  
  This requires saving the algorithm moves in the puzzle file. Currently they are saved separately.
- Improve Rotation animation for algorithms.
- Properly animate geared puzzles.  
  May be able to detect them automatically if points of a cycle are not on one plane. Then find a main and secondary axis of rotation.
- Add preview option for moves and especially algorithms.  
  In GUI with buttons, a single press/ hover shows preview, double press executes the move/ algorithm.

### User Interface
- The CLI is not great for usability. A GUI with buttons and a 3D viewport would be much more intuitive and faster to use.
- Improve UX:
  - when `loadpuzzle` is called while a puzzle is loaded, call `closepuzzle` automatically.
  - Prevent crashes by catching more bugs. Crashes are a common way to lose prgress.
- Simplify workflow of rotation and algorithm generation. Make both accessible from the same file or main CLI.
- Fix `reset` when 3D pieces are displayed.  
  This currently doesn't work because setting the color of the custom defined vpy-Polyhedra doesn't work. Instead, store solved position and orientation of each piece.
- Enable user to record their own solves and save them to a file.  
  This could be used to compare human solves to AI solves or to save a solve for later reference.

### Puzzle Files
- Save algorithm moves in the puzzle file.  
  Currently they are saved separately in an auto-generated `.txt` file in the puzzle folder. Many parts of the program depend on loading puzzle files or expect algorithm and rotation names to start with "alg_" and "rot_" respectively.
- Mark algorithms and rotations without relying on the name.  
  Requires support in various parts of the program. Due to the expected complexity of new files, I decided early on not to do this for now and accepted the name dependency, making the change harder to implement later.  
  Each move could be assigned a unique index, which remains independent of the name and doesn't change when moves are renamed
- Enable renaming algorithms without resetting the state space size of the puzzle.
- Enable storing text notes for algorithm descriptions, solution strategies and more.

## Rotational Symmetry Detection
- Combine move based and (purely) geometry based symmetry detections, implementing the fallback to geometry based detection if move based detection is not possible.

## Algorithm generation
- Improve Reproducability! Save algorithm generation parameters when saving algorithms.
- Add automatic hyperparameter tuning or recommendations/ guidance for parameters.
- Automatic naming of algorithms. Some puzzles already use naming conventions for algorithms:
   | phrase | meaning |
   | --- | --- |
   | swap_2 | swaps two pieces described afterwards |
   | swap_n | (n is even) makes n/2 swaps of pieces |
   | flip | flips a piece in-place |
   | cycle | moves at least 3 pieces cyclicly |
   | cycle_n_k | two separate cycles of lengths n and k |
   | centers | center pieces, usually having exactly 1 color |
   | edges | edge pieces, usually having exactly 2 colors |
   | corners | corner pieces, usually having >2 colors |
- use patterns to find algorithms faster and learn across puzzles.  
  1. Use common patterns like commutators (`A B A' B'`), conjugates (`A B A'`) with `A` and `B` being any move sequences
  2. Detect useful patterns of algorithms and store them across puzzles as algorithm templates. Then, insert moves or move sequences into these templates to generate new algorithms. E.g. in a template `A B A'`, set `A = F U` and `B = R` to get `F U R U' F'` as a new potential algorithm.

## AI Solver
- Integrate NN solver in the A* search. This should only take a few minutes to add as it's already well-prepared.
- make NN architecture flexible. Currently uses the default sb3 policy for PPO (2 dense hidden layers with 64 neurons each).  
  This works well for all tested puzzles so far, but different architectures and parameter counts could reduce training time or improve performance of trained agents.
- experiment with different RL algorithms.  
  Currently, we use PPO with no other options.
- Add automatic hyperparameter tuning.  
  Current parameters seem to work well for most puzzles. I performed some experiments to tune them manually, but those are not well documented.
- make training easier. Suggest hyperparameters automatically based on state space size
- Implement Early Stopping again  
  removed when adding parallelization with `VecEnv` and never reimplemented because continued training showed improvements in average episode length.

## AI Policy visualization
- Simplify comparison of different (AI) agents.
