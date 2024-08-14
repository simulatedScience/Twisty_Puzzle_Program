"""
This module provides functions to generate cuboid puzzles (a.k.a. n x m x k Rubik's cubes).
"""

import numpy as np
import matplotlib.pyplot as plt

def generate_cuboid(
        size: tuple[int, int, int],
        cuby_size: float = 1.,
        sticker_offset: float = 0.025,
    ):
    """
    Generate a cuboid of size `size[0] x size[1] x size[2]`, where each cuby has a size of `cuby_size` with stickers offset from the faces by `sticker_offset`.

    Args:
        size (tuple[int, int, int]): The size of the cuboid in the form (width, depth, height).
        cuby_size (float): The size of the cuby.
        sticker_offset (float): The offset of the stickers from the faces of the cuby.
    
    Returns:
        (np.ndarray): The vertices of the cuboid. (shape: (s, 4)), s = number of stickers, fourth component is an integer representing the sticker color by index in the list of the second output
        (np.ndarray): The colors of the stickers. (shape: (6, 3))
    """
    colors = np.array([
        [.1, .8, .1], # green
        [.9, .1, .1], # red
        [.1, .5, .9], # blue
        [1., .5, 0.], # orange
        [.9, .9, .9], # white
        [1., .8, 0.], # yellow
    ])
    
    # construct each face from 5 properties:
    #    start: the location of the first point on the face
    #    dir1: the direction in which the second point is located
    #    dir2: the direction in which the first point of the second row is located
    #    fixed: the axis that is fixed for all points on the face
    #    sign: the sign for the fixed axis (indicating location of the face along that axis)
    # cuby size and offset are automatically computed later
    sticker_coords = []
    face_configs = [
        # Green face (front)
        {
            'start': np.array((-size[0]/2, -size[1]/2, -size[2]/2)),
            'dir1': np.array((1, 0, 0)),
            'dir2': np.array((0, 0, 1)),
            'fixed': 1,
            'sign': -1,
            'color': 0},
        # Red face (right)
        {
            'start': np.array((size[0]/2, -size[1]/2, -size[2]/2)),
            'dir1': np.array((0, 1, 0)),
            'dir2': np.array((0, 0, 1)),
            'fixed': 0,
            'sign': 1,
            'color': 1},
        # Blue face (back)
        {
            'start': np.array((size[0]/2, size[1]/2, -size[2]/2)),
            'dir1': np.array((-1, 0, 0)),
            'dir2': np.array((0, 0, 1)),
            'fixed': 1,
            'sign': 1,
            'color': 2},
        # Orange face (left)
        {
            'start': np.array((-size[0]/2, size[1]/2, -size[2]/2)),
            'dir1': np.array((0, -1, 0)),
            'dir2': np.array((0, 0, 1)),
            'fixed': 0,
            'sign': -1,
            'color': 3},
        # White face (top)
        {
            'start': np.array((-size[0]/2, -size[1]/2, size[2]/2)),
            'dir1': np.array((1, 0, 0)),
            'dir2': np.array((0, 1, 0)),
            'fixed': 2,
            'sign': 1,
            'color': 4},
        # Yellow face (bottom)
        {
            'start': np.array((size[0]/2, size[1]/2, -size[2]/2)),
            'dir1': np.array((-1, 0, 0)),
            'dir2': np.array((0, -1, 0)),
            'fixed': 2,
            'sign': -1,
            'color': 5},
    ]

    for config in face_configs:
        # calculate offset to center the stickers on each cuby
        start_offset = (config['dir1'] + config['dir2']) * cuby_size / 2
        start_offset[config['fixed']] = 0
        # scale to cuby size and add offset
        start = config['start'] * cuby_size + start_offset
        dir1 = config['dir1'] * cuby_size
        dir2 = config['dir2'] * cuby_size
        # calculate coordinate of the fixed axis
        fixed_offset = config['sign'] * (size[config['fixed']] * cuby_size / 2 + sticker_offset)
        # calculate sticker coordinates
        for i in range(size[abs(config['dir1']).argmax()]): # iterate over the first direction
            for j in range(size[abs(config['dir2']).argmax()]): # iterate over the second direction
                pos = start + i * dir1 + j * dir2
                pos[config['fixed']] = fixed_offset
                sticker_coords.append([*pos, config['color']]) # combine coordinates and color index
    
    return np.array(sticker_coords), colors

