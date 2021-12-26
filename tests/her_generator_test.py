import random


state_history = list(range(20))
k_for_her = 4
move_number = len(state_history)

for t, state in enumerate(reversed(state_history)):
    for k in range(min(t, k_for_her)):
        new_goal = random.choice(state_history[move_number-t-1:])
        print(state, new_goal)