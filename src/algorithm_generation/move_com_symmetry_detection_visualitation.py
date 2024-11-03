"""
Visualize how the move-based symmetry detection works.
"""

import os
if __name__ == "__main__":
    import sys, inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    parent2dir = os.path.dirname(parentdir)
    sys.path.insert(0,parent2dir)


import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import vpython as vpy

from src.algorithm_generation.algorithm_generation_CLI import load_twisty_puzzle
from src.algorithm_generation.move_com_symmetry_detection import reduce_to_coms
from src.algorithm_generation.test_symmetry_plane_detection import set_equal_aspect_3d


def main(
        puzzle_name: str = None,
        save_folder: str = "",
    ):
    """
    
    """
    # 0. load a puzzle
    puzzle, puzzle_name = load_twisty_puzzle(puzzle_name)
    X, X_colors = get_colored_puzzle_points(puzzle)
    # 1. create plot
    fig, ax = create_3d_plot()
    # 2. plot colored puzzle points with mpl
    points = plot_puzzle_points(ax, X, X_colors, alpha=1)
    wait_to_continue(
            fig,
            save_path=save_folder + "/1_colored_points.png",
    )
    remove_artists(points)
    # 3.1 for each move, highlight its affected points by making all others slightly transparent
    reduced_moves: list[str] = []
    for move in puzzle.moves:
        inverse_name = move[:-1] if move.endswith("'") else move + "'"
        if inverse_name not in reduced_moves:
            reduced_moves.append(move)

    move_com_artists: list[plt.Artist] = []
    for i, move in enumerate(reduced_moves):
        move_artists = highlight_move_points(
            ax,
            puzzle.moves[move],
            X,
            X_colors,
            min_alpha=0.2,
        )
        wait_to_continue(
            fig,
            save_path=save_folder + f"/2.{i}.1_move_{move}_points.png",
            text=f"Showing points affected by move {move}.\n",
            )
        # 3.2 draw that move's COM and lines to the affected points
    
        com, lines = draw_move_com_and_lines(
            ax,
            puzzle.moves[move],
            X,
        )
        move_com_artists.append(com)
        wait_to_continue(
            fig,
            save_path=save_folder + f"/2.{i}.2_move_{move}_lines.png",
        )
        # 3.3 hide lines to affected points
        remove_artists(lines)
        wait_to_continue(
            fig,
            save_path=save_folder + f"/2.{i}.3_move_{move}_com.png",
        )
        remove_artists(move_artists)
    # 4. show all move COMs
    points = plot_puzzle_points(ax, X, X_colors, alpha=.2)
    wait_to_continue(
            fig,
            save_path=save_folder + f"/3_all_coms.png",
        )
    remove_artists(points)
    set_equal_aspect_3d(ax)
    # 5. show p1, p2
    move_coms_dict: dict[str, np.ndarray] = reduce_to_coms(X, {move: puzzle.moves[move] for move in reduced_moves})
    move_coms = list(move_coms_dict.values())
    
    vector_artists: list[plt.Artist] = []
    user_input: str = ""
    while user_input != "next":
        if vector_artists:
            remove_artists(vector_artists)
            vector_artists = vector_artists[:-2]
        vector_artists.append(
            show_random_vector(
                    ax,
                    move_coms,
                    rel_length=1,
                    color="#58f",
                    label="p1",
            ),
        )
        vector_artists.append(
            show_random_vector(
                    ax,
                    move_coms,
                    rel_length=1,
                    color="#2d2",
                    label="p2",
            ),
        )
        user_input = wait_to_continue(
            text="Type 'next' to continue, or anything else to regenerate p1, p2 randomly.\n",
            )
    
    if save_folder:
        fig.savefig(save_folder + "/5_p1_p2.png")
    # 6. show t1, t2
    user_input: str = ""
    while user_input != "next":
        if len(vector_artists) > 2:
            remove_artists(vector_artists[-2:])
            vector_artists = vector_artists[:-2]
        vector_artists.append(
            show_random_vector(
                    ax,
                    move_coms,
                    rel_length=.7,
                    color="#259",
                    label="t1",
            ),
        )
        vector_artists.append(
            show_random_vector(
                    ax,
                    move_coms,
                    rel_length=0.7,
                    color="#090",
                    label="t2",
            ),
        )
        user_input = wait_to_continue(
            text="Type 'next' to continue, or anything else to regenerate t1, t2 randomly.\n",
            )
    if save_folder:
        fig.savefig(save_folder + "/6_t1_t2.png")
    # 7. show rotated p1, p2
    
    wait_to_continue()
    os._exit(0)


##### helper functions #####

def wait_to_continue(
        fig: plt.Figure = None,
        save_path: str = "",
        text: str = "",
        time: float = 0.05,
    ) -> str:
    """
    Wait for the given time (to show the current plot), then wait for user input.
    If figure and save_path are given, save the figure and wait for user input.
    """
    plt.pause(time)
    user_input = input(text + "Press Enter to continue...")
    if fig and save_path:
        fig.savefig(save_path)
    return user_input

def remove_artists(artists: list) -> None:
    """
    Remove the given artists from the plot.
    """
    if isinstance(artists, list):
        for artist in artists:
            remove_artists(artist)
    elif isinstance(artists, plt.Artist):
        artists.remove()

