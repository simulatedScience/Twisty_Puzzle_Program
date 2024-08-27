"""
This module implements a greedy solver for twisty puzzles based on dense reward counting the number of correct points up to symmetry.
"""
import random # for choosing between multiple best actions
if __name__ != "__main__":
    from .twisty_puzzle_model import perform_action
else:
    from twisty_puzzle_model import perform_action


class Greedy_Puzzle_Solver():
    def __init__(self,
                 ACTIONS_DICT,
                 SOLVED_STATE,
                 reward_dict={
                    "exact_solved":500,
                    "solved_up_to_symmetry":100,
                    "unsolved_factor":1,
                 },
                 puzzle_name=None,):
        """
        initialize a puzzle for training via v-learning (assign a value to each state)

        inputs:
        -------
            ACTIONS_DICT - (dict) - dictionary containing all possible actions as cycles
                keys are the names of the actions
            SOLVED_STATE - (list) of ints - the solved state. Each integer represents one color
            reward_dict - (dict) - dict containing rewards for certain events must have keys:
            name - (str) - name of the puzzle
        """
        if puzzle_name is None:
            self.name = "twisty_puzzle #0"
        else:
            self.name = puzzle_name
        
        self.ACTIONS_DICT = ACTIONS_DICT
        self.ACTION_KEYS = list(self.ACTIONS_DICT.keys())
        self.N_ACTIONS = len(self.ACTION_KEYS)
        self.SOLVED_STATE = SOLVED_STATE

        self.reward_dict = reward_dict

        # initialize list of solved states considering rotations
        solved_states: list[list[int]] = get_symmetric_solvable_states(SOLVED_STATE, ACTIONS_DICT)
        self.get_state_value: callable = most_correct_points_reward_factory(solved_states, self.reward_dict)
    
    def choose_action(self, state: list[int]) -> str:
        """
        choose the action that leads to the state with the highest value.
        If multiple moves have the same value, choose a random one.

        inputs:
        -------
            state - (list) - the current state of the puzzle

        returns:
        --------
            (str) - the name of the chosen action
        """
        best_actions: list[str] = []
        best_value: float = float("-inf")
        
        for action in self.ACTION_KEYS:
            new_state = perform_action(state.copy(), self.ACTIONS_DICT[action])
            value = self.get_state_value(new_state)
            if value > best_value:
                best_actions = [action]
                best_value = value
            elif value == best_value:
                best_actions.append(action)
        # choose random action with maximum value
        best_action = random.choice(best_actions)
        return best_action

def get_symmetric_solvable_states(
            solved_state: list[int],
            actions_dict: dict[str, list[list[int]]],
            rotations_prefix: str = "rot_",
        ) -> list[list[int]]:
    """
    Get all possible states that are solvable by the given actions_dict and are symmetric to the solved_state.
    The original solved_state will be the first entry in the list.

    Args:
        solved_state (list[int]): The solved state of the puzzle.
        actions_dict (dict[str, list[list[int]]]): The dictionary of actions that can be performed on the puzzle.

    Returns:
        (list[list[int]]): The list of symmetric solvable states (starting with the original solved_state).
    """
    rotated_solved_states: list[list[int]] = [solved_state]
    for move in actions_dict:
        if not move.startswith(rotations_prefix):
            continue
        rotated_solved_states.append(perform_action(solved_state.copy(), actions_dict[move]))
    return rotated_solved_states


def most_correct_points_reward_factory(solved_states: list[tuple[int]], rewards: dict[str, float]) -> callable:
    def most_correct_points_reward(state):
        """
        Count the number of points that are in the correct position considering several possible solved states. This is especially useful when considering any rotation of the solved state as solved.

        Args:
            state (np.ndarray): The current state of the environment.
            # action
            solved_states (list[np.ndarray]): The solved states of the environment.

        Returns:
            (float): The reward in range [0, 1].
            (bool): True if the puzzle is solved, False otherwise
        """
        if state == solved_states[0]:
            return rewards["exact_solved"]#, True

        max_correct_points = 0
        for solved_state in solved_states:
            correct_points = sum([p1 == p2 for p1, p2 in zip(state, solved_state)])
            max_correct_points = max(max_correct_points, correct_points)
        match_percentage = max_correct_points/len(state)
        done = 1-match_percentage < 1e-5
        if done:
            reward = rewards["solved_up_to_symmetry"]
        else:
            reward = rewards["unsolved_factor"] * match_percentage
        return reward#, done
    return most_correct_points_reward



def merge_dicts(dict_1, dict_2):
    """
    add all entries of dict_2 to dict_1.
    keys that already exist will be overwritten.
    """
    for key, val in dict_2.items():
        dict_1[key] = val
    return dict_1

# if __name__ == "__main__":
#     print()