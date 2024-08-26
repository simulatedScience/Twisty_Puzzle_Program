"""
implementation of an A* algorithm for solving a given twisty puzzle
"""
import time
from copy import deepcopy

import numpy as np
from sortedcontainers import SortedDict

from .ai_modules.twisty_puzzle_model import perform_action
from .ai_modules.q_puzzle_class import Puzzle_Q_AI
from .ai_modules.v_puzzle_class import Puzzle_V_AI
from .ai_modules.greedy_solver import Greedy_Puzzle_Solver
# from .ai_modules.nn_puzzle_class import Puzzle_Network

def solve_puzzle(
        start_state: list[int],
        ACTIONS_DICT: dict[str, list[list[int]]],
        SOLVED_STATE: list[int],
        ai_class: Puzzle_Q_AI | Puzzle_V_AI | Greedy_Puzzle_Solver,
        max_time: float = 60,
        WEIGHT: float = 0.1):
    """
    inputs:
    -------
        start_state - (list) - scrambled state of the puzzle, that shall be solved
        ACTIONS_DICT - (dict) - dictionary containing all availiable moves for the puzzle
        SOLVED_STATE - (list) - solved state representation as for the Q-Learning
        ai_class - (Puzzle_Q_AI) or (Puzzle_V_AI) or (Puzzle_Network) - an instance of the Q/V-learning puzzle class or the puzzle network class
            this determines what is used for the solving process
            the Q/V-table or neural network should already be loaded.
        max_time - (float) - maximum time (in seconds) allowed for finding the solution
        WEIGHT - (float) - weight for weighted A* search. 1 for normal A*

    returns:
    --------
        - list/tuple/str of moves chosen to solve the puzzle
    """
    # def _get_key(key):
    #     """
    #     helper function for max() to get the best action from open_states
    #     """
    #     return open_states[key][0]
    def seq_length_from_key(key):
        return len(key[1])

    end_time = time.time() + max_time

    # open_states = {():(0, start_state)} # init starting state with value 0, no actions taken so far
    open_states = SortedDict({(0,tuple(start_state)):()})
    # open_states = SortedDict({(0, ): start_state})
    closed_states = dict()


    while time.time() < end_time:
        # best_action_seq = max(open_states, key=_get_key)
        # best_action_seq = open_states.peekitem(index=-1)
        # value, puzzle_state = open_states[best_action_seq]
        solution_sequence = expand_node(#best_action_seq,
                                        open_states,
                                        closed_states,
                                        ACTIONS_DICT,
                                        SOLVED_STATE,
                                        ai_class,
                                        WEIGHT=WEIGHT)
        if solution_sequence is not None:
            print(f"Searched {len(closed_states) + len(open_states)} state-action pairs to find a solution.")
            print(f"Maximum search depth was {max([seq_length_from_key(key) for key in open_states.keys()])} moves.")
            return " ".join(solution_sequence)
    print(f"Searched {len(closed_states) + len(open_states)} state-action pairs but found no solution.")
    print(f"Maximum search depth was {max([seq_length_from_key(key) for key in open_states.keys()])} moves.")
    return ""


def expand_node(#action_seq,
                open_states,
                closed_states,
                ACTIONS_DICT,
                SOLVED_STATE,
                ai_class,
                WEIGHT=0.1):
    """
    for all possible actions in [ACTIONS_DICT], add the action to [action_seq] and add that to open_states, unless the state resulting from that action was already visited and had a better value than it has now.

    inputs:
    -------
        action_seq - (tuple) - 
        open_states - (dict) - 
        closed_states - (dict) - 
        ACTIONS_DICT - (dict) - 
        SOLVED_STATE - (list) - 
        ai_class - (Puzzle_Q_AI) or (Puzzle_V_AI) or (Puzzle_Network) - an instance of the Q/V-learning puzzle class or the puzzle network class
            this determines what is used for the solving process
            the Q/V-table or neural network should already be loaded.
        WEIGHT - (float) - weight factor in [0,1] for weighted A*. 
            default value .1

    returns:
    --------
        None if no solution was found,
        (tuple) action_key sequence of the solution if it was found.
    """
    (prev_value, prev_state),  action_seq= open_states.popitem(index=0)
    # prev_value, prev_state = open_states.pop(action_seq)
    for action_key, action_cycles in ACTIONS_DICT.items():
        puzzle_state = list(prev_state)
        perform_action(puzzle_state, action_cycles)
        new_action_seq = action_seq + (action_key,)
        if puzzle_state == SOLVED_STATE:
            return new_action_seq
        # start_time = time.perf_counter()
        value = -get_a_star_eval(prev_value, prev_state, ai_class, WEIGHT=WEIGHT)
        # end_time = time.perf_counter()
        # print(f"evaluation of state took {(end_time-start_time)*1000:5} ms.")

        state_tuple = tuple(puzzle_state)
        if not state_tuple in closed_states:
            # state was not seen before -> explore
            open_states[(value, state_tuple)] = new_action_seq
        else:
            if value < closed_states[state_tuple]:
                # found better path to a state visited before.
                # delete from closed_states and add to open_states
                del(closed_states[state_tuple])
                open_states[(value, state_tuple)] = new_action_seq
                # open_states[new_action_seq] = (value, puzzle_state)
        closed_states[tuple(prev_state)] = prev_value


