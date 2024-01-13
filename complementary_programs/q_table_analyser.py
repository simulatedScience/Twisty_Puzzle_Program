import random
from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt
from src.puzzle_class import Twisty_Puzzle
from src.ai_modules.twisty_puzzle_model import perform_action

def plot_q_table(puzzle_name, max_scramble_moves=30, n_scrambles=1000):
    """
    plot average values of the Q-table over the number of scramble moves

    inputs:
    -------
        puzzle_name - (str) - name of an existing puzzle folder
        max_scramble_moves - (int) - maximum number of moves from a solved state
        n_scrambles - (int) - number of scrambles are considered for each difficulty level

    outputs:
    --------
        displays a plot using matplotlib.pyplot
    """
    puzzle = Twisty_Puzzle()
    puzzle.load_puzzle(puzzle_name)
    ACTIONS_DICT = puzzle.moves
    ACTION_ORDERS = {name:get_action_order(action) for name, action in ACTIONS_DICT.items()}
    puzzle.train_q_learning(num_episodes=0) #load the q_table
    max_qs, average_qs, min_qs, considered_values, none_values = \
            get_average_q_values(puzzle, ACTION_ORDERS, max_scramble_moves, n_scrambles)


    labeled_data = {"max_qs":max_qs,
                    "average_qs":average_qs,
                    "min_qs":min_qs}#,
                    # "considered_values":considered_values,
                    # "none_values":none_values}
    # print(average_qs)
    x_values = list(range(1, max_scramble_moves+1))
    for label, y_values in labeled_data.items():
        plt.semilogy(x_values, y_values, ".", label=label)
    plt.grid(True)
    plt.legend()
    plt.show()

def get_average_q_values(puzzle, ACTION_ORDERS, max_scramble_moves, n_scambles=1000):
    """
    generate [n_scrambles] different random scrambles approximately [scramble_difficulty] moves away from a solved state. Then calculate the average over all Q-values in those final scramble states

    inputs:
    -------
        puzzle - (Twisty_Puzzle) - a Twisty_Puzzle object containing information about the relevant puzzle
        ACTION_ORDERS - (dict) - order of each action possible in the puzzle
        max_scramble_moves - (int) - maximum number of moves the scrambled state is from a solved_state
        n_scrambles - (int) - number of scrambles are considered for each difficulty level
    """
    #initialize data lists
    base_list = [0 for _ in range(max_scramble_moves)]

    max_qs = deepcopy(base_list)
    average_qs = deepcopy(base_list)
    min_qs = deepcopy(base_list)
    considered_values = deepcopy(base_list)
    none_values = deepcopy(base_list)

    n_actions = len(puzzle.moves) # = len(ACTION_ORDERS)

    for _ in range(n_scambles):
        state_hist = scramble_n(puzzle.ai_q_class.SOLVED_STATE, puzzle.moves, max_scramble_moves, ACTION_ORDERS)
        for i, state in enumerate(state_hist):
            action_values = get_action_values(puzzle.ai_q_class.Q_table, state, ACTION_ORDERS)
            # maximum q-values
            try:
                max_q = max(action_values)
            except ValueError:
                max_q = float("nan")
            if max_q > max_qs[i]:
                max_qs[i] = max_q
            # minimum q-values
            try:
                min_q = min(action_values)
            except ValueError:
                min_q = float("nan")
            if min_q < min_qs[i]:
                min_qs[i] = min_q
            # number of found q_values
            considered_values[i] += len(action_values)
            # number of unexplored q-values
            none_values[i] += n_actions - len(action_values)
            # average_qs
            average_qs[i] += sum(action_values)
    # divide the q-value sums to get the average
    for i, n_values in enumerate(considered_values):
        if n_values != 0:
            average_qs[i] /= n_values

    return max_qs, average_qs, min_qs, considered_values, none_values



def get_action_values(Q_table, state, ACTIONS_DICT):
    """
    get a list of all values associated to the actions possible in the given state
    """
    action_values = []
    for action in ACTIONS_DICT:
        try:
            action_values.append(Q_table[(tuple(state), action)])
        except KeyError:
            pass
    return action_values


def scramble_n(SOLVED_STATE, ACTIONS_DICT, n_moves, ACTION_ORDERS):
    """
    scrambles the puzzle such that the result state is approximately [n_moves] away from the solved state

    inputs:
    -------
        SOLVED_STATE - (list) - unscrambled initial state of the puzzle
        ACTIONS_DICT - (dict) - dictionary with all possible action names and cycle representations
        n_moves - (int) - number of moves the scrambled state is from a solved_state
        ACTION_ORDERS - (dict) - order of each action possible in the puzzle

    returns:
    --------
        (list) - state history excluding the solved state
    """
    action_keys = list(ACTIONS_DICT.keys())
    scramble_hist = []
    state_hist = [tuple(SOLVED_STATE)]
    state = deepcopy(SOLVED_STATE)
    while len(scramble_hist) < n_moves:
        action = random.choice(action_keys)
        perform_action(state, ACTIONS_DICT[action])
        state_tuple = tuple(state)
        if state_tuple in state_hist:
            # discard last scramble moves as they didn't do anything
            state_index = state_hist.index(tuple(state))
            scramble_hist = scramble_hist[:state_index]
            state_hist = state_hist[:state_index+1]
            continue
        else:
            scramble_hist.append(action)
            state_hist.append(state_tuple)
        if len(scramble_hist) == n_moves:
            # print("\nprevious:   " , " ".join(scramble_hist))
            shorten_scramble(scramble_hist, state_hist, ACTION_ORDERS, ACTIONS_DICT)
            # print("shortened:  ", " ".join(scramble_hist))

    return state_hist[1:]


