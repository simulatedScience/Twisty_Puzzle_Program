
from typing import Union
import vpython as vpy

def get_move_similarity_classes(
        moves: dict[str, list[list[int]]],
        pieces: list[set[int]] = None,
        points: list[vpy.baseObj] = None,
    ) -> list[set[str]]:
    """
    Given a dict of moves, return a list of sets of moves that are similar to each other.
    Similar moves are likely to be exchangeable in an algorithm to apply the same algorithm in a different orientation.
    
    Moves are separated based on three criteria:
    1. move cycle signature: the lengths of the cycles in the move
    2. piece signature: the number of points in each piece affected by the move
    3. geometry of affected points: the positions of the points affected by the move relative to their COM and the move's rotation axis

    Args:
        moves (dict[str, list[list[int]]]): Dict defining each move with a name and a list of cycles. E.g. {"R": [[0, 1, 2], [3, 4, 5]]}
        

    Returns:
        list[set[str]]: A list of sets of moves that are similar to each other.
    
    Example:
    ```python
    >>> get_move_similarity_classes(
            {
                "R": [[0, 1, 2]],
                "L": [[4, 5, 6]],
                "S": [0, 4], [1, 5], [2, 6]],
            }
        )
    [{'R', 'L'}, {'S'}]
    ```
    """
    # precompute move signatures
    move_signatures: dict[str, tuple[int]] = {move_name: get_move_signatures(move) for move_name, move in moves.items()}
    # precompute piece signatures
    piece_signatures: dict[str, tuple[int]] = {move_name: get_piece_signatures(move, pieces) for move_name, move in moves.items()}
    
    equivalence_classes: set[str] = set()
    for move_name, move in moves.items():
        # get move signature
        move_signature = move_signatures[move_name]
        # get piece signature
        piece_signature = piece_signatures[move_name]
        
        for candidate_class in equivalence_classes:
            # check equivalence of current move to one representative of the candidate class
            representative_move = moves[candidate_class][0]


def is_similar_move(
        move_a_signature: tuple[int],
        move_a_piece_signature: tuple[int],
        move_a_geometry_signature: dict[str, Union[vpy.vector, list[vpy.vector]]],
        move_b_signature: tuple[int],
        move_b_piece_signature: tuple[int],
        move_b_geometry_signature: dict[str, Union[vpy.vector, list[vpy.vector]]],
    ) -> bool:
    """
    Check if two moves are similar based on three criteria:
    1. move cycle signature: the lengths of the cycles in the move
    2. piece signature: the number of points in each piece affected by the move
    3. geometry of affected points: the positions of the points affected by the move relative to their COM and the move's rotation axis

    Args:
        move_a_signature (tuple[int]): _description_
        move_a_piece_signature (tuple[int]): _description_
        move_b_signature (tuple[int]): _description_
        move_b_piece_signature (tuple[int]): _description_
        points (list[vpy.baseObj], optional): _description_. Defaults to None.

    Returns:
        bool: whether the moves are considered similar
    """
    # check move cycle signature
    if move_a_signature != move_b_signature:
        return False
    if move_a_piece_signature != move_b_piece_signature:
        return False
    if compare_move_geometry(move_a_geometry_signature, move_b_geometry_signature):
        return False
    
def compare_move_geometry(
        move_a_geometry_signature: dict[str, Union[vpy.vector, list[vpy.vector]]],
        move_b_geometry_signature: dict[str, Union[vpy.vector, list[vpy.vector]]],
        max_angle_difference: float = vpy.pi,
        tolerance: float = 1e-3,
    ) -> bool:
    """
    Compare the geometry of two moves based on the positions of the points affected by the move relative to their COM and the move's rotation axis
    move geometry signatures are dicts with the following keys:
    - "com" (vpy.vector): the center of mass of the points affected by the move
    - "axis" (vpy.vector): the rotation axis of the move
    - "points" (list[vpy.vector]): the positions of the points affected by the move relative to the COM and the axis
    - "points_angles" (list[float]): the angles of the points projected onto a unit circle in the plane perpendicular to the rotation axis relative to the first point around the move's axis
    
    Args:
        move_a_geometry_signature (dict[str, Union[vpy.vector, list[vpy.vector]]]): move geometry signature for move a
        move_b_geometry_signature (dict[str, Union[vpy.vector, list[vpy.vector]]]): move geometry signature for move b
        
    Returns:
        bool: whether the moves are considered similar
    """
    # move points a to COM of move b
    com_distance: vpy.vector = move_b_geometry_signature["com"] - move_a_geometry_signature["com"]
    shifted_move_a_points: list[vpy.vector] = move_a_geometry_signature["points"] + com_distance
    # rotate points a to align rotation axes of moves a and b
    rotation_axis: vpy.vector = move_a_geometry_signature["axis"].cross(move_b_geometry_signature["axis"])
    rotation_angle: float = move_a_geometry_signature["axis"].diff_angle(move_b_geometry_signature["axis"])
    for point in shifted_move_a_points:
        point.rotate(angle=rotation_angle, axis=rotation_axis)
    # rotate points a around rotation axis of move b to find alginment
    radius_vec_a: vpy.vector = shifted_move_a_points[0] - move_a_geometry_signature["com"]
    for point_b in move_b_geometry_signature["points"]:
        # calculate target angle where to rotate points a
        radius_vec_b: vpy.vector = point_b - move_b_geometry_signature["com"]
        angle: float = radius_vec_a.diff_angle(radius_vec_b)
        # Optimization: Only check up to rotation angle be the move
        if angle > max_angle_difference:
            continue
        # rotate points a to target angle
        for point_a in shifted_move_a_points:
            point_a.rotate(angle=angle, axis=move_b_geometry_signature["axis"])
        # check if points a are now aligned with points b
        if all(vpy.norm(point_a - point_b) < tolerance for point_a, point_b in zip(shifted_move_a_points, move_b_geometry_signature["points"])):
            return True
        # recalculate radius vector of first point of move a since points were rotated
        radius_vec_a: vpy.vector = shifted_move_a_points[0] - move_a_geometry_signature["com"]
    return False


