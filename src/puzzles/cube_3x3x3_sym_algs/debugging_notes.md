move F has index 6 in puzzle class with cycles:
```python
    [[9, 38, 35, 51], [12, 37, 32, 52], [15, 36, 29, 53], [0, 2, 8, 6], [1, 5, 7, 3], [4]]
```

in nn_solver, it gets converted to:
```python
    F = np.array([6, 3, 0, 7, 4, 1, 8, 5, 2, 51, 10, 11, 52, 13, 14, 53, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 36, 30, 31, 37, 33, 34, 38, 15, 12, 9, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 35, 32, 29])
```
array of length 54, type uint16 with values from 0 to 53.

- This is a correct conversion of the permutation.
- The action index `6` is indeed mapped to `'F'` inside `NN_solver`, as expected. Note that action keys are sorted alhapbetically before assigning indices.
- the solved state in `NN_solver` is (at least initially) identical to the one used in training.


**Solved state**
[5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]

**State according to `puzzle_class._get_ai_nn_state()` after applying `F` once:**
[5, 5, 5, 5, 5, 5, 5, 5, 5, 1, 4, 4, 1, 4, 4, 1, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 0, 2, 2, 0, 2, 2, 0, 2, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 4, 4, 4]

Expected state:
permutation: `[[9, 38, 35, 51], [12, 37, 32, 52], [15, 36, 29, 53], [0, 2, 8, 6], [1, 5, 7, 3], [4]]`
initial state:    `[5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]`
indices:          `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53]`
expected perm:    `[*, *, *, *, *, *, *, *, *, 0, *, *, *, *, *, *, *, *, *, *, *, *, *, *, *, *, *, *, *, *, *, *, *, *, *, 1, *, 4, 4, *, *, *, *, *, *, *, *, *, *, *, *, 2, *, *]`
perm in rl env:   `[5, 5, 5, 5, 5, 5, 5, 5, 5, 0, 4, 4, 0, 4, 4, 0, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 1, 2, 2, 1, 2, 2, 1, 4, 4, 4, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 2, 2, 2]`
inverse expected: `[*, *, *, *, *, *, *, *, *, 1, *, *, 1, *, *, *, *, *, *, *, *, *, *, *, *, *, *, *, *, *, *, *, *, *, *, 0, *, *, 2, *, *, *, *, *, *, *, *, *, *, *, *, 4, *, *]`
perm gotten:      `[5, 5, 5, 5, 5, 5, 5, 5, 5, 1, 4, 4, 1, 4, 4, 1, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 0, 2, 2, 0, 2, 2, 0, 2, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 4, 4, 4]`

sympy permutation agrees with the puzzle class permutation => change rl env permutations to match that.