def get_colored_puzzle_points(puzzle: "Twisty_Puzzle") -> tuple[np.ndarray, np.ndarray]:
    """
    Load the points and colors of a puzzle.

    Args:
        puzzle_name (str): name of the puzzle

    Returns:
        np.ndarray: 3D coordinates of all points of the puzzle
        np.ndarray: RGB colors of all points of the puzzle
    """
    point_dicts = puzzle.POINT_INFO_DICTS
    points: list[vpy.vector] = [point["coords"] for point in point_dicts]
    point_coordinates: np.ndarray = np.array([[p.x, p.y, p.z] for p in points])
    vpy_point_colors: list[vpy.vector] = [point["vpy_color"] for point in point_dicts]
    point_colors: np.ndarray = np.array([[c.x, c.y, c.z] for c in vpy_point_colors])
    return point_coordinates, point_colors


##### main visualization functions #####

def create_3d_plot(
        bg_color: tuple[float, float, float] = (.95, .95, .95, 0.3)
    ) -> tuple[plt.Figure, Axes3D]:
    """
    Create a 3D plot with equal aspect ratio.
    """
    fig = plt.figure(
        figsize=(8, 8)
    )
    ax: Axes3D = fig.add_subplot(
        111,
        projection='3d',
    )
    ax.xaxis.set_pane_color(bg_color)
    ax.yaxis.set_pane_color(bg_color)
    ax.zaxis.set_pane_color(bg_color)
    fig.subplots_adjust(
        left=0,
        right=1,
        bottom=0,
        top=1,
    )
    return fig, ax

def plot_puzzle_points(
        ax: Axes3D,
        X: np.ndarray,
        X_colors: np.ndarray,
        size: int = 100,
        alpha: float = 1,
    ) -> plt.Artist:
    """
    Plot the puzzle points with their colors.
    """
    points = ax.scatter(
        X[:, 0], # x
        X[:, 1], # y
        X[:, 2], # z
        c = X_colors,
        s = size,
        alpha=alpha,
    )
    set_equal_aspect_3d(ax)
    return points

def highlight_move_points(
        ax: Axes3D,
        move_cycles: list[list[int]],
        X: np.ndarray,
        X_colors: np.ndarray,
        size: int = 100,
        min_alpha: float = 0.1,
    ) -> list[plt.Artist]:
    """
    Highlight the points affected by a move by making all others transparent.
    """
    affected_point_indices: list[int] = []
    for cycle in move_cycles:
        affected_point_indices += cycle
    affected_point_indices = sorted(affected_point_indices)
    unaffected_point_indices: list[int] = [i for i in range(len(X)) if i not in affected_point_indices]
    
    affected_points = ax.scatter(
        X[affected_point_indices, 0], # x
        X[affected_point_indices, 1], # y
        X[affected_point_indices, 2], # z
        c = X_colors[affected_point_indices],
        s = size,
        alpha=1,
    )
    unaffected_points = ax.scatter(
        X[unaffected_point_indices, 0], # x
        X[unaffected_point_indices, 1], # y
        X[unaffected_point_indices, 2], # z
        c = X_colors[unaffected_point_indices],
        s = size,
        alpha=min_alpha,
    )
    set_equal_aspect_3d(ax)
    return [affected_points, unaffected_points]

def draw_move_com_and_lines(
        ax: Axes3D,
        move_cycles: list[list[int]],
        X: np.ndarray,
        com_size: int = 100,
        com_color: str = "#808",
        line_width: float = 1,
        line_color: str = "black",
    ) -> list[plt.Artist]:
    """
    Draw the COM of a move and lines to the affected points.
    """
    affected_point_indices: list[int] = []
    for cycle in move_cycles:
        affected_point_indices += cycle
    com = np.mean(X[affected_point_indices], axis=0)
    com_artist = ax.scatter(
        com[0], # x
        com[1], # y
        com[2], # z
        c = com_color,
        s = com_size,
        alpha=1,
    )
    lines: list[plt.Artist] = []
    for point in X[affected_point_indices]:
        lines.append(
            ax.plot(
                [com[0], point[0]], # x
                [com[1], point[1]], # y
                [com[2], point[2]], # z
                color=line_color,
                linewidth=line_width,
            )[0]
        )
    set_equal_aspect_3d(ax)
    return [com_artist, lines]

def show_random_vector(
        ax: Axes3D,
        vec_choices: list[np.ndarray],
        rel_length: float = 1,
        color: str = "#111",
        label: str = None,
    ) -> plt.Artist:
    """
    Show a random vector from the given choices.
    """
    vec: np.ndarray = vec_choices[np.random.choice(len(vec_choices))]
    vec = vec * rel_length
    vec_artist = ax.quiver3D(
        0, 0, 0, # start x,y,z
        vec[0], vec[1], vec[2], # end x,y,z
        color=color,
        label=label,
    )
    if label:
        ax.legend()
        
    return vec_artist

if __name__ == "__main__":
    from tkinter.filedialog import askdirectory
    main(
        puzzle_name="gear_cube_ultimate",
        save_folder=askdirectory(
            title="Choose a folder to save the images."),
    )