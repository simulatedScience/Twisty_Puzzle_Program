"""
Calculate the pieces of a twisty puzzle based on the defined moves.
This is version 2, version 1 had too many cases that did not work correctly.

Author: Sebastian Jost

"""
import random
import time
from ..ai_modules.twisty_puzzle_model import perform_action


def detect_pieces(
        moves: list[list[list[int]]],
        n_points: int,
        inverse_dict=None,
        max_moves=1000
        ):
    """
    calculate all pieces of a puzzle, including those only seperable through move sequences that are longer than one move.
    This is achieved by randomly performing [max_moves] moves and cutting pieces every time it's possible. This takes a little bit of time but shouldn't exceed 1s on most common puzzles.
    Due to the choice of using random moves, it is possible that not all pieces are calculated correctly, but that's very, very unlikely unless the puzzle is built specifically to break this algorithm. In that case, just use more moves.
    
    
    """
    start_time = time.perf_counter()
    visited_states = set()
    current_state = list(range(n_points))
    pieces_template =(get_piece_template(moves, n_points,\
            inverse_dict=inverse_dict))
    moves_list = list(moves.values())
    for _ in range(max_moves):
        # choose and apply random move
        move = random.choice(moves_list)
        perform_action(current_state, move)
        # save state, if it is a new state.
        state_tuple = tuple(current_state)
        if not state_tuple in visited_states:
            visited_states.add(state_tuple)
            # get new pieces
            new_pieces = list()
            for piece in pieces_template:
                new_piece = {current_state[i] for i in piece}
                if not new_piece in pieces_template:
                    new_pieces.append(new_piece)
            # if new pieces were found, intersect them with the previous ones.
            if len(new_pieces) > 0:
                pieces_template = (intersect_pieces([pieces_template, new_pieces], n_points))
    end_time = time.perf_counter()
    # print(f"calculation of {max_moves} moves took {end_time - start_time:7} s.")
    anaylse_pieces(pieces_template)
    return pieces_template


def get_piece_template(moves, n_points, inverse_dict=None):
    """
    calculate all puzzle pieces necessary to perform each move at least once.
    """
    move_pieces, movesets, cycle_sets = \
            split_moves(moves, n_points, inverse_dict=inverse_dict)
    puzzle_pieces = intersect_pieces(move_pieces, n_points)
    return puzzle_pieces


def intersect_pieces(move_pieces, n_points):
    """
    calculate the puzzle pieces with all moves taken into consideration.
    the pieces enforced by each move are given.
    """
    puzzle_pieces = move_pieces[0]
    empty_set = set()
    for pieces in move_pieces[1:]:
        for piece in pieces:
            i = 0
            n_pieces = len(puzzle_pieces)
            while i != n_pieces:
                intersect = puzzle_pieces[i] & piece # calculate intersection A&B
                if intersect != empty_set:
                    if intersect != puzzle_pieces[i]:
                        puzzle_pieces[i] -= intersect   # replace piece A with A\B
                        puzzle_pieces.append(intersect) # add piece A&B
                        n_pieces += 1
                    # if intersect != piece:          # add piece B\A
                    #     puzzle_pieces.append(piece-intersect)
                    #     n_pieces += 1
                i += 1
    return puzzle_pieces


def split_moves(moves: dict[str, list[list[int]]], n_points: int, inverse_dict: dict[str, str]=None):
    """
    calculate the pieces necessary to make each move at least once.

    inputs:
    -------
        moves - (dict) - dictionary with move names and cycle lists
            keys are (str)s,
            values are (list)s of (list)s of (int)s -
            every move is represented as a list of cycles
                describing the move
        n_points - (int) - number of points in the puzzle
        inverse_dict - (dict[str, str]) - dictionary that assigns inverse moves
            for each move where one exists.
            keys and values are both move names and therefore (str)s

    returns:
    --------
        (list) of (set)s
    """
    movesets = list()
    cycle_sets = set()
    move_pieces = list()
    if inverse_dict != None:
        calculated_moves = list()
    for move_name, cycles in moves.items():
        if inverse_dict != None:
            # skip move if it's inverse was already investigated
            if inverse_dict[move_name] in calculated_moves:
                continue
            calculated_moves.append(move_name)
        pieces, moveset, new_cycle_sets = \
                split_move(cycles, n_points)
        # save sets of all points affected by each move
        movesets.append(moveset)
        # save sets of all points affected by each cycle in any move
        cycle_sets |= new_cycle_sets
        # save pieces forced by each move
        move_pieces.append(pieces)
    return move_pieces, movesets, cycle_sets


def split_move(move, n_points):
    """
    calculate the pieces that are enforced just by applying the given move.

    inputs:
    -------
        move - (list) of (list)s of (int)s - list of cycles as lists of integers representing a move
        moveset - (set) of (int)s - set of all indices changed by the move
        n_points - (int) - number of points in the puzzle

    returns:
    --------
        (list) of (set)s of (int)s - list of pieces as sets of integers
        (set) of (int)s - set of all points affected by the given move
        (set) of (frozenset)s - set of all cycles as sets of all affected points
    """
    moveset = set()
    cycle_sets = set()
    pieces = list()
    sorted_cycles = sorted(move, key=len)
    last_len = 0
    for cycle in sorted_cycles:
        if last_len != len(cycle):
            pieces.append(set())
        cycle_set = frozenset(cycle)
        pieces[-1] |= cycle_set
        moveset |= cycle_set
        cycle_sets.add(cycle_set)
        last_len = len(cycle)
    del(last_len, sorted_cycles)

    # generate one piece for the unchanged part of the puzzle
    unchanged_piece = set()
    for n in range(n_points):
        if not n in moveset:
            unchanged_piece.add(n)
    pieces.append(unchanged_piece)
    del(unchanged_piece)

    return pieces, moveset, cycle_sets


def anaylse_pieces(pieces):
    """
    categorize pieces by how many points are on them.
    """
    piece_lengths = [len(piece) for piece in pieces]
    for n in set(piece_lengths):
        print(f"Found {piece_lengths.count(n)} pieces with {n} stickers.")