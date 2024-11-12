"""
This module implements a simple CLI for testing and evaluating a trained RL model.
"""

import os
import tkinter as tk
from tkinter.filedialog import askopenfilename

if __name__ == "__main__":
    import sys, inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    parent2dir = os.path.dirname(parentdir)
    sys.path.insert(0,parent2dir)
from src.ai_modules.nn_rl_testing import test_from_file


def test_from_file_cli(
        ai_files_path: str = "ai_files",
        test_scramble_length: int = 50,
        test_max_moves: int = None, # use same as during training
        num_tests: int = 100,
    ):
    """
    1. request the user to pick a model file or experiment folder to test.
    2. let user enter parameters for testing.
    3. run the tests and save results to file.
    4. print the results.
    5. ask user if more tests are to be run.
    
    Args of this function are used as default values for CLI, if the user doesn't enter other values.
    
    Args:
        test_scramble_length (int, optional): default values for CLI: length of the scrambles to test. Defaults to 50.
        test_max_moves (int, optional): default values for CLI: maximum number of moves to test. Defaults to None.
        num_tests (int, optional): default values for CLI: number of tests to run. Defaults to 100.
    """
    # raise NotImplementedError("TODO")
    # 1. request the user to pick a model file or experiment folder to test.
    while True:
        try:
            exp_folder_path, model_snapshot_steps = pick_model(ai_files_path)
            break
        except FileNotFoundError as exception:
            print(exception)
            print(f"Please select a experiment folder (containing puzzle definition and training info) or model-file.")
            continue
        except SystemExit as exception:
            print(exception)
            print("Exiting.")
            return

    test_from_file(
        exp_folder_path=exp_folder_path,
        model_snapshot_steps=model_snapshot_steps,
        test_scramble_length=test_scramble_length,
        test_max_moves=test_max_moves,
        num_tests=num_tests,
    )
    
    
def pick_model(ai_files_path: str) -> str:
    root = tk.Tk()
    file_path = askopenfilename(
        initialdir=ai_files_path,
        title="Select a model file or experiment folder to test",
        filetypes=[("All files", "*.*"), ("model files", "*.zip")],
    )
    root.withdraw()
    
    if "model_snapshots" in file_path:
        model_snapshot_steps: int = int(file_path.split("_")[-2])
        sep = "/" if "/" in file_path else "\\"
        exp_folder_path = "/".join(file_path.split(sep)[:-2])
    # check if user selected valid experiment folder
    elif "model_snapshots" in os.listdir(file_path):
        # find model with highest step count
        model_snapshot_steps = 0
        for model_snapshot in os.listdir(os.path.join(file_path, "model_snapshots")):
            steps = int(model_snapshot.split("_")[-2])
            if steps > model_snapshot_steps:
                model_snapshot_steps = steps
        exp_folder_path = file_path
    else:
        raise FileNotFoundError(f"Invalid file selected:\n  {file_path}")
    return exp_folder_path, model_snapshot_steps
    
    
    # raise NotImplementedError("TODO")
    # if file_path == "":
    #     # abort with suitable exit error
    #     raise SystemExit("No file selected.")
    # # check if the user selected a file or a folder
    # if file_path.endswith(".zip"):
    #     # remove model name and checkpoint folder from path
    #     exp_folder_path: str = file_path # TODO
    #     # extract number of steps from model name
    #     model_snapshot_steps: int = "" # TODO
    # else: # user chose a folder
    #     # check if folder is valid (contains traing_info.json and puzzle_definizion.xml)
    #     exp_folder_path: str = file_path
    #     # check if folder is valid experiment folder
    #     if not os.path.exists(os.path.join(exp_folder_path, "training_info.json")):
    #         raise FileNotFoundError(f"Invalid folder:\n  {exp_folder_path} does not contain `training_info.json`")
    #     if not os.path.exists(os.path.join(exp_folder_path, "puzzle_definition.xml")):
    #         raise FileNotFoundError(f"Invalid folder:\n  {exp_folder_path} does not contain `puzzle_definition.xml`")
    #     # extract number of steps from training_info.json
    #     model_snapshot_steps: int = ""
    
    
if __name__ == "__main__":
    test_from_file_cli(
        test_scramble_length=200,
        test_max_moves=200,
        num_tests=1000,
    )