def get_move_signatures(move: list[list[int]]) -> tuple[int]:
    """
    Map a move to an ordered tuple of its cycle lengths.

    Args:
        move (list[list[int]]): The move represented as a list of cycles, 
                                where each cycle is a list of integers representing points.

    Returns:
        tuple[int, ...]: An ordered tuple of the lengths of each cycle in the move.
    """
    cycle_lengths = tuple(sorted(len(cycle) for cycle in move))
    return cycle_lengths

def get_piece_signatures(move: list[list[int]], pieces: list[set[int]]) -> tuple[int]:
    """
    Map a move to the number of points in each piece affected by the move.

    Args:
        move (list[list[int]]): The move represented as a list of cycles.
        pieces (list[set[int]]): The list of pieces, where each piece is a set of point indices.

    Returns:
        tuple[int, ...]: An ordered tuple representing the count of points in each piece affected by the move.
    """
    # Convert move cycles to a set of affected points
    affected_points = set(point for cycle in move for point in cycle)

    # Count the number of affected points in each piece
    affected_counts = []
    for piece in pieces:
        count = len(piece.intersection(affected_points))
        if count > 0:
            affected_counts.append(count)

    return tuple(sorted(affected_counts))


def main(
        puzzle_moves: dict[str, list[list[int]]],
        puzzle_pieces: list[set[int]]):

    # Example usage move_cycle_similarity
    print(f"testing move_cycle_similarity:")
    for move_name, cycles in puzzle_moves.items():
        print(f"move: {move_name}\ncycle lengths: {get_move_signatures(cycles)}")
    # This should return the tuple (2, 3, 3)


    # Example usage pieces_similarity
    print(f"testing pieces_similarity:")
    for move_name, cycles in puzzle_moves.items():
        print(f"move: {move_name}\npieces affected: {get_piece_signatures(cycles, puzzle_pieces)}")
    # This should return a tuple representing the counts of points in each piece affected by the move

if __name__ == "__main__":
    from piece_detection import detect_pieces
    def square_two_puzzle():
        s = [(33, 36), (34, 37), (38, 35), (24, 39), (40, 25), (41, 26), (10, 22), (11, 23), (49, 52), (48, 53), (15, 3), (14, 2), (0, 13), (1, 12), (50, 51)]
        t = [(11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 0, 1), (34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 35)]
        t_inv = [(1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11), (35, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34)]
        b = [(38, 37, 36, 47, 46, 45, 44, 43, 42, 41, 40, 39), (12, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13)]
        b_inv = [(39, 40, 41, 42, 43, 44, 45, 46, 47, 36, 37, 38), (13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 12)]
        
        square_two_moves = {
            "t": t,
            "t'": t_inv,
            "b": b,
            "b'": b_inv,
            "s": s,
        }
        square_two_pieces = detect_pieces(square_two_moves, 54)
        return square_two_moves, square_two_pieces
    
    def skewb_puzzle():
        wbr = [(0, 8, 7), (24, 25, 26), (4, 17, 10), (5, 15, 11), (6, 16, 9)]
        wgo = [(1, 2, 3), (24, 27, 28), (9, 22, 5), (11, 21, 4), (10, 23, 6)]
        ryg = [(13, 12, 14), (26, 29, 27), (16, 23, 11), (17, 21, 9), (15, 22, 10)]
        oyb = [(19, 20, 18), (28, 29, 25), (21, 15, 6), (5, 23, 17), (4, 22, 16)]
        skewb_moves: dict[str, list[list[int]]] = {
            "wbr": wbr,
            "wgo": wgo,
            "ryg": ryg,
            "oyb": oyb,
        }
        skewb_pieces = detect_pieces(skewb_moves, 30)
        return skewb_moves, skewb_pieces
    
    main(*square_two_puzzle())
    # main(*skewb_puzzle())