import random
from copy import deepcopy
from numpy import lcm
from .ai_modules.twisty_puzzle_model import perform_action

def smart_scramble(SOLVED_STATE, ACTIONS_DICT, n_moves):
    scramble_moves = scramble_n(
            SOLVED_STATE,
            ACTIONS_DICT,
            n_moves,
            get_action_orders(ACTIONS_DICT))
    return scramble_moves


def get_action_orders(ACTIONS_DICT) -> dict[str, int]:
    """
    inputs:
    -------
        ACTIONS_DICT - (dict) - dictionary with all possible action names and cycle representations

    returns:
    --------
        (dict[str, int]) - dictionary mapping each action name to its order
    """
    return {action_name:get_action_order(action) for action_name, action in ACTIONS_DICT.items()}


def scramble_n(SOLVED_STATE, ACTIONS_DICT, n_moves, action_orders) -> list[str]:
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
        (list[str]) - state history excluding the solved state
    """
    action_keys = list(ACTIONS_DICT.keys())
    scramble_hist = [] #list of moves
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
            shorten_scramble(scramble_hist, state_hist, action_orders, ACTIONS_DICT)
            # print("shortened:  ", " ".join(scramble_hist))

    return scramble_hist


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
    return lcm.reduce(cycle_lengths)