def get_a_star_eval(prev_value, prev_state, ai_class, WEIGHT=0.1):
    """
    evaluate the current sequence of actions according to the usual formula of weighted A*:
        f(s) = WEIGHT * g(s) + h(s)
    
    inputs:
    -------
        action_key - (str) - new action_key added to the currently investigated action sequence
        prev_value - (float) - value of the current action sequence without `action_key` added to it
        prev_state - (list) - resulting state of the current action sequence without `action_key` added to it
        ai_class - (Puzzle_Q_AI) or (Puzzle_V_AI) or (Puzzle_Network) - an instance of the Q/V-learning puzzle class or the puzzle network class
            this determines what is used for the solving process
            the Q/V-table or neural network should already be loaded.
        WEIGHT - (float) - weight in [0,1] representing lambda in the above equation.

    returns:
    --------
        (float) - representing f(s)
    """
    return WEIGHT*prev_value + ai_class.get_state_value(tuple(prev_state))#, action_key, action_cycles)
    # if isinstance(ai_class, Puzzle_Q_AI):
    #     return WEIGHT*prev_value-WEIGHT + get_q_value(tuple(prev_state), action_key, ai_class)
    # if isinstance(ai_class, Puzzle_V_AI):
    #     return WEIGHT*prev_value-WEIGHT + get_v_value(tuple(prev_state), action_cycles, ai_class)
    # if isinstance(ai_class, Puzzle_Network):
    #     return WEIGHT*prev_value-WEIGHT + get_nn_value(prev_state, action_cycles, ai_class)


def get_q_value(state, action_key, ai_class):
    """
    calculates the q-values assigned to the given state-action_key pair by the given Q-table

    inputs:
    -------
        state - (tuple) - the current puzzle state as a tuple
        action_key - (str) - the action_key of interest
        ai_class - (Puzzle_Q_AI) - an instance with Q-table already loaded (otherwise the solver is completely random)

    returns:
    --------
        (float) - value of the given state-action_key pair in range [0,1]. 
            0 if the key doesn't exist
    """
    try:
        return ai_class.q_table[(state, action_key)]
    except KeyError:
        return 0
    except TypeError:
        return ai_class.q_table[(tuple(state), action_key)]


def get_v_value(state, action_cycles, ai_class):
    """
    calculates the q-values assigned to the given state-action pair by the given Q-table

    inputs:
    -------
        state - (tuple) - the current puzzle state as a tuple
        action_cycles - (list) of (list) of (int) - the action of interest
        ai_class - (Puzzle_V_AI) - an instance with V-table already loaded (otherwise the solver is completely random)

    returns:
    --------
        (float) - value of the given state-action pair in range [0,1]. 
            0 if the key doesn't exist
    """
    temp_state = list(state)
    perform_action(temp_state, action_cycles)
    new_state = tuple(temp_state)
    try:
        return ai_class.v_table[new_state]
    except KeyError:
        return 0


def get_nn_value(state, action, ai_class):
    """
    calculates the value of the given state-action pair with the neural network given in ai_class

    inputs:
    -------
        state - (list) - the current puzzle state as a list
        action - (str) - the action of interest
        ai_class - (Puzzle_Network) - puzzle Network class instance with trained network ai_class.model
    """
    # # start_time = time.time()
    # # value = ai_class.model.predict([ai_class.prepare_state(state) + ai_class.ACTION_VECTOR_DICT[action] for action in ai_class.ACTION_VECTOR_DICT], use_multiprocessing=True)[0]
    # value = ai_class.model.predict([ai_class.prepare_state(state) + ai_class.ACTION_VECTOR_DICT[action]], use_multiprocessing=False)[0]
    # # end_time = time.time()
    # # print(f"Neural network prediction took {(end_time-start_time)*1000:5} ms.")
    # return value
    temp_state = list(state)
    perform_action(temp_state, action)
    nn_input = np.array([temp_state + ai_class.SOLVED_STATE])
    try:
        return ai_class.neural_net.predict(nn_input)[0]
    except KeyError:
        return 0
