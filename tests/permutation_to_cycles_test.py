"""
This file is meant to demonstrate how a permutation is converted between list and cyclic forms.

We want consistent behavior with sympy permutations.
Therfore [0,1,2,4][5][6] is equivalent to [1,2,4,3,0,5,6].
"""


from sympy.combinatorics import Permutation
import numpy as np

def cyclic_to_list(cyclic_form: list[list[int]], size: int) -> np.ndarray:
    """
    Convert a permutation from cyclic form to list form.
    """
    list_form = np.arange(size)
    for cycle in cyclic_form:
        # apply cycle to list_form
        first_elem = cycle[0]
        # for elem in cycle:
        for elem in cycle[-1:0:-1]:
            list_form[elem], list_form[first_elem] = list_form[first_elem], list_form[elem]
    return list_form

def permutation_cycles_to_tensor(state_length: int, action: list[list[int]]) -> np.ndarray:
    """
    Convert a permutation in cycle notation to a tensor.

    Args:
        action (list[list[int]]): permutation in cycle notation

    Returns:
        np.ndarray: permutation as a tensor
    """
    STICKER_DTYPE = np.uint16
    permutation = np.arange(state_length, dtype=STICKER_DTYPE)
    for i, cycle in enumerate(action):
        for j, element in enumerate(cycle):
            permutation[element] = cycle[(j+1) % len(cycle)]
    return permutation

n = 7
# perm = [4,0,1,3,2,5,6]
perm = [1,2,4,3,0,5,6]
# desired cyclic form: [0,1,2,4]
array = list(range(n))
# array = ["a", "b", "c", "d", "e", "f", "g"]
sy_perm = Permutation(perm, size=n)


nparray = np.array(list(range(n)))


print("perm:", perm)
print("cyclic form:", sy_perm.cyclic_form)
print("applied perm:", sy_perm(array))

print("np_perm:", nparray[perm])
print("perm from cycle:      ", cyclic_to_list(sy_perm.cyclic_form, n))
print("perm from cycle in rl:", permutation_cycles_to_tensor(n, sy_perm.cyclic_form))