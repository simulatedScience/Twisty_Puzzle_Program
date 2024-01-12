import numpy as np

def generate_maze(width: int, height: int, wall_percentage: float = 0.5, epsilon: float = 0.5):
  """
  generate a maze with start and end point and the given dimensions.
  start and goal have at least distance of `(width + height)//2 - 2`
  1. choose random start and goal (not equal)
  2. generate a maze with randomly placed walls
  3. generate a random path from start to goal
  4. remove walls from path to guarantee a solution
  5. clean up any inaccessible free positions

  Args:
      width (int): width of the maze
      height (int): height of the maze
      wall_percentage (float): percentage of walls in the maze before solution path generation
  
  Returns:
      (np.ndarray): maze as 0-1 array (0=free, 1=wall)
      (np.ndarray): start position
      (np.ndarray): goal position
  """
  # 1. choose random start and goal (not equal)
  start_pos = np.array([np.random.randint(0, width), np.random.randint(0, height)])
  goal_pos = np.array([np.random.randint(0, width), np.random.randint(0, height)])
  while reward_manhattan(start_pos, goal_pos) > -(width + height)//2 + 1:
    goal_pos = np.array([np.random.randint(0, width), np.random.randint(0, height)])

  # 2. generate a maze with randomly placed walls
  maze = np.random.choice([0, 1], size=(width, height), p=[1-wall_percentage, wall_percentage])
  
  # 3. generate a random path from start to goal
  path = generate_path(start_pos, goal_pos, maze, epsilon=epsilon)

  # 4. remove walls from path to guarantee a solution
  for pos in path:
    maze[pos[0], pos[1]] = 0
  
  # 5. clean up any inaccessible free positions
  maze = cleanup_maze(maze, start_pos)

  print(f"generated maze of size {width}x{height} with {wall_percentage*100:.0f}% walls and {epsilon}-greedy path generation:")
  print_maze(maze, start_pos, goal_pos)

  return maze, start_pos, goal_pos


def generate_path(start_pos: np.ndarray, goal_pos: np.ndarray, maze: np.ndarray, 
  epsilon: float = 0.4):
  """
  generate a random path from start to goal by using an epsilon-greedy policy and manhattan distance to the goal.
  choode random action with probability `epsilon`, otherwise choose random action that maximizes manhattan reward to goal.

  Args:
      start_pos (np.ndarray): start position
      goal_pos (np.ndarray): goal position
      maze (np.ndarray): maze as 0-1 array (0=free, 1=wall)
  
  Returns:
      (np.ndarray): path as list of positions
  """
  # initialize variables
  path = [start_pos]
  current_pos = start_pos
  # generate path
  while np.any(current_pos != goal_pos):
    # choose random action with probability epsilon
    if np.random.random() < epsilon:
      action = np.random.choice([0, 1, 2, 3])
      path.append(get_new_pos(current_pos, action, maze))
      current_pos = path[-1]
    # otherwise choose random action that maximizes manhattan reward for goal
    else:
      manhattan_distances = np.zeros(4, dtype=np.int32)
      new_positions = np.zeros((4, 2), dtype=np.int32)
      for action in range(4):
        new_pos = get_new_pos(current_pos, action, maze, ignore_walls=True)
        new_positions[action, :] = new_pos
        manhattan_distances[action] = reward_manhattan(new_pos, goal_pos)
      # choose random action with max reward
      action = np.random.choice(np.where(manhattan_distances == manhattan_distances.max())[0])
      path.append(new_positions[action, :])
      current_pos = new_positions[action, :]
  return path


def cleanup_maze(maze: np.ndarray, start_pos: np.ndarray):
  """
  cleanup the maze by removing all free positions that are not accessible from the start position.
  Procedure:
  1. use breadth-first-search to find all accessible positions from start position
  2. remove all free positions that are not accessible

  Args:
      maze (np.ndarray): maze as 0-1 array (0=free, 1=wall)
      start_pos (np.ndarray): start position

  Returns:
      (np.ndarray): cleaned maze as 0-1 array (0=free, 1=wall)
  """
  # 1. use breadth-first-search to find all accessible positions from start position
  accessible_positions = np.zeros(maze.shape, dtype=bool)
  accessible_positions[start_pos[0], start_pos[1]] = True
  bfs_fringe = [start_pos]
  while len(bfs_fringe) > 0:
    current_pos = bfs_fringe.pop(0)
    for action in range(4):
      new_pos = get_new_pos(current_pos, action, maze, ignore_walls=False)
      if not accessible_positions[new_pos[0], new_pos[1]]:
        accessible_positions[new_pos[0], new_pos[1]] = True
        bfs_fringe.append(new_pos)

  # 2. remove all free positions that are not accessible
  maze[accessible_positions == False] = 1
  return maze


def get_new_pos(pos: np.ndarray, action: int, maze: np.ndarray, ignore_walls: bool = False):
  """
  get new position after taking an action disregarding any walls

  Args:
      pos (np.ndarray): current position
      action (int): action to take
      maze (np.ndarray): maze as 0-1 array (0=free, 1=wall)
      ignore_walls (bool, optional): if True, ignore walls and move freely. Defaults to False.

  Returns:
      (np.ndarray): new position
  """
  x,y = pos
  new_x, new_y = x, y
  # move
  if action == 0: # up
    new_y = min(maze.shape[1] - 1, y + 1)
  elif action == 1: # right
    new_x = min(maze.shape[0] - 1, x + 1)
  elif action == 2: # down
    new_y = max(0, y - 1)
  elif action == 3: # left
    new_x = max(0, x - 1)
  else:
    raise ValueError("Invalid action. Valid options are: 0, 1, 2, 3")
  if (not ignore_walls) and maze[new_x, new_y] == 1:
    return pos # don't move if there is a wall and ignore_walls is False
  return np.array([new_x, new_y], dtype=np.int32)


def print_maze(grid: np.ndarray, start_pos: np.ndarray = None, goal_pos: np.ndarray = None):
  """
  prints the maze. ⬜ = empty space, ⬛ = wall

  Args:
      grid (np.ndarray): the grid with walls represented by 1 and empty space by 0
  """
  grid = grid.copy()
  if not start_pos is None:
    grid[start_pos[0], start_pos[1]] = 2
  if not goal_pos is None:
    grid[goal_pos[0], goal_pos[1]] = 3
  for row in grid:
    for cell in row:
      if cell == 0:
        print("⬜", end="")
      elif cell == 1:
        print("⬛", end="")
      elif cell == 2:
        print("🟢", end="")
      elif cell == 3:
        print("🔴", end="")
    print() # new line

def reward_manhattan(state: np.ndarray, goal: np.ndarray):
  """
  Compute the negative manhattan distance between the state and the goal.

  Args:
      state (torch.tensor): the current state
      goal (torch.tensor): the goal state

  Returns:
      torch.tensor: the manhattan distance between the state and the goal
  """
  return -np.sum(np.abs(state - goal))

if __name__ == "__main__":
  maze, start_pos, goal_pos = generate_maze(20, 35, wall_percentage=0.5, epsilon=0.5)
  maze[start_pos[0], start_pos[1]] = 2
  if maze[goal_pos[0], goal_pos[1]] == 1:
    print("Warning: Goal position is a wall.")
  maze[goal_pos[0], goal_pos[1]] = 3
  print_maze(maze)