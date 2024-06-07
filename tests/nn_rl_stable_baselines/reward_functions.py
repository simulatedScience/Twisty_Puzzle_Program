
import numpy as np

def binary_reward(state, action, solved_state):
    done = np.all(state == solved_state)
    reward = 1 if done else 0
    return reward, done


def euclidean_distance_reward(state, action, solved_state):
    diff = state - solved_state
    distance = np.linalg.norm(diff)
    reward = 1 - distance
    done = distance < 1e-3
    return reward, done