from sympy.combinatorics import Permutation
import numpy as np

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