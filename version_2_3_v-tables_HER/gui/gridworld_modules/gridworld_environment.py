"""
a gridworld environment for reinforcement learning
Implemented to test Hindsight Experience Replay.
"""
import xml.etree.ElementTree as ET
from typing import Tuple

# import torch
import numpy as np

from rl_problem import RLProblem
from reward_functions import reward_01, reward_euclidean, reward_manhattan
from maze_generator import generate_maze

class GridworldEnvironment(RLProblem):
  def __init__(self, size, reward_type="01", goal_type="random", wall_percentage=0.3, path_eps=0.4):
    """
    Initialize the gridworld environment with a `size` x `size` grid.
    States are the position of the agent in the grid.
    Actions are: 0 = up, 1 = right, 2 = down, 3 = left
    Goals are a random position in the grid that is not the start state.


    Args:
        size: number of rows and columns in the grid
        reward_type: "01" or "euclidean"
    """
    self.size = size
    self.goal_type = goal_type
    self.wall_percentage = wall_percentage
    self.path_eps = path_eps
    if reward_type == "01":
      self.reward_function = reward_01
    elif reward_type.lower() == "euclidean":
      self.reward_function = reward_euclidean
    elif reward_type.lower() == "manhattan":
      self.reward_function = reward_manhattan
    else:
      raise ValueError("Invalid reward type. Valid options are: 01, euclidean, manhattan")
    # initialize maze, state and goal
    self.state: "torch.tensor" = None
    self.goal: "torch.tensor" = None
    self.n_goals: int = None
    self.initial_world: "torch.tensor" = None
    self.world: "torch.tensor" = None
    self.generate_maze()
    self.reset()


  def get_num_actions(self):
    return 4

  def get_state_size(self):
    return 4 # position and goal

  def get_max_steps(self):
    return 3 * self.size

  def generate_maze(self):
    """
    Generate walls in the gridworld for the saved size. Walls are represented by 1.
    """
    maze, start, goal = generate_maze(self.size, self.size, self.wall_percentage, self.path_eps)
    self.initial_world = np.array(maze, dtype=np.int8)
    self.start_state = np.array(start, dtype=np.float32) / (self.size - 1)
    self.goal = np.array(goal, dtype=np.float32) / (self.size - 1)
    # number of potential goals
    self.n_goals = np.sum(self.initial_world == 0) - 1 # subtract starting position

  def reset(self) -> Tuple["torch.tensor", "torch.tensor"]:
    """
    Reset the environment to the start state (0,0) and a random goal that is not the start state.

    Returns:
        state: the start state
        goal: a random goal that is not the start state
    """
    # reset state to start position
    self.state = self.start_state.copy()
    self.world = self.initial_world.copy()
    if self.goal_type == "random":
      # choose a random square in world that is not a wall or the start state.
      goal_index = np.random.randint(0, self.n_goals, (1,))[0]
      # choose the goal corresponding to the index
      for i in range(self.size):
        for j in range(self.size):
          if self.world[i, j] == 0:
            if goal_index == 0 and (i, j) != (self.state[0], self.state[1]):
              self.goal = np.array([i, j]) / (self.size - 1)
              break
            else:
              goal_index -= 1
        else:
          continue
        break

    return self.state.copy(), self.goal.copy()


  def step(self, action: int) -> Tuple["torch.tensor", "torch.tensor", bool]:
    """
    Move the agent in the gridworld. If the agent hits a wall or edge of the grid, it stays in the same position.
    Allowed actions are: 0 = up, 1 = right, 2 = down, 3 = left

    Args:
        action: 0 = up, 1 = right, 2 = down, 3 = left
    """
    # get current position
    # get x,y as int
    x, y = int(self.state[0] * (self.size - 1)), int(self.state[1] * (self.size - 1))
    new_x, new_y = x, y
    # move
    if action == 0: # up
      new_y = min(self.size - 1, y + 1)
    elif action == 1: # right
      new_x = min(self.size - 1, x + 1)
    elif action == 2: # down
      new_y = max(0, y - 1)
    elif action == 3: # left
      new_x = max(0, x - 1)
    else:
      raise ValueError("Invalid action. Valid options are: 0, 1, 2, 3")
    # update state
    if not self.world[new_x, new_y] > 0: # if not wall at new position
      self.state = torch.tensor([new_x, new_y]) / (self.size - 1)
    reward, done = self.compute_reward(self.state, self.goal)
    return self.state.clone(), reward, done


  def compute_reward(self, state, goal):
    done = torch.equal(state, goal)
    reward = self.reward_function(state, goal)
    return reward, done

  def __str__(self) -> str:
    """
    return gridworld size
    """
    return f"Gridworld({self.size}x{self.size})"
  
  def convert_to_twisty_puzzle_xml(self, filename):
        """
        Convert the gridworld to a twisty puzzle and save it in XML format.
        :param filename: Name of the file to save the XML.
        """
        root = ET.Element('puzzledefinition')
        points_element = ET.SubElement(root, 'points')
        
        point_index = 0
        point_indices = {}
        # calculate COM of all points from grid size
        com = np.array([self.size / 2, self.size / 2])
        for i in range(self.size):
            for j in range(self.size):
                cell_value = self.initial_world[i][j]
                if (i, j) == tuple(np.array(self.size * self.start_state, dtype=int)):
                    cell_value = 2  # Start
                elif (i, j) == tuple(np.array(self.size * self.goal, dtype=int)):
                    cell_value = 3  # Goal

                color = self.get_color(cell_value)
                point_element = ET.SubElement(points_element, 'point', {'size': '7.0'})
                coords = np.array([i, j], dtype=float)
                # shift coordinates to center of mass
                coords -= com
                coords = ET.SubElement(point_element, 'coords', {'x': '0.0', 'y': str(coords[1]), 'z': str(coords[0])})
                ET.SubElement(point_element, 'color', {'r': str(color[0]), 'g': str(color[1]), 'b': str(color[2])})
                
                point_indices[(i, j)] = point_index
                point_index += 1

        moves_element = ET.SubElement(root, 'moves')
        for i in range(self.size):
            for j in range(self.size):
                if self.initial_world[i][j] != 1:  # Not a wall
                    for di, dj, move_prefix in [(-1, 0, 'v'), (1, 0, 'v'), (0, -1, 'h'), (0, 1, 'h')]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < self.size and 0 <= nj < self.size and self.initial_world[ni][nj] != 1:
                            move_name = f"{move_prefix}{i}_{j}"
                            move_element = ET.SubElement(moves_element, 'move', {'name': move_name})
                            # create cycle entry like <cycle>0, 1, 2, 3</cycle>
                            ET.SubElement(move_element, 'cycle', {}).text = f"{point_indices[(i, j)]}, {point_indices[(ni, nj)]}"


        tree = ET.ElementTree(root)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        ET.indent(tree, space="    ")
        tree.write(filename)

  def get_color(self, cell_value):
      """
      Return the color based on the cell value.
      """
      if cell_value == 0:  # Empty cell
          return 1, 1, 1  # White
      elif cell_value == 1:  # Wall
          return 0, 0, 0  # Black
      elif cell_value == 2:  # Start
          return 0, 1, 0  # Green
      elif cell_value == 3:  # Goal
          return 1, 0, 0  # Red

if __name__ == "__main__":
  import os
  n = 5
  env = GridworldEnvironment(
    size = n,
    goal_type="random",
  )
  print(env)
  print(env)
  env.convert_to_twisty_puzzle_xml(f"gui/puzzles/gridworld_{n}x{n}/puzzle_definition.xml")
