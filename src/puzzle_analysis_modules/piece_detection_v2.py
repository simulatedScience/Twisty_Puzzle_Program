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
        inverse_dict: dict[str, str] = None,
        max_moves: int = 1000
        ):
    """
    calculate all pieces of a puzzle, including those only seperable through move sequences that are longer than one move.
    This is achieved by randomly performing [max_moves] moves and cutting pieces every time it's possible. This takes a little bit of time but shouldn't exceed 1s on most common puzzles.
    Due to the choice of using random moves, it is possible that not all pieces are calculated correctly, but that's very, very unlikely unless the puzzle is built specifically to break this algorithm. In that case, just use more moves.

    Args:
        moves (list[list[list[int]]]): list of moves as lists of cycles
        n_points (int): number of points in the puzzle
        inverse_dict (dict[str, str]): dictionary that assigns inverse moves
        max_moves (int): number of moves to perform
    """
    start_time: float = time.perf_counter()
    visited_states: set[tuple[int]] = set()
    current_state: list[int] = list(range(n_points))
    current_pieces: list[set[int]] = get_piece_template(
            moves,
            n_points,
            inverse_dict=inverse_dict)
    moves_list = list(moves.values())
    for n_moves in range(max_moves):
        # choose and apply random move
        move = random.choice(moves_list)
        perform_action(current_state, move)
        # save state, if it is a new state.
        state_tuple = tuple(current_state)
        if not state_tuple in visited_states:
            visited_states.add(state_tuple)
            # get new pieces
            new_pieces = list()
            for piece in current_pieces:
                new_piece = {current_state[i] for i in piece}
                if not new_piece in current_pieces:
                    new_pieces.append(new_piece)
            # if new pieces were found, intersect them with the previous ones.
            if len(new_pieces) > 0:
                current_pieces = (intersect_pieces([current_pieces, new_pieces]))
    end_time = time.perf_counter()
    # print(f"calculation of {max_moves} moves took {end_time - start_time:.2f} s.")
    anaylse_pieces(current_pieces)
    return current_pieces

def get_piece_template(moves, n_points, inverse_dict=None):
    """
    calculate all puzzle pieces necessary to perform each move at least once.
    """
    move_pieces: list[list[set[int]]] = split_moves(moves, n_points, inverse_dict=inverse_dict)

    puzzle_pieces = intersect_pieces(move_pieces)

    return puzzle_pieces

def intersect_pieces(piece_sets: list[list[set[int]]]) -> list[set[int]]:
    """
    Given a list of (partial) partitions `piece_sets` of the point set, calculate the largest partition Pi such that every given partition can be formed by joining elements of Pi.
    
    calculate the puzzle pieces with all moves taken into consideration.
    the pieces enforced by each move are given.

    Args:
        partitions (list[list[set[int]]): list of (partial) partitions of the point set. Partitions may include either all points or only a subset of them. Order of the pieces is irrelevant.
        
    Returns:
        list[set[int]]: list of partitions of the point set.
    """
    updated_pieces = piece_sets[0]
    empty_set = set()
    for pieces in piece_sets[1:]:
        for piece_a in pieces:
            i = 0
            n_pieces = len(updated_pieces)
            while i != n_pieces:
                intersection = updated_pieces[i] & piece_a # calculate intersection B&A
                if intersection != empty_set: # piece_a intersects with a current piece
                    if intersection != updated_pieces[i]: # and is not equal to it
                        updated_pieces[i] -= intersection   # replace piece B with B\A
                        updated_pieces.append(intersection) # add piece B&A
                        n_pieces += 1
                i += 1
    return updated_pieces


def split_moves(
        moves: dict[str, list[list[int]]],
        n_points: int,
        inverse_dict: dict[str, str]=None,
    ) -> tuple[list[set[int]], list[set[int]], set[frozenset]]:
    """
    For each move, calculate the pieces it necessitates by itself. Returns a list of partitions of {1, ..., `n_points`}.

    Args:
        moves (dict[str, list[list[int]]]): dictionary with move names and cycle lists
            every move is represented as a list of cycles
                describing the move
        n_points (int): number of points in the puzzle
        inverse_dict (dict[str, str]): dictionary that assigns inverse moves for each move where one exists.
            keys and values are both move names

    Returns:
        list[list[set[int]]]: list of pieces necessitated by each move. May be shorter than the number of moves since inverse moves are skipped because they yield the same pieces as the original move.
    """
    move_pieces = list()
    if inverse_dict:
        calculated_moves: set[str] = set()
    for move_name, cycles in moves.items():
        # skip move if it's inverse was already investigated
        if inverse_dict:
            if move_name in inverse_dict and inverse_dict[move_name] in calculated_moves:
                continue
            calculated_moves.add(move_name)
        # save pieces forced by each move
        move_pieces.append(split_move(cycles, n_points))
    return move_pieces


def split_move(move: list[list[int]], n_points: int) -> tuple[list[set[int]], set[int], set[frozenset]]:
    """
    Calculate the pieces that are enforced just by applying the given move.
    This splits the puzzle into:
    - one piece for the points unaffected by the move
    - one piece for each unique cycle length in the move

    Algorithm:
    1. sort cycles by length
    2. join cycles of the same length into one piece for each cycle length

    Args:
        move (list[list[int]]): list of cycles as lists of integers representing a move
        n_points (int): number of points in the puzzle

    Returns:
        list[set[int]]: list of pieces as sets of integers
        set[int]: set of all points affected by the given move
        set[frozenset[int]]: set of all cycles as sets of all affected points
    """
    move_pieces = list()
    sorted_cycles = sorted(move, key=len)
    last_len = 0
    for cycle in sorted_cycles:
        if len(cycle) == 1: # ignore cycles with only one point
            continue
        if last_len != len(cycle):
            move_pieces.append(set())
        # add cycle to the last piece that collects cycles of the same length
        move_pieces[-1] |= set(cycle)
        last_len = len(cycle)

    # generate one piece for the unchanged part of the puzzle
    unchanged_piece = set()
    for n in range(n_points):
        for piece in move_pieces:
            if n in piece:
                break
        else:
            unchanged_piece.add(n)
    if len(unchanged_piece) > 0:
        move_pieces.append(unchanged_piece)

    return move_pieces


def anaylse_pieces(pieces):
    """
    categorize pieces by how many points are on them.
    """
    piece_lengths = [len(piece) for piece in pieces]
    for n in set(piece_lengths):
        print(f"Found {piece_lengths.count(n)} pieces with {n} stickers.")
