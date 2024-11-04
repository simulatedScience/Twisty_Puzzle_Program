# Solve comparisons
Here, we collect solves of different agents for some scramblles. These agents include: human solves, DeepcubeA solves and solves by our own, trained AI.

## Scramble 1
**Scramble:**
B D U F F L' F' D R D' L B' D B' D R' D' L R' L' L' D U R' D F' U' R L F'

**Human solve 1 (layer-wise):**
<!-- solve white layer -->
U' U' B' U U' L F U B' D B F D' F' D' D' F' D F D' D' L' D L rot_yg
<!-- solve middle edges -->
L' U L U F U' F' U U F' U F U R U' R' B' U B U L U' L' U B U' B' U' R' U R
<!-- solve yellow edges -->
F R U R' U' R U R' U' F' U F R U R' U' F'
<!-- solve yellow corners -->
R' D' R D R' D' R D R' D' R D R' D' R D U'
R' D' R D R' D' R D U'
R' D' R D R' D' R D R' D' R D R' D' R D U'
R' D' R D R' D' R D U'

Some rotations were omitted and instead converted to the corresponding moves. This is because humans perceive the puzzle differently from AIs and replicating all rotations would be difficult.

**Complete human solve (for copying):**
U' U' B' U U' L F U B' D B F D' F' D' D' F' D F D' D' L' D L rot_12 L' U L U F U' F' U U F' U F U R U' R' B' U B U L U' L' U B U' B' U' R' U R F R U R' U' R U R' U' F' U F R U R' U' F' R' D' R D R' D' R D R' D' R D R' D' R D U' R' D' R D R' D' R D U' R' D' R D R' D' R D R' D' R D R' D' R D U' R' D' R D R' D' R D U'


**DeepCubeA solve:**
U F' U F' B' U' L F' R L' F' U L U R L F' F' L' F' L D' F' L' U L' L' U' L' U L' L' D' L U' L' D L'

## Scramble 2
**Scramble:**
D F L' R F' F' L D' D' L' L' B D U' R' B D' D' B' B' R R D U' F U' B U' F D

**Human solve 1 (layer-wise):**
<!-- layer 1 -->
U' L' R F' D' R R D D L D' L' B D' B' R' D' R D' R D' R' D' D' R' D R U' rot_yg
<!-- layer 2 -->
U L' U L rot_wo U R U' R' rot_wb R U' R' U' rot_wr L' U L R U R' rot_wr U' L' U' L rot_wr U R U' R' U' rot_wr L' U L rot_wr U R U' R' U' rot_wr L' U L
<!-- layer 3 -->
F R U R' U' F' U rot_wo R U R' U R U U R' U rot_wr U' L' U R U' L U R' rot_wo R' D' R D R' D' R D R' D' R D R' D' R D U U R' D' R D R' D' R D U U

**Human solve 2 (corners first):**
<!-- corners -->
U' F F R D' R' D R D' R' D rot_yg R' D' R D R' D' R D U R' D' R D R' D' R D U R' D' R D R' D' R D U
<!-- yellow layer -->
E' E' R E' R' U' D' M D M' U M' D D M U' D' S D D S' D D rot_rg
<!-- layer 2 -->
R R R U R' R' U R R U U R' R' U' U' R R U R' R' U R R U U R' R' U' U' R R R R U R' R' U R R U U R' R' U' U' R R U R' R' U R R U U R' R' U' U' rot_yb R R U R' R' U R R U U R' R' U' U' R R U R' R' U R R U U R' R' U' U' E' L' rot_wr R R U R' R' U R R U U R' R' U' U' R R U R' R' U R R U U R' R' U' U' B E F rot_gy
<!-- layer 3 -->
R R U R' R' U R R U U R' R' U' U' R R U R' R' U R R U U R' R' U' U' rot_wo R R U R' R' U R R U U R' R' U' U' R R U R' R' U R R U U R' R' U' U' rot_gr
<!-- orient edges -->
M' U M' U M' U M' U M U' M U' M U' M U' rot_yb M' U M' U M' U M' U M U' M U' M U' M U' rot_rg R B M' U M' U M' U M' U M U' M U' M U' M U' B' R'

**full solve:**
U' F F R D' R' D R D' R' D rot_yg R' D' R D R' D' R D U R' D' R D R' D' R D U R' D' R D R' D' R D U E' E' R E' R' U' D' M D M' U M' D D M U' D' S D D S' D D rot_rg R R R U R' R' U R R U U R' R' U' U' R R U R' R' U R R U U R' R' U' U' R R R R U R' R' U R R U U R' R' U' U' R R U R' R' U R R U U R' R' U' U' rot_yb R R U R' R' U R R U U R' R' U' U' R R U R' R' U R R U U R' R' U' U' E' L' rot_wr R R U R' R' U R R U U R' R' U' U' R R U R' R' U R R U U R' R' U' U' B E F rot_gy R R U R' R' U R R U U R' R' U' U' R R U R' R' U R R U U R' R' U' U' rot_wo R R U R' R' U R R U U R' R' U' U' R R U R' R' U R R U U R' R' U' U' rot_gr M' U M' U M' U M' U M U' M U' M U' M U' rot_yb M' U M' U M' U M' U M U' M U' M U' M U' rot_rg R B M' U M' U M' U M' U M U' M U' M U' M U' B' R'

