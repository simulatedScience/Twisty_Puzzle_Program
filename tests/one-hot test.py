from sklearn.preprocessing import OneHotEncoder
import random


def gen_L(max_len=100_000):
    L = []
    for _ in range(max_len):
        L.append(random.choice(items))
    return L


def get_state_2(int_list):
    new_L = list()
    for item in int_list:
        new_L += encoder_dict[item]
    return new_L


items = [1,2,3,4]
encoder_dict = {1:[1,0,0,0],
                2:[0,1,0,0],
                3:[0,0,1,0],
                4:[0,0,0,1]}

L = gen_L(10)
print(L)

enc = OneHotEncoder(categories=[[1,2,3,4]]*10, dtype=int)
# enc = OneHotEncoder(dtype=int)
enc.fit([L])
print(list(enc.transform([L]).toarray()[0]))
print(get_state_2(L))