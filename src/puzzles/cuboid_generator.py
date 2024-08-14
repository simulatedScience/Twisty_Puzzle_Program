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
        [.1, .9, .1], # green
        [.1, .5, 1.], # blue
        [1., .5, 0.], # orange
        [1., .1, .1], # red
        [1., .8, 0.], # yellow
        [.9, .9, .9], # white
    ])
    # generate cuboid sticker coordinates for each of the 6 faces
    sticker_coords: list[list[float]] = []
    # green (front) and blue (back) faces
    for sign in [-1, 1]:
        # generate one face
        for x in range(size[0]):
            for z in range(size[2]):
                sticker_coords.append([
                    x*cuby_size - size[0]*cuby_size/2 + cuby_size/2,
                    sign * (size[1]*cuby_size/2 + sticker_offset),
                    z*cuby_size - size[2]*cuby_size/2 + cuby_size/2,
                    0 + (sign>0), # color index 0 or 1
                ])
    # red (right) and orange (left) faces
    for sign in [1, -1]:
        # generate one face
        for y in range(size[1]):
            for z in range(size[2]):
                sticker_coords.append([
                    sign * (size[0]*cuby_size/2 + sticker_offset),
                    y*cuby_size - size[1]*cuby_size/2 + cuby_size/2,
                    z*cuby_size - size[2]*cuby_size/2 + cuby_size/2,
                    2 + (sign>0), # color index 2 or 3
                ])
    # white (top) and yellow (bottom) faces
    for sign in [-1, 1]:
        # generate one face
        for x in range(size[0]):
            for y in range(size[1]):
                sticker_coords.append([
                    x*cuby_size - size[0]*cuby_size/2 + cuby_size/2,
                    y*cuby_size - size[1]*cuby_size/2 + cuby_size/2,
                    sign * (size[2]*cuby_size/2 + sticker_offset),
                    4 + (sign>0), # color index 4 or 5
                ])
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
    )
    # show sticker index as text at the sticker position
    for i, coords in enumerate(sticker_coords):
        ax.text(*coords[:3], f"{i}", color="black")
    # ax.set_box_aspect([1, 1, 1])
    ax.set_aspect("equal")
    plt.show()
    
if __name__ == "__main__":
    # generate 2x3x4 cuboid
    # sticker_coords, colors = generate_cuboid((2, 3, 4))
    sticker_coords, colors = generate_cuboid((2,3,5))
    plot_points(sticker_coords, colors)