**full solve algs:**
U' F F R D' R' D R D' R' D rot_yg R' D' R D R' D' R D U R' D' R D R' D' R D U R' D' R D R' D' R D U E' E' R E' R' U' D' M D M' U M' D D M U' D' S D D S' D D rot_rg R alg_cycle_3_edges R R alg_cycle_3_edges rot_yb alg_cycle_3_edges E' L' rot_wr alg_cycle_3_edges B E F rot_gy alg_cycle_3_edges rot_wo alg_cycle_3_edges rot_gr alg_flip_2_edges rot_yb alg_flip_2_edges rot_rg R B alg_flip_2_edges B' R'


**DeepCubeA solve:**
D R' U L D F' L F' R' F' U F D B D' B' R' F' U L D' F D L' U' F L' R'

## Scramble 3
**Scramble:**
F' U' U' B' R' F D L R' D F B U' R' F' U D U D B' L U' B' U L B U B U D'

**Human solve 1 (layer-wise):**
<!-- layer 1 -->
R U R' B B D D F F L R' D R D D L' D B D' B' D' R D' R' D F' D F rot_yg
<!-- layer 2 -->
rot_wb U U R U' R' U' rot_wr L' U L rot_wo U L' U L rot_wo U R U' R'
<!-- layer 3 -->
rot_wo F R U R' U' R U R' U' F' U' U' L' U R U' L U R' rot_yb R U R' U' R U R' U' D R U R' U' R U R' U' D R U R' U' R U R' U' D D

**DeepCubeA solve:**
F' L B' D F D' B' R U' R' L' D' U L F U L' F' U' F R U R' L D F' U' F D' F' U L' F' L'

## Scramble 4
**Scramble:**
F F B' L R F' B L F L' L' F' U B' L U D B' B' F' R F B' U D' U' U' D L U'

**Human solve 1 (layer-wise):**
<!-- layer 1 -->
F' U B' B' R' F' U' U' L U D' D' R' D R B' D B rot_wo R' D R L' D D L D' R' D R rot_yr
<!-- layer 2 -->
U rot_wo L' U L U rot_wo R U' R' U' L' U L U rot_wo R U' R' U rot_wo L' U L U rot_wo R U' R'
<!-- layer 3 -->
F R U R' U' F' rot_wr R U R' U R U U R' U U R U' L' U R' U' L rot_wo U R U' L' U R' U' L R' D' R D R' D' R D U' R' D' R D R' D' R D R' D' R D R' D' R D U

= F' U B' B' R' F' U' U' L U D' D' R' D R B' D B rot_wo R' D R L' D D L D' R' D R rot_yr U rot_wo L' U L U rot_wo R U' R' U' L' U L U rot_wo R U' R' U rot_wo L' U L U rot_wo R U' R' F R U R' U' F' rot_wr R U R' U R U U R' U U R U' L' U R' U' L rot_wo U R U' L' U R' U' L R' D' R D R' D' R D U' R' D' R D R' D' R D R' D' R D R' D' R D U

**DeepCubeA solve:**
U' L U' L F' R' L' L' B L F B U' L' D' F F D L B' L' F L B R' D F' D R D R' D' F D' D' R

## Scramble 5
**Scramble:**
R D' R' L' U D' F R U' L L F R L F R' U R' D U' B F R' D R U' U' D' L' B

**Human solve 1 (layer-wise):**
<!-- layer 1 -->
R B U L U' B' U' F U D L' D L R' D' R D R' D' R L D' L' D' R D' D' R' rot_yg
<!-- layer 2 -->
R U R' rot_wr U' L' U' L rot_wr U R U R' rot_wr U' L' U' L U U R U R' rot_wr U' L' U' L rot_wb U U L' U' L rot_wo U R U R' U U L' U' L rot_wo U R U R'
<!-- layer 3 -->
F R U R' U' F' U R U R' U R U U R' U rot_wb U' L' U R U' L U R' R' D' R D R' D' R D U' R' D' R D R' D' R D R' D' R D R' D' R D U' R' D' R D R' D' R D U' R' D' R D R' D' R D R' D' R D R' D' R D U'

**DeepCubeA solve:**
U U R D' F' U' F B' L' B' D R L' F' L' F D F' F' L F R F' L' D U' R B

## Scramble 6
**Scramble:**
D L' F' L D R' F' D L' F' R' D' D' B U D' B D U' F' U' B' F' L' L' D' F R D' L'

**Human solve 1 (layer-wise):**
<!-- layer 1 -->
F' L' D R R L' F L L B' L' D L' D L D D F D' F' D R D' R' D D L D' L' D F' D F rot_yg
<!-- layer 2 -->
L' U L U F U' F' L U' L' U' B' U B U R' U R U B U' B' R U' R' U' F' U F
<!-- layer 3 -->
U U F R U R' U' R U R' U' F' U' R U R' U R U U R' U U' L' U R U' L U R' R' D' R D R' D' R D U' R' D' R D R' D' R D R' D' R D R' D' R D U' R' D' R D R' D' R D U' R' D' R D R' D' R D R' D' R D R' D' R D U'

**DeepCubeA solve:**
F U B R' U B' D L B' U' L U B B D' U R' B U' B' R D
