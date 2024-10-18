

import os, sys, inspect
if __name__ == "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    parent2dir = os.path.dirname(parentdir)
    sys.path.insert(0,parent2dir)
from src.ai_modules.twisty_puzzle_model import perform_action
from src.puzzle_class import Twisty_Puzzle
from src.algorithm_generation.algorithm_analysis import get_inverse_moves_dict
from src.ai_modules.ai_data_preparation import state_for_ai

def analyze_strategy(
        test_data: dict[str, any],
        correctness_threshold: float,
        puzzle: Twisty_Puzzle
        ) -> list[float]:
    """
    
    """
    solved_state, color_list = state_for_ai(puzzle.SOLVED_STATE)
    moves_dict: dict[str, list[list[int]]] = puzzle.moves
    inverse_dict: dict[str, str] = get_inverse_moves_dict(puzzle.moves)
    
    deviations_per_point = [[] for _ in range(len(solved_state))]  # List to track deviations for each point

    for run in test_data["run_info"]:
        agent_moves = run["agent_moves:"].split()
        
        # Reverse the solve sequence
        reverse_moves = [inverse_dict[move] for move in reversed(agent_moves)]
        
        # Copy the solved state to track the current state
        current_state = solved_state[:]
        
        # Track correctness of each point over time
        correctness_history = [[1] * len(solved_state)]  # Start with all points correct
        deviation_move_counts = [-1] * len(solved_state)  # Initialize the first deviation count

        # Apply moves in reverse
        for move_num, move in enumerate(reverse_moves):
            # Apply the move
            perform_action(current_state, moves_dict[move])
            
            # Track correctness
            for i, (current_val, solved_val) in enumerate(zip(current_state, solved_state)):
                correctness_history[i].append(1 if current_val == solved_val else 0)
                
                # Check if the running average falls below the threshold
                if len(correctness_history[i]) >= correctness_threshold * (move_num + 1):
                    # TODO: logic error here. Fix correctness_threshold calculation
                    avg_correctness = sum(correctness_history[i][-correctness_threshold * (move_num + 1):]) / (correctness_threshold * (move_num + 1))
                    if avg_correctness < correctness_threshold and deviation_move_counts[i] == -1:
                        deviation_move_counts[i] = move_num
        
        # Add to overall deviations list
        for i in range(len(solved_state)):
            if deviation_move_counts[i] != -1:
                deviations_per_point[i].append(deviation_move_counts[i])
    
    # Calculate averages for each point
    avg_deviations = [sum(deviation_list) / len(deviation_list) if deviation_list else None for deviation_list in deviations_per_point]
    
    return avg_deviations

if __name__ == "__main__":
    from src.interaction_modules.ai_file_management import load_test_file

    # choose and load test data
    test_file_path: str | None = "C:/Users/basti/Documents/programming/python/Twisty_Puzzle_Program/src/ai_files/cube_3x3x3_sym_algs/2024-09-28_23-37-59/tests/test_2024-09-29_05-31-09.json"
    # test_file_path: str | None = None
    test_data, test_file_path = load_test_file(test_file_path)
    base_path = test_file_path.split("/")[:-2]
    # load corresponding puzzle
    puzzle_definition_path: str = os.path.join(*base_path, "puzzle_definition.xml")
    puzzle_definition_path: str | None = r"C:\Users\basti\Documents\programming\python\Twisty_Puzzle_Program\src\ai_files\cube_3x3x3_sym_algs\2024-09-28_23-37-59\puzzle_definition.xml"
    print(puzzle_definition_path)
    # print(ref_path)
    puzzle = Twisty_Puzzle()
    puzzle.load_puzzle(puzzle_definition_path)

    correctness_threshold = 0.1  # Example threshold for deviation

    avg_deviations = analyze_strategy(
        test_data,
        correctness_threshold,
        puzzle)
    print(avg_deviations)