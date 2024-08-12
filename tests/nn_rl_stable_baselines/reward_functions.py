
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
    """
    Calculate the reward based on the euclidean distance between the current state and the solved state. Note that this does not produce useful results when the state is a vector of integers representing colors. In that case the colors would not be treated equally.
    """
    diff = state - solved_state
    distance = np.linalg.norm(diff)
    reward = 1 - distance
    done = distance < 1e-3
    # print("euclidean reward: ",
    #       state,
    #       solved_state,
    #       f"reward = {reward}",
    #       sep="\n",
    #       end="\n\n")
    return reward, done

def correct_points_reward(state, action, solved_state):
    """
    Count the number of points that are in the correct position.

    Args:
        state (np.ndarray): The current state of the environment.
        # action
        solved_state (np.ndarray): The solved state of the environment.

    Returns:
        (float): The reward in range [0, 1].
    """
    correct_points = np.sum(state == solved_state, axis=-1)
    reward = correct_points/state.shape[-1]
    done = 1-reward < 1e-5
    if done:
        reward = 100.
    # print("correct points reward: ",
    #       state,
    #       solved_state,
    #       f"reward = {reward}",
    #       sep="\n",
    #       end="\n\n")
    return reward, done

def most_correct_points_reward(state, action, solved_states: list[np.ndarray]):
    """
    Count the number of points that are in the correct position considering several possible solved states. This is especially useful when considering any rotation of the solved state as solved.

    Args:
        state (np.ndarray): The current state of the environment.
        # action
        solved_states (list[np.ndarray]): The solved states of the environment.

    Returns:
        (float): The reward in range [0, 1].
    """
    max_correct_points = 0
    for solved_state in solved_states:
        correct_points = np.sum(state == solved_state, axis=-1)
        max_correct_points = max(max_correct_points, correct_points)
    reward = correct_points/state.shape[-1]
    done = 1-reward < 1e-5
    if done:
        reward = 100.
    # print("most correct points reward: ",
    #       state,
    #       solved_states,
    #       f"reward = {reward}",
    #       sep="\n",
    #       end="\n\n")
    return reward, done