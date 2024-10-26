"""
Provides functions to rename the rotations of a puzzle to a more human-readable format: Name rotations as `rot_[c1][c2]` where `c1` and `c2` are first letter the color names that are moved to where the white and green faces are in the solved state.

See `doc/puzzle_simulator/rotation_auto_naming.md` for Motivation and approach.
"""
import os
import tkinter as tk

import numpy as np

if __name__ == "__main__":
    import sys, inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    parent2dir = os.path.dirname(parentdir)
    sys.path.insert(0,parent2dir)
from src.puzzle_class import Twisty_Puzzle
from src.ai_modules.ai_data_preparation import state_for_ai

DEFAULT_COLORS_6: dict[str, np.ndarray[np.float32]] = {
    "white":  np.array((0.9, 0.9, 0.9)),
    "yellow": np.array((1.0, 1.0, 0.1)),
    "green":  np.array((0.1, 0.95, 0.1)),
    "blue":   np.array((0.0, 0.5, 1.0)),
    "red":    np.array((1.0, 0.1, 0.1)),
    "orange": np.array((1.0, 0.5, 0.0)),
}
DEFAULT_COLORS_12: dict[str, np.ndarray[np.float32]] = {
    "white":     np.array((1.00, 1.00, 1.00)), # "#ffffff"
    "lime":      np.array((0.50, 1.00, 0.00)), # "#88ff00"
    "olive":     np.array((0.50, 0.50, 0.00)), # "#888800"
    "grey":      np.array((0.55, 0.55, 0.55)), # "#999999"
    "red":       np.array((1.00, 0.10, 0.10)), # "#ff0000"
    "fuchsia":   np.array((1.00, 0.40, 1.00)), # "#ff66ff"
    "purple":    np.array((0.50, 0.00, 0.50)), # "#770077"
    "crimson":   np.array((0.60, 0.07, 0.20)), # "#aa1133"
    "yellow":    np.array((1.00, 1.00, 0.10)), # "#ffee00"
    "blue":      np.array((0.20, 0.33, 0.87)), # "#3355dd"
    "turqouise": np.array((0.07, 0.73, 0.67)), # "#11bbaa"
    "amber":     np.array((0.93, 0.60, 0.00)), # "#ee9900"
}

def find_closest_color(
        rgb_color: np.ndarray[np.float32],
        color_dict: dict[str, np.ndarray[np.float32]]
        ) -> str:
    """
    Find the color name that is closest to the given rgb color in the given color dictionary.
    
    Args:
        rgb_color (np.ndarray): The rgb color to find the closest color name for.
        color_dict (dict[str, np.ndarray]): The color dictionary to find the closest color name in.
    
    Returns:
        str: The color name that is closest to the given rgb color.
    """
    closest_color: str = ""
    min_distance: float = float("inf")
    for color_name, color_rgb in color_dict.items():
        distance = np.linalg.norm(
            np.array(rgb_color) - color_rgb,
            ord=np.inf,
        )
        if distance < min_distance:
            min_distance = distance
            closest_color = color_name
    return closest_color

