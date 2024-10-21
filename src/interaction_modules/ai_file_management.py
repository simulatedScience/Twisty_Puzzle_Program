"""
This module provides functions for loading and managing AI files. For now only loading test data files is supported.

author: Sebastian Jost
"""
import json
import os
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

def get_policy_savepath(
        test_file_path: str,
        file_base_name: str,
    ) -> str:
    """
    Given the path to a test file (ending in [exp_folder]/tests/tests_[datetime2].json), create a policy analysis subfolder in [exp_folder].
    Return [file_base_name]_[datetime2].

    Args:
        test_file_path (str): path to the test file
        file_base_name (str): base name for the new file

    Returns:
        str: path to the new file: ...[exp_folder]/policy_analysis/[file_base_name]_[datetime2]
    """
    path_parts: list[str] = test_file_path.split("/")
    test_datetime: str = path_parts[-1][5:-5] # remove "test_" and ".json"
    new_file_name: str = f"{file_base_name}_{test_datetime}"
    # create policy_analysis folder in exp_folder (= path_parts[-3])
    policy_analysis_folder = os.path.join(*path_parts[:-2], "policy_analysis")
    os.makedirs(policy_analysis_folder, exist_ok=True)
    # return path to new file
    return os.path.join(policy_analysis_folder, new_file_name)
