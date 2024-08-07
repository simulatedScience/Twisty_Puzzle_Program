# Solving Twisty Puzzles with Reinforcement using Algorithms

## Goals:
1. solve harder puzzles with similar or less compute resources than previously possible
2. produce solutions which are easier for humans to replicate and understand.
    i.e. don't find shortest solutions, but instead ones that generalize well between many different scrambled states of puzzles.

## Approach 1: Extending Action Set with Algorithms and Symmetries
1. use a secondary program to detect rotational symmetries in the puzzle.
2. Use a third program to generate algorithms that can be used to solve the puzzle.
   1. Detected symmetries can be used to filter out variations of the same algorithm in different orientations.
   2. if the group generated by the found algorithms and symmetries is the same as the group generated by the base moves, we are sure that we have found algorithms that are sufficient to solve the puzzle without needing any more base moves.
3. Train an RL agent with the following actions:
   - base moves
   - symmetries (rotate puzzle in 3D space)
   - algorithms (each algorithm in only one orientation)

### Problems:
- Agent rarely uses the algorithms if it has base moves available as well.  
  Since solutions with algorithms are often longer than those without, the direct solutions receive higher rewards since there are fewer discount steps for reward to fade over.
- Training seems to ttake longer, especially initially, since the action space is much larger. (for cubes, add 23 symmetries and usually 3-10 algorithms to just 8-18 base moves)

### Possible Improvements:
- see approach 2

## Approach 2: Replacing Base Actions with Algorithms and Symmetries
steps 1 and 2 as in approach 1.
3. Train an RL agent with the following actions:
   - symmetries (rotate puzzle in 3D space)
   - algorithms (each algorithm in only one orientation)

### Benefits:
- forces agent to use algorithms to solve the puzzle.

### Problems:
- solutions can be longer than using just base moves (even when counting each algorithm as just one move).
- agent can't use setup moves to efficiently solve the puzzle.

### Possible Improvements:
- First, train on just algorithms and symmetries, then add base_moves later on (similar to fine-tuning)
  1. add new output neurons later on
  2. penalize using base moves during early stages of training


## Approach 3: Rewarding Similarity between different Solves
Make the reward for each solve depend on similarity to other solves.

### Benefits:
- No explicit algorithm generation step required

### Problems:
- not guaranteed to find algorithms that are easily understood by humans.
- crafting a suitable reward function is difficult and this function is likely a lot more compute intensive than a binary reward, adding to training time.  
  Expensive reward function may only need to be evaluated at the end of each successfull episode. For example:  
  **reward = success * (_solve similarity to past 100 solves_)**  
  Where `success` is the binary reward.