def shorten_scramble(scramble_hist, state_hist, ACTION_ORDERS, ACTIONS_DICT):
    """
    Try shortening a given scramble by detecting unnecessary repetition of moves
        and replacing them with their inverses.
    This won't always result in a shortest possible scramble to get to the final state.

    This could still be improved by detecting repeated algorithms (any repeated sequence of moves),
        calculating their inverses and replacing them if beneficial.

    inputs:
    -------
        scramble_hist - (list) of stings - list of move names (= action keys) representing the scramble
        state_hist - (list) of tuples - tuples represent each state in the scramble_history
            must not contain any state more than once
            -> no pairs of consecutive action and inverse action in scramble_hist
            state_hist must be one element longer than scramble_hist
        ACTION_ORDERS - (dict) - assigning each action key it's order n such that action^n = identity operation
        ACTIONS_DICT - (dict) - dict of all availiable actions with lists of cycles as values

    returns:
    --------
        None

    outputs:
    --------
        scramble_hist and state_hist may be shortened or changed in-place the scramble itself won't change though. Only how efficient the final state is reached.
    """
    inverse_actions = get_inverse_action_dict(ACTIONS_DICT)

    repeat_counter = 1
    last_action = ""
    i = 0
    while i < len(scramble_hist):
        action = scramble_hist[i]
        if last_action == action:
            repeat_counter += 1
            i += 1
            continue
        # current action is different from the previous one
        elif last_action != '' \
            and repeat_counter > 1 \
            and inverse_actions[last_action] != None \
            and repeat_counter >= ACTION_ORDERS[last_action]//2:
            # although very unlikely for most puzzles: using >= instead of > could shorten the scramble even more but requires additional care to prevent an infinite loop.
            # replace last <repeat_counter> actions with appropriate inverse actions
            n_inv_actions = ACTION_ORDERS[last_action] - repeat_counter
            new_actions = [inverse_actions[last_action]]*n_inv_actions
            scramble_hist[i-repeat_counter:i] = new_actions
            # generate new states and replace the old ones
            new_i = i - repeat_counter + 1
            new_states = gen_new_states(list(state_hist[i-repeat_counter]), new_actions, ACTIONS_DICT)
            state_hist[new_i:i+1] = new_states

            if ACTION_ORDERS[last_action] > 3:
                for j, state in enumerate(new_states):
                    if state in state_hist[:new_i]:
                        state_index = state_hist.index(state)
                        del(state_hist[state_index:new_i])
                        del(scramble_hist[state_index:new_i])
                        new_i = state_index + 1
                    else:
                        new_i += 1
            i = new_i

        repeat_counter = 1
        last_action = action
        i += 1
    #ugly repetition of the shortening code from above
    if repeat_counter > 1 \
        and inverse_actions[last_action] != None \
        and repeat_counter >= ACTION_ORDERS[last_action]//2:
        # although very unlikely for most puzzles: using >= instead of > could shorten the scramble even more but requires additional care to prevent an infinite loop.
        # replace last <repeat_counter> actions with appropriate inverse actions
        n_inv_actions = ACTION_ORDERS[last_action] - repeat_counter
        new_actions = [inverse_actions[last_action]]*n_inv_actions
        scramble_hist[i-repeat_counter:i] = new_actions
        # generate new states and replace the old ones
        new_i = i - repeat_counter + 1
        new_states = gen_new_states(list(state_hist[i-repeat_counter]), new_actions, ACTIONS_DICT)
        state_hist[new_i:i+1] = new_states

        if ACTION_ORDERS[last_action] > 3:
            for j, state in enumerate(new_states):
                if state in state_hist[:new_i]:
                    state_index = state_hist.index(state)
                    del(state_hist[state_index:new_i])
                    del(scramble_hist[state_index:new_i])
                    new_i = state_index + 1
                else:
                    new_i += 1


def gen_new_states(START_STATE, action_hist, ACTIONS_DICT):
    """
    perform the actions given in action_hist on START_STATE
    return a list of all new states visited while applying these actions
    """
    new_states = []
    state = START_STATE
    for action in action_hist:
        perform_action(state, ACTIONS_DICT[action])
        new_states.append(tuple(state))
    return new_states



def get_action_order(action):
    """
    calculate the order of a move given as a list of permutations

    inputs:
    -------
        action - (list) of lists of ints - a move given as a list of cycles

    returns:
    --------
        (int) - the order of the given move
    """
    cycle_lengths = [len(cycle) for cycle in action]
    return np.lcm.reduce(cycle_lengths)


def get_inverse_action_dict(ACTIONS_DICT):
    """
    generates a dictionary that maps every action to it'S inverse
    """
    return {action:get_inverse_action(action, ACTIONS_DICT) for action in ACTIONS_DICT.keys()}


def get_inverse_action(action_key, ACTIONS_DICT):
    """
    inputs:
    -------
        action_key - (str) - an action given by its name that is either its own inverse,
            includes a ' at the end or it's inverse is given by action_key+"'"
    """
    if action_key[-1] == "'":
        return action_key[:-1]
    rev_action = action_key+"'"
    if rev_action in ACTIONS_DICT:
        return rev_action
    order = get_action_order(ACTIONS_DICT[action_key])
    if order == 2: #actions of order 2 are self-inverse
        return action_key
    # print(action_key, "does not have an inverse.")
    return None


if __name__ == "__main__":
    plot_q_table("ivy_cube_3", max_scramble_moves=30, n_scrambles=100)
    # plot_q_table("skewb", max_scramble_moves=30, n_scrambles=1000)