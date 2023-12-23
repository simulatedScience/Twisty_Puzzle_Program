from smart_scramble import scramble_n, get_action_orders
import random

def generate_reverse_scramble_dataset(state, actions, max_moves=30, num_scrambles=1000):
    """
    Generate a dataset of reverse scrambles.

    Each data point in the dataset is a state-action pair, where the state is an intermediate
    state of the puzzle, and the action is the last move that led to this state.

    inputs:
    -------
        state - (list) of ints - list representing the initial state of the puzzle
        actions - (dict[str, list[list[int]]]) - dictionary of all possible actions
        max_moves - (int) - maximum number of moves in each scramble
        num_scrambles - (int) - number of scrambles to generate

    returns:
    --------
        (list[tuple[list[int], str]]) - dataset of (state, action) pairs
    """
    dataset = []
    action_orders: dict[str, int] = get_action_orders(actions)
    for _ in range(num_scrambles):
        current_state = state.copy()
        scramble_sequence = scramble_n(current_state, actions, n_moves=max_moves, action_orders=action_orders)

        # Reverse the scramble sequence to get the reverse scramble dataset
        for action_key in reversed(scramble_sequence):
            # Record the state and the action that led to it
            dataset.append((current_state.copy(), action_key))

            # Undo the action to go back to the previous state
            undo_action(current_state, actions[action_key])

    return dataset

def undo_action(state, action):
    """
    Undo the given action on the given state in-place

    inputs:
    -------
        state - (list) of (int) - list representing the state
        action - (list) of (list) of (int) - list representing an action, here as a list of cycles
    """
    for cycle in reversed(action):
        # Apply the cycle in reverse
        temp = state[cycle[-1]]
        for i in range(len(cycle) - 1, 0, -1):
            state[cycle[i]] = state[cycle[i - 1]]
        state[cycle[0]] = temp


if __name__ == "__main__":
    # test puzzle: single face of a Megaminx
    # solved_state = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10] # 0 = center piece
    # actions_dict = {
    #     "r": [[1, 3, 5, 7, 9], [2, 4, 6, 8, 10]],
    #     "r'": [[1, 9, 7, 5, 3], [2, 10, 8, 6, 4]],
    # }
    # test puzzle: 2 intersecting loops, 7 pieces each
    solved_state = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    actions_dict = {
        "r": [[0, 1, 2, 3, 4, 5, 6]],
        "r'": [[0, 6, 5, 4, 3, 2, 1]],
        "l": [[0, 6, 7, 8, 9, 10, 11]],
        "l'": [[0, 11, 10, 9, 8, 7, 6]],
    }
    
    dataset = generate_reverse_scramble_dataset(
        solved_state,
        actions_dict,
        max_moves=3,
        num_scrambles=10,
    )
    for scramble in dataset:
        print(f"state: {scramble[0]}, action: {scramble[1]}")