def rename_rotations(
        puzzle: Twisty_Puzzle,
    ) -> dict[str, str]:
    """
    Find all rotation moves in the puzzle (starting with "rot_") and rename them to a more human-readable format: Name rotations as `rot_[c1][c2]` where `c1` and `c2` are first letter the color names that are moved to where the white and green (lime if there is no green) faces are in the solved state.
    """
    color_idx_solved_state, color_list = state_for_ai(puzzle.SOLVED_STATE)
    n_colors = len(color_list)
    if n_colors == 6:
        target_colors = DEFAULT_COLORS_6
    elif n_colors == 12:
        target_colors = DEFAULT_COLORS_12
    else:
        print("Unsupported number of colors. Auto-naming currently only supports 6 or 12 colors.")
        return {}
    point_colors: list[np.ndarray[np.float32]] = [
        np.array((obj.color.x, obj.color.y, obj.color.z))
        for obj in puzzle.vpy_objects]
    # map colors to their first letter
    color_map: dict[tuple[float, float, float], str] = {
        tuple(color): find_closest_color(color, target_colors) for color in point_colors
    }
    # find indices of white and green/ lime points
    white_idx: list[int] = [i for i, color in enumerate(point_colors) if color_map[tuple(color)] == "white"]
    green_idx: list[int] = [i for i, color in enumerate(point_colors) if color_map[tuple(color)] == "green"]
    if not green_idx:
        green_idx = [i for i, color in enumerate(point_colors) if color_map[tuple(color)] == "lime"]

    renamed_rotations: dict[str, str] = {}
    # for each rotation, apply rotation, then find the colors at the white and green indices
    for move_name in list(puzzle.moves.keys()):
        if not move_name.startswith("rot_"):
            continue
        puzzle.reset_to_solved()
        puzzle.perform_move(move_name)
        state_colors: list[np.ndarray[np.float32]] = [
            tuple((obj.color.x, obj.color.y, obj.color.z))
            for obj in puzzle.vpy_objects]
        white_location_colors: list[str] = [color_map[state_colors[i]] for i in white_idx]
        green_location_colors: list[str] = [color_map[state_colors[i]] for i in green_idx]
        if len(set(white_location_colors)) > 1:
            print(f"Could not find clear color mapping for {move_name}. The colors {set(white_location_colors)} all appear on the formerly white face.")
            continue
        if len(set(green_location_colors)) > 1:
            print(f"Could not find clear color mapping for {move_name}. The colors {set(green_location_colors)} all appear on the formerly green face.")
            continue
        
        # rename the move
        new_move_name = f"rot_{white_location_colors[0][0]}{green_location_colors[0][0]}"
        renamed_rotations[move_name] = new_move_name
        if input(f"Rename {move_name} to {new_move_name}? (y/N): ").lower() == "y":
            puzzle.rename_move(move_name, new_move_name)
        puzzle.reset_to_solved()

    # request user permission to save the renaming changes
    if not renamed_rotations:
        print("No rotations were renamed.")
        return renamed_rotations
    if input("Save renaming changes? (y/N): ").lower() == "y":
        new_puzzle_name = input("Enter new puzzle name (leave empty to overwrite current puzzle or type 'cancel' to cancel): ")
        if new_puzzle_name.lower() == "cancel":
            return renamed_rotations
        if new_puzzle_name:
            puzzle.PUZZLE_NAME = new_puzzle_name
        puzzle.save_puzzle(puzzle.PUZZLE_NAME)
        print(f"Renamed rotations saved as puzzle: {puzzle.PUZZLE_NAME}")

    return renamed_rotations

def rgb_to_hex(color: np.ndarray[np.float32]) -> str:
    """
    Helper function to convert numpy array to hex color
    """
    r, g, b = (color * 255).astype(int)
    return f"#{r:02x}{g:02x}{b:02x}"

def colormap_checker_gui(
    test_colors: dict[str, np.ndarray[np.float32]],
    target_colors: dict[str, np.ndarray[np.float32]],
    ) -> None:
    """
    
    """
    bg_color: str = "#2d2d3d"
    fg_color: str = "#eeeeee"
    # Initialize main window
    root = tk.Tk()
    root.title("Color Mapping Visualization")
    root.configure(bg=bg_color)


    # Display default colors as a table
    frame = tk.Frame(root, pady=10, bg=bg_color)
    frame.pack()

    tk.Label(
        frame,
        text="Default Colors",
        font=("Arial", 15, "bold"),
        bg=bg_color,
        fg=fg_color,
    ).grid(row=0, columnspan=30)
    
    label_width: int = len(max(target_colors.keys(), key=len))
    for col, (name, color) in enumerate(target_colors.items()):
        tk.Label(
            frame,
            text=name,
            font=("Arial", 12, ""),
            width=label_width,
            bg=bg_color,
            fg=fg_color,
        ).grid(row=1, column=col, padx=2, pady=3)
        tk.Label(
            frame,
            width=label_width,
            height=2,
            text="",
            bg=rgb_to_hex(color),
            border=0,
        ).grid(row=2, column=col, sticky="n")

    # Display test colors with mapped colors below
    result_frame = tk.Frame(root, bg=bg_color)
    result_frame.pack(pady=20)

    n_rows = len(test_colors)
    # split at half if more than 6 test colors (round up for first column)
    split_index: int = (n_rows + 1) // 2 if n_rows > 6 else 6
    col_offset: int = 0
    for row, (test_name, test_color) in enumerate(test_colors.items()):
        closest_name = find_closest_color(test_color, target_colors)
        closest_color = target_colors[closest_name]

        if row >= split_index:
            row -= split_index
            col_offset = 5

        # Display each row with test color and closest color mapping
        tk.Label(
            result_frame,
            text=test_name,
            font=("Arial", 12),
            bg=bg_color,
            fg=fg_color,
        ).grid(row=row, column=0+col_offset, padx=(5*col_offset + 5, 5))
        tk.Canvas(
            result_frame,
            width=30,
            height=30,
            bg=rgb_to_hex(test_color),
            highlightthickness=0,
        ).grid(row=row, column=1+col_offset, padx=5)
        tk.Label(
            result_frame,
            text="->",
            font=("Arial", 12),
            bg=bg_color,
            fg=fg_color,
        ).grid(row=row, column=2+col_offset, padx=5)
        tk.Canvas(
            result_frame,
            width=30,
            height=30,
            bg=rgb_to_hex(closest_color),
            highlightthickness=0,
        ).grid(row=row, column=3+col_offset, padx=5)
        tk.Label(
            result_frame,
            text=closest_name,
            font=("Arial", 12),
            bg=bg_color,
            fg=fg_color,
        ).grid(row=row, column=4+col_offset, padx=5)

    root.mainloop()