def define_moves(size: tuple[int, int, int]) -> dict[str, list[list[str]]]:
    """
    Define the base moves for a cuboid of the given shape (x, y, z).
    This method relies on points being ordered exactly as output by the `generate_cuboid` function.

    Args:
        size (tuple[int, int, int]): The size of the cuboid in the form (width, depth, height).

    Returns:
        (dict[str, list[list[str]]]): The base moves for the cuboid with default names represented by permutations as lists of cycles acting on the stickers.
        https://rubiks.fandom.com/wiki/Notation
        https://jperm.net/3x3/moves
        F = turn green face clockwise (90° if x=z, otherwise 180°)
        B = turn blue face clockwise (90° if x=z, otherwise 180°)
        R = turn red face clockwise (90° if y=z, otherwise 180°)
        L = turn orange face clockwise (90° if y=z, otherwise 180°)
        U = turn white face clockwise (90° if x=y, otherwise 180°)
        D = turn yellow face clockwise (90° if x=y, otherwise 180°)
        
        # only for odd number of layers in the corresponding direction:
        M = Median slice. The slice in the middle between L and R in L direction.
        E = Equatorial slice. The slice in the middle between U and D in D direction.
        S = Standing slice. The slice in the middle between F and B in F direction.
        
        # for more than 3 layers in the corresponding direction:
        for faces that are further inwards, the name is prefixed by the number of layers that are further from the center than this face.
        e.g. moves of a 7x7x7 from left to right: L, 2L, 3L, M, 3R, 2R, R
    """
    # calculate number of stickers on each face
    n_stickers = {
        "green": size[0]*size[2],
        "blue": size[0]*size[2],
        "red": size[1]*size[2],
        "orange": size[1]*size[2],
        "white": size[0]*size[1],
        "yellow": size[0]*size[1],
    }
    moves: dict[str, list[list[str]]] = {}
    # U moves
    if size[0] == size[1] and size[2] > 1:
        # 1. define outermost move: U
        # 1.1 define white face cycles

        # 1.2 define cycles of green, red, blue, orange faces

        # 2. define inner moves: 2U, 3U, ...
        for z in range(1, size[2]//2):
            if z > 0:
                name = f"{z+1}U"
            # 2.1 define white face cycles
            moves[name] = [
                
            ]
def plot_points(
        sticker_coords: np.ndarray,
        colors: np.ndarray,
        show_indices: bool = False,
    ):
    """
    Plot the given points and colors in 3D using matplotlib.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    # set aspect ratio to 1
    color_indices = sticker_coords[:, 3].astype(int)
    ax.scatter(
        sticker_coords[:, 0],
        sticker_coords[:, 1],
        sticker_coords[:, 2],
        c=colors[color_indices],
        s=100,
        alpha=1,
    )
    # show sticker index as text at the sticker position
    if show_indices:
        for i, coords in enumerate(sticker_coords):
            ax.text(*coords[:3], f"{i}", color="black")
    # ax.set_box_aspect([1, 1, 1])
    ax.set_aspect("equal")
    plt.show()
    
if __name__ == "__main__":
    # generate 2x3x4 cuboid
    # sticker_coords, colors = generate_cuboid((2, 3, 4))
    sticker_coords, colors = generate_cuboid((2,3,5))
    # sticker_coords, colors = generate_cuboid((5,5,5))
    # sticker_coords, colors = generate_cuboid((3,3,3))
    plot_points(sticker_coords, colors, show_indices=sticker_coords.shape[0] < 100)