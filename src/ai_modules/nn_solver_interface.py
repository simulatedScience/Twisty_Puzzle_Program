"""
This module implements a class to enable the use of a trained neural network-based agent with the common interface for puzzle solvers, crucially implementing a `choose_action` method with standard signature.

Author: Sebastian Jost
"""
import json
import os
import tkinter as tk
from tkinter.filedialog import askopenfilename

import gymnasium as gym
import numpy as np
from stable_baselines3 import PPO

from .nn_rl_environment import Twisty_Puzzle_Env, puzzle_info_to_np
from .nn_rl_training import setup_training, get_action_index_to_name
from src.algorithm_generation.algorithm_generation import get_inverse_moves_dict

AI_FILES_FOLDER_NAME: str = "ai_files"
MODEL_SNAPSHOT_FOLDER_NAME: str = "model_snapshots"


class NN_Solver():
    def __init__(self,
            ACTIONS_DICT: dict[str, list[list[int]]],
            SOLVED_STATE: list[int],
            model_path: str,
            deterministic: bool = False
        ):
        """
        Initialize a class to use a trained neural network-based agent to solve a puzzle.
        This class implements a common interface for puzzle solvers for the RL-agents.
        
        Args:
            ACTIONS_DICT (dict[str, list[list[int]]]): dictionary containing available moves as permutations in cyclic form
            SOLVED_STATE (list[int]): the solved state of the puzzle as list of color indices
            model_path (str): path to the trained model or puzzle name. If only a puzzle name is given, load the latest model for that puzzle. Otherwise, load the model from the given path.
        """
        self.solved_state: list[int] = SOLVED_STATE
        self.actions_dict: dict[str, list[list[int]]] = ACTIONS_DICT

        self.np_solved_state, self.np_actions, _ = puzzle_info_to_np(SOLVED_STATE, ACTIONS_DICT, base_actions=None)
        self.action_index_to_name: dict[int, str] = get_action_index_to_name(ACTIONS_DICT)
        
        self.inverse_moves_dict: dict[str, str] = get_inverse_moves_dict(ACTIONS_DICT)
        
        self.deterministic: bool = deterministic
        
        exp_folder_path: str = get_experiment_folder(model_path)
        if not AI_FILES_FOLDER_NAME in model_path:
            model_path: str = exp_folder_path
        self.env, self.reward_func = load_environment(
            solved_state=SOLVED_STATE,
            actions_dict=ACTIONS_DICT,
            exp_folder_path=exp_folder_path)
        self.model: PPO = load_model(
            model_path=model_path,
            env=self.env)

    def choose_action(self, state: list[int]) -> str:
        """
        Choose an action for the given state using the NN-based agent `self.model`.
        
        Args:
            state (list[int]): the current state of the puzzle as list of color indices
        
        Returns:
            str: the name of the chosen action
        """
        # 1. convert the state to the observation format
        np_state: np.ndarray = np.array(state)
        # 2. get action from the model
        action, _ = self.model.predict(np_state, deterministic=self.deterministic)
        # 3. get name of chosen action
        action_name = self.action_index_to_name[int(action)]
        # invert action if AI was trained before 2024_10_05 because until then, permutations were applied incorrectly
        # if True: # placeholder condition
        #     action = self.actions_dict[action_name]
        #     max_cycle_order = max([len(cycle) for cycle in action])
        #     if max_cycle_order > 2:
        #         action_name: str = self.inverse_moves_dict[action_name]
        return action_name

def load_environment(
            solved_state: list[int],
            actions_dict: dict[str, list[list[int]]],
            exp_folder_path: str,
    ) -> tuple[gym.Env, callable]:
    """
    Load puzzle environment from the given path
    """
    # load experiment configuration
    with open(os.path.join(exp_folder_path, "training_info.json"), "r") as file:
        exp_config: dict = json.load(file)
    # get puzzle name as parent folder of exp_folder_path
    # if not MODEL_SNAPSHOT_FOLDER_NAME in exp_folder_path:
    try:
        puzzle_name: str = exp_folder_path.split(os.sep)[-2]
    except IndexError:
        puzzle_name: str = exp_folder_path.split("/")[-2]
    # else:
    #     puzzle_name: str = os.path.basename(exp_folder
    # create environment
    file_solved_state, file_actions_dict, reward_func = setup_training(
            puzzle_name=puzzle_name,
            base_actions=exp_config["base_actions"],
            reward=exp_config["reward"]
    )
    if file_actions_dict != actions_dict:
        raise ValueError(f"Given actions do not match the ones used for training the agent at {exp_folder_path}")
    if file_solved_state != solved_state:
        raise ValueError(f"Given solved state does not match the one used for training the agent at {exp_folder_path}")
    # load training info
    env = Twisty_Puzzle_Env(
        solved_state=file_solved_state,
        actions=file_actions_dict,
        base_actions=exp_config["base_actions"],
        max_moves=exp_config["max_moves"],
        initial_scramble_length=exp_config["start_scramble_depth"],
        success_threshold=exp_config["success_threshold"],
        reward_func=reward_func,
    )
    return env, reward_func

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
        models_path: str = os.path.join(exp_folder_path, MODEL_SNAPSHOT_FOLDER_NAME)
        # model files are named by the number of training steps
        model_files: list[str] = sorted([file for file in os.listdir(models_path) if file.endswith(".zip")])
        model_file: str = model_files[-1]
        model_path = os.path.join(models_path, model_file)
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
        models_folder: str = os.path.join("src", AI_FILES_FOLDER_NAME, puzzle_name)
        # training run folder names start with the datetime => sort by name
        experiment_folders: list[str] = sorted(os.listdir(models_folder))
        # pick the latest model
        experiment_folder: str = experiment_folders[-1]
        return os.path.join(models_folder, experiment_folder)
    # get path before model snapshots
    return model_path.split(MODEL_SNAPSHOT_FOLDER_NAME)[0][:-1]