def test_color_map(
        target_color_dicts: list[dict[str, np.ndarray[np.float32]]] = (DEFAULT_COLORS_6, DEFAULT_COLORS_12),
    ):
    """
    Visualize the color mapping between predefined test colors and a set of target color dictionaries in a GUI.
    """
    test_colors: dict[str, np.ndarray[np.float32]] = {
        # blues
        "blue1": np.array((0.0, 0.0, 1.0)),
        "blue2": np.array((0.0, 0.0, 0.9)),
        "blue3": np.array((0.0, 0.5, 0.95)),
        # greens
        "green1": np.array((0.0, 1.0, 0.0)),
        "green2": np.array((0.0, 0.9, 0.0)),
        "green3": np.array((0.2, 0.8, 0.2)),
        # whites
        "white1": np.array((1.0, 1.0, 1.0)),
        "white2": np.array((0.9, 0.9, 0.9)),
        "white3": np.array((0.8, 0.8, 0.8)),
        # yellows
        "yellow1": np.array((1.0, 1.0, 0.0)),
        "yellow2": np.array((0.9, 0.9, 0.0)),
        "yellow3": np.array((0.8, 0.8, 0.2)),
        # "yellow4": np.array((1.0, 0.9, 0.0)),
        # reds
        "red1": np.array((1.0, 0.0, 0.0)),
        "red2": np.array((0.9, 0.0, 0.0)),
        "red3": np.array((0.8, 0.2, 0.2)),
        # oranges
        "orange1": np.array((1.0, 0.5, 0.0)),
        "orange2": np.array((0.9, 0.5, 0.0)),
        "orange3": np.array((0.8, 0.4, 0.2)),
        # limes
        "lime1": np.array((0.5, 1.0, 0.0)),
        "lime2": np.array((0.5, 0.9, 0.0)),
        "lime3": np.array((0.6, 0.8, 0.2)),
        # olives
        "olive1": np.array((0.5, 0.5, 0.0)),
        "olive2": np.array((0.5, 0.5, 0.1)),
        "olive3": np.array((0.6, 0.6, 0.2)),
        # greys
        "grey1": np.array((0.3, 0.3, 0.3)),
        "grey2": np.array((0.5, 0.5, 0.5)),
        "grey3": np.array((0.7, 0.7, 0.7)),
        # fuchsias
        "fuchsia1": np.array((1.0, 0.4, 1.0)),
        "fuchsia2": np.array((0.9, 0.4, 0.9)),
        "fuchsia3": np.array((0.8, 0.2, 0.8)),
        # purples
        "purple1": np.array((0.5, 0.0, 0.5)),
        "purple2": np.array((0.5, 0.0, 0.6)),
        "purple3": np.array((0.4, 0.1, 0.5)),
        # crimsons
        "crimson1": np.array((0.67, 0.07, 0.20)),
        "crimson2": np.array((0.67, 0.07, 0.30)),
        "crimson3": np.array((0.77, 0.17, 0.30)),
        # turquoises
        "turqouise1": np.array((0.07, 0.73, 0.67)),
        "turqouise2": np.array((0.07, 0.73, 0.77)),
        "turqouise3": np.array((0.17, 0.83, 0.77)),
        # ambers
        "amber1": np.array((0.93, 0.60, 0.00)),
        "amber2": np.array((0.93, 0.60, 0.10)),
        "amber3": np.array((0.93, 0.70, 0.30)),
    }
    for target_colors in target_color_dicts:
        colormap_checker_gui(
            test_colors=test_colors,
            target_colors=target_colors,
        )

if __name__ == "__main__":
    # load puzzle
    puzzle = Twisty_Puzzle()
    puzzle.load_puzzle("skewb_sym")
    import time
    time.sleep(3)
    renamed_rotations = rename_rotations(puzzle)
    os._exit(0)
