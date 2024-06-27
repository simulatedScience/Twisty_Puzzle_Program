
import numpy as np

def binary_reward(state, action, solved_state):
    done = np.all(state == solved_state, axis=-1)
    if isinstance(done, (bool, np.bool_)):
        reward = 1. if done else 0.
    elif isinstance(done, np.ndarray):
        reward = np.where(done, 1., 0.)
    else:
        raise ValueError(f"Unexpected type for done: {type(done)}")
    return reward, done


def euclidean_distance_reward(state, action, solved_state):
    diff = state - solved_state
    distance = np.linalg.norm(diff)
    reward = 1 - distance
    done = distance < 1e-3
    return reward, done