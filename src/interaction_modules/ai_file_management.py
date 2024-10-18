"""
This module provides functions for loading and managing AI files. For now only loading test data files is supported.

author: Sebastian Jost
"""
import json
import tkinter as tk
from tkinter.filedialog import askopenfilename

def load_test_file(test_file: str | None = None) -> tuple[dict[str, any], str]:
    """
    Prompt the user to select an ai agent test file.

    Args:
        test_file (str, optional): The path to a test file. Defaults to None (prompt the user to select a file).

    Returns:
        None | dict[str, Any]: The loaded test data or None if no file was selected.
        str: The path to the selected file.
    """
    if not test_file:
        root = tk.Tk()
        root.withdraw()
        test_file = askopenfilename(
            initialdir="./src/ai_files",
            title="Select a test file",
            filetypes=[("JSON Test files", "*.json")],
        )
    if not test_file:
        print("No file selected.")
        return None, test_file
    print(f"Selected file: {test_file}")
    with open(test_file) as file:
        data = json.load(file)
    return data, test_file