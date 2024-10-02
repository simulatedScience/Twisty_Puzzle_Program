"""
This module implements a class to enable the use of a trained neural network-based agent with the common interface for puzzle solvers, crucially implementing a `choose_action` method with standard signature.

Author: Sebastian Jost
"""
import json
import os
import tkinter as tk
from tkinter.filedialog import askopenfilename

import gymnasium as gym
from stable_baselines3 import PPO

from nn_rl_environment import Twisty_Puzzle_Env
from nn_rl_training import setup_training

AI_FILES_FOLDER_NAME: str = "ai_files"
MODEL_SNAPSHOT_FOLDER_NAME: str = "model_snapshots"


class NN_Solver():
    def __init__(self,
            ACTIONS_DICT: dict[str, list[list[int]]],
            SOLVED_STATE: list[int],
            model_path: str
        ):
        """
        Initialize a class to use a trained neural network-based agent to solve a puzzle.
        This class implements a common interface for puzzle solvers for the RL-agents.
        
        Args:
            ACTIONS_DICT (dict[str, list[list[int]]]): dictionary containing available moves as permutations in cyclic form
            SOLVED_STATE (list[int]): the solved state of the puzzle as list of color indices
            model_path (str): path to the trained model or puzzle name. If only a puzzle name is given, load the latest model for that puzzle. Otherwise, load the model from the given path.
        """
        self.ACTIONS_DICT = ACTIONS_DICT
        self.SOLVED_STATE = SOLVED_STATE
        
        exp_folder_path: str = get_experiment_folder(model_path)
        self.env: gym.Env = load_environment(
            solved_state=SOLVED_STATE,
            actions_dict=ACTIONS_DICT,
            exp_folder_path=exp_folder_path)
        self.model: PPO = load_model(
            model_path=model_path,
            env=self.env)

    def choose_action(self, state: list[int]) -> str:
        """
        Choose an action for the given state.
        
        Args:
            state (list[int]): the current state of the puzzle as list of color indices
        
        Returns:
            str: the name of the chosen action
        """
        # 1. convert the state to the observation format
        
        # 2. set environment state to the given state
        
        # 3. get action from the model
        
        # 4. get name of chosen action
        action_name ="" #TODO
        return action_name

def load_environment(
            solved_state: list[int],
            actions_dict: dict[str, list[list[int]]],
            exp_folder_path: str,
    ) -> gym.Env:
    """
    Load puzzle environment from the given path
    """
    # load experiment configuration
    with open(os.path.join(exp_folder_path, "training_info.json"), "r") as file:
        exp_config: dict = json.load(file)
    # create environment
    file_solved_state, file_actions_dict, reward_func = setup_training(
            puzzle_name=exp_config["puzzle_name"],
            base_actions=exp_config["base_actions"],
            reward=exp_config["reward"]
    )
    if file_solved_state != solved_state:
        raise ValueError(f"Given solved state does not match the one used for training the agent at {exp_folder_path}")
    if file_actions_dict != actions_dict:
        raise ValueError(f"Given actions do not match the ones used for training the agent at {exp_folder_path}")
    # load training info
    env = Twisty_Puzzle_Env(
        solved_state=solved_state,
        actions=actions_dict,
        base_actions=exp_config["base_actions"],
        max_moves=exp_config["max_moves"],
        initial_scramble_length=exp_config["start_scramble_depth"],
        success_threshold=exp_config["success_threshold"],
        reward_func=reward_func,
    )
    return env

def load_model(model_path: str, env: gym.Env) -> PPO:
    """
    Load a model from a file.
    
    Args:
        model_path (str): path to the model file or an experiment folder path
        env (gym.Env): the environment to use the model in
    
    Returns:
        PPO: the loaded model instance as sb3.PPO object
    """
    if not MODEL_SNAPSHOT_FOLDER_NAME in model_path:
        exp_folder_path: str = model_path
        # model files are named by the number of training steps
        model_files: list[str] = sorted(os.listdir(exp_folder_path))
        model_file: str = model_files[-1]
        model_path = os.path.join(exp_folder_path, model_file)
    # load the model
    model = PPO.load(
        model_path,
        env=env,
        device="auto",
    )
    return model

def get_experiment_folder(model_path: str) -> str:
    """
    Given a model path or puzzle name, return the path to the experiment folder.
    If given a model path, return the exp. folder that model is inside.
    If given a puzzle name, return the latest experiment folder for that puzzle.

    Args:
        model_path (str): path to the model file or an experiment folder path

    Returns:
        str: path to the experiment folder (usually contains `puzzle_definition.xml` and `training_info.json`)
    """
    if not MODEL_SNAPSHOT_FOLDER_NAME in model_path:
        # only puzzle name is given
        puzzle_name: str = os.path.basename(model_path)
        models_folder: str = os.path.join(AI_FILES_FOLDER_NAME, puzzle_name, MODEL_SNAPSHOT_FOLDER_NAME)
        # training run folder names start with the datetime => sort by name
        experiment_folders: list[str] = sorted(os.listdir(models_folder))
        # pick the latest model
        experiment_folder: str = experiment_folders[-1]
        return experiment_folder
    # get path before model snapshots
    return model_path.split(MODEL_SNAPSHOT_FOLDER_NAME)[0]

def check_actions(actions_dict: dict[str, list[list[int]]], exp_folder_path: str) -> bool:
    """
    Compare the given actions to those in the puzzle definition in the given experiment folder.
    Return True, if they match, False otherwise.

    Args:
        actions_dict (dict[str, list[list[int]]]): the actions to check given with name and permutation in cyclic form
        exp_folder_path (str): path to the experiment folder containing puzzle_definition.xml
    """
    raise NotImplementedError("TODO")
    # TODO

# if __name__ == "__main__":
#     # verify check_actions