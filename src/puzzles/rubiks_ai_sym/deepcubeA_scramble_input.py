"""
This file implements tools to input scramble sequences into the deepcubeA solver website (https://deepcube.igb.uci.edu/) by simulating keyboard inputs.
"""
import time

from pynput.keyboard import Key, Controller

KEYBOARD = Controller()

def press_key(key, shift_modifier: bool = False):
    """
    Presses a key on the keyboard.
    """
    if shift_modifier:
        with KEYBOARD.pressed(Key.shift):
            KEYBOARD.press(key)
            KEYBOARD.release(key)
    else:
        KEYBOARD.press(key)
        KEYBOARD.release(key)

def print_countdown(length: int = 10):
    for i in range(length, 0, -1):
        print(f"\rStarting in {i} seconds...", end="")
        time.sleep(1)
    print("Starting! The programm will automatically press keys now.")

def enter_move_sequence(
        move_sequence: str,
        start_delay: float = 10,
        move_delay: float = 0.2):
    """
    Convert a given move sequence string into a sequence of keypresses.
    
    Args:
        move_sequence (str): The move sequence to input. moves are separated by spaces. Valid moves are:
        F, R, U, B, L, D and their inverses F', R', U', B', L', D'.
        These get converted into key presses
    """
    print_countdown(start_delay)
    for move in move_sequence.split():
        key, shift_modifier = convert_move(move)
        press_key(key, shift_modifier)
        time.sleep(move_delay)

def convert_move(move: str) -> tuple[str, str]:
    """
    Converts a move string into a key press instruction.
    
    Args:
        move (str): A single move to convert.
    
    Returns:
        tuple[str, str]: The key press instruction, consisting of a key and a modifier. This can be passed directly to press_key:
    """
    if "'" in move:
        return move[:-1], True
    return move.lower(), False

def main():
    move_sequence: str = "B D U F F L' F' D R D' L B' D B' D R' D' L R' L' L' D U R' D F' U' R L F'" # 1
    move_sequence: str = "D F L' R F' F' L D' D' L' L' B D U' R' B D' D' B' B' R R D U' F U' B U' F D" # 2
    move_sequence: str = "F' U' U' B' R' F D L R' D F B U' R' F' U D U D B' L U' B' U L B U B U D'" # 3
    move_sequence: str = "F F B' L R F' B L F L' L' F' U B' L U D B' B' F' R F B' U D' U' U' D L U'" # 4
    move_sequence: str = "R D' R' L' U D' F R U' L L F R L F R' U R' D U' B F R' D R U' U' D' L' B" # 5
    move_sequence: str = "D L' F' L D R' F' D L' F' R' D' D' B U D' B D U' F' U' B' F' L' L' D' F R D' L'" # 6
    move_sequence = "F' R' D' U' R' U B R D' F D' U' L' U' D' F B F D D' U R R U' U B' L D' F' D D' U D D' L' R F D' U' D' R' D' U F D' U F B D' B' B U R R' D' D L' B B' R B' D' R' L L B B L' R' U L B B' L F' U R B' U' L' U L' B' B' F' R D L' U F F F' R' R U F R' R' D B'" # 7
    move_sequence = "R F R R L' R R' U' U' L F B U F' F D R' D R' U L' R U' R' R' B F' U' D D F R B' L L R F B L D R U D F F L' U' L F' R U D' U U B' U' F U U' L L D R F' R' F' R' D' B F R' B' B' U' F B' L R L B' B' B F' B D' L F B' B' B F' L R D B L F D' F' F" # 8
    move_sequence = "F' U' D R U' U' L' F U D' B' R B U' L F L' D' F B' U' B U' F R B' B D U L' U' L' B U D L' F' F' U' U' L R F B' F' U' L' R F' F F B B R' L' R' D D B D' B' U R U' F' B F' D' D F F B' F' R U B D' D' R' F D' R L F R' F' B B F' L' F B' B' L L F F F' F' F'" # 9
    move_sequence = "U U R L R' L' L F B L' D L D F B D R' D R' D B F U F U' R' D F R B' L U L' L' F F R' L' L' L B R D' U B B' B' L U' F D' U' B U D B' U' D R U U B' F B F R' B' B U' B' R F D' L U' F' R' L F' R' F' D' U L' D' L' U' D B' U' F B L U U D' L' D U D'" # 10
    move_sequence = "F' U' F F' D D' D R D R' L F' U D' R' L' U D B' B' D R' F L' F R R F' L' L U F' U' F' R' D' L L R' D R' L' F D' L' F L' D' U B' R R' B' R' D' B' D D F F L R' B D R' D' B' R R' B' R' F' D L' D' D U' F F L' U' R' F' L U L' R' U L R D U D L' B B B D F D" # 11
    move_sequence = "B' R B F B' B' B' B' U L' R R' R U' B D U' D D F' F' R L L' B' R' U F' R B R' L F' U B F F' R' F R R' D' D' R R D' L B' F U' U' L U' R D' D R D' R' U' D U' B' D' F' R F U B D B' U' L F' U' F D' U' R' F' B F' B B L' D L B B' U' R F' D' B' D' F D' D U' B'" # 12
    move_sequence = "L' L D B U' U D' L' B D' U' B B D U' U' R' L' U' B B' D' U' B' D' B R' F D' L L' R' F' L B L L' L F R F' D' F' R' R' D L' U' L L' U' L R L' L R' U F' B' D D' R B' F U' B' B' U L' D F' U L L' D R L' B U L' B D R' L' L B' D F' R' L L' U L' D D' L' B U' L' F" # 13
    move_sequence = "D R' F U L R' F' D D U F' L' F' R' D U D F F' F L' F' R F' D L' B' U D R' F' L U' L' L R' L' R U' B B D' R' D F F' U' L D' L R F' R' L' U D B' U' R R' B' F F' R' L L' R F U' D' L' L R' U B L R B L' R F B U' R B' B D' R D D L L R' L' L' D L D R' R" # 14
    move_sequence = "R R U' D' B' U L D' U' F B F L D' B' D R R F' F' U' F' L L B D U L' B B D R' B F L R' L F D B' U' R' F' R L' R D U' R' L L' L' F' B L' U L B' B R F B' B' U' L D U R' B' B U' B' F B' F L' R' R U' B' B R' F R' R' R' B F B' R F' D U D' L' D' B' U' F' D'" # 15
    move_sequence = "D R F U B' B' R' B' B B' B L' L' D' L U' F' B' F' R' D' F R B U B' F F' U' F' F' B B R B' R D' B U D L' R D' F' D R' R' F' U' F L' D D B' D' R' L B F' R U R' U L D' U' U B R R R R R' L' F' L B L' U' D F' B' U U' U F' F L R D' R F' L' U' U R L' L L L'" # 16
    move_sequence = "F F' L' R D' R' R' B U B' R R' L' F' F F D' F D' R B' F F B U' R D U D' R' B U B U' U B' R' B F R' L R D' D D' F' R D' D' U L F' R F D L' L F' L' F L F R' F B B L L U' R U' U' B F F L' B' B U' F D D' L D' B B R L' F R U R D' D L' D U' R' L' D'" # 17
    move_sequence = "L U U L B' U' D' F L' R' L U F U' R' B B' L' U L' B D U' U' D' D' L' D' D' R B B L' R D L F U L' B' D R' B D D R' D' F' U D' R' B R' B L' F' F' L' B L' D' B' L B' B' D D U' L U D' U D' B R' D L' L' D F L' L' L' U' L' B L F F' L' U R R R' D' R' L' R B L'" # 18
    move_sequence = "B D R R' F' L' B F' B B' L F L' D' U' U R R' B' B' U' D U F' R' L' U R' B D' B' F F' R' F' R R' F U R' L' U F' R L' F' U' R L' F' U' U' B U' D' U U' U' U' L' F' F' U B' R B D' U' D' R B' U D' L R U' R' F D R R L D R R' R' B' B R' B D D' R B L R' D B R U" # 19
    move_sequence = "D' R' B B' F F' B L' L' F' D' U' F' D' B U R' U F D' D L' B R' B' D L F U B' U' R' F' L B R L' U' D L' R' U L U F' R' D U F R B' D' D L R' U' D' L R D' B' U' U R' U R' U B R' R' R F F' R' D' U' B B U' U U' D B F R' B' L D B' D' B' U F U' D' U' L' F D F" # 20
    move_sequence = "U' R R' L U' D' B F' F D' L L' F' L L' F D' U' B R R' R' B' U L B' D' L' B B' B' B U R' B R D' U D L' B' D F R' R' B' U' R' B' L U' L' F' B F' D L U' F F B' D D' F U' R D' D' B' B' R U U' L B' L D' F L' U' R R U' U L' F R F' F R' F B' B' D' D' R F' D' L' U'" # 21
    move_sequence = "U' D' B D' R' L F B F B' F B' L F B' D F' U L U B B B R' B' D B' U U' L D D R' F' R' B' D D U F D F' D' F' F B' R' B B D U D B' D' R L D D U R F R R R D' F B D D' U' U' F U' R' L U U' L D L U' L B' D' U L' F' F' R' D' B' D' U R' U' B' U' B D' B" # 22
    move_sequence = "D' L' R F' B' B R' B' L' R' L' D L F' F B L R F' L U F R' L' L L L' U' L' B' R B L L U' L U' U' R' U U' D R' L L U' F R R F U B R L B' F' U' B' U' F B' F L' B U' U B L' D F' F' L B' R' B' B' F' U' U' B R U F' U R' L L' L B D' U' U' D D' D L D' B L' U'" # 23
    move_sequence = "B L' B' B' D L U B R' D' R D' L B R L' L' B B U' B' F U R D U B B D U R' R' B L' B' B' F B B B' L' L' U L' R B' F F R U L' R' F' B R F' U' F' U' R' B F U D R R D' B' R' B' B' U' D U F' U F U R' L B' U L B' U B B D' B F' D L' B R' D R' R' D' U' R" # 24
    move_sequence = "U U D U D' U' B L U' R' F B F' B U R' L' D' B R U' R' B' R F' U' R' B D' D R' D D' R' F F L' B D L U' D' R L' U' B L' B L' D' F' U D' L' D L' L D' L B' U D' B U R' D' U' F' U D F' F' B F L' B' D' U D' U U L L R' D' F' D L D' R F F R F U F' B' L' F' U'" # 25
    move_sequence = "F' U U' U B' L L' D F' D' U' R L' L D' F' L L' U' R F' L' F F' R D' B' F R' U' L U D' B D' R' F' D D L R' U D' U' B R D' L' R F' R U R D B' R F' L D' L' L' R U' B' F B R R' L' U' F B L' L B L' F' B B' U U' L' U U' U D' B L' L' L' R' F B R U R' R' F' R D" # 26
    move_sequence = "F L B B' R D F L' B B' L F' L D B' U D' U L' U L D D' U R' F F R R F F' L R D' U D' D' F L B' D B' U L R' R' D' U' R D D D R L' R D' D' R R' F' R' L' R L' F D' U F F' D' B F' D L' D' U' D D' R U L' R L B' F' D' F' L F L' R U R R F F' B R F L'" # 27
    move_sequence = "D F L L R' D' B' U' B L D B L' U' D R U' B' B R U' D B' U L B D' R' U' B D' F F' U' B' D L' R' B L' R' B' R U L B' B B' U F L' B U' B' U U' F F' D F D' D U U L D U' F R' R B U' U D D D U R F' D' L' L U B' R' F' D F D' R' R F' B' D' R B' U' B D F" # 28
    move_sequence = "U' B' B' B' U R U' B' D' B' R' R' R' F' D L' F R' R L U L F' R F B' D' F L R' R' U' L' D U D' D' F' F F D' L L L D D' L D L L' U' F B' U B D' L' D U' D B L U' D R' L' L L B B U B' L U L' L' D D' R' U' L' L L D' R B D' L' D F' D B' U D R R U D R U" # 29
    move_sequence = "R' D B D R' F B' B B F U F B L' F' F L F' U' R' U' D' D' F F B L' B' B' F' U' U B' U' L' B F' F R' R D' U F D B' B B' R' R F' F F B L U' R B' B' B' D' L' B D D R D B' U F' D B F R R' L' F D U' B U' D U B' L B F F U' U L L B' B' B R' F L' F' U L'" # 30
    move_sequence = "D F' F F F U U' R F F R R' L D B' D B U' U' D' U U' F R' U D U' L R R R L U' F' R' F' L' R B' R B' D L' B F' U L' F U D B' B' L U' F B L U B D U D' B F' L D F D' R' D U' R R F' F' D F' U B' L' R' U' L B' U B' R U B' L F' D U L' L F B' R D U'" # 31
    move_sequence = "F B' D' R' D L' R' D R F' R D' B' D D' B' D' F U R L D B' D L R F' F' R U B' F' L' B' L R' L' L' B' L' R L' U' F' L' R R' F D D' U L' L U B' D U B' R' D' R' L' R' D R' F R U' U U' F' R' F B D R D' B R' L' B B U' U U' U L' R' B' D' L D' R L' F' F F D R F'" # 32
    move_sequence = "L' L' R' U U' D D' L' U' B U' L L' L B' B' D' R B L' B D' D' R' F' D' R U' D D D' U' F U' B' B R D F' R U F' U D B' U B' L' L L R B' R' L B D B' B' U' D' F' D D U' F D' D U' B' L U' F U' U' U B L' U D U L' B' R L D B' B' R' L' L U' D D' F' B' R D' R' R R'" # 33
    move_sequence = "R U' U L L' F' F B D' B F L' R D' F' F B' U F B' R' U' L' U' U F' R' F R L' L' F U U R L' U F' U' D L R U' D' R' R' U' D F R R' B' R B B L U' U' R D' D' B F' D' L' D' F' B' D' B' B' U D F' B U' F F R R' U L' B' L D B' D' U' R' U' B B D' F' F' B' U' F' L U'" # 34
    move_sequence = "D L R' F B' U R R' F' R D' B' U B' B B' D' B' U U F D' L U D' U R U U F' L B' L' F R' D U' B' F' B' U L R R L R U L' L' D R D' F R D R U R U' L U' R B' F L' U D R' D' L' U' D' U F' F' B D B' U' B R' B L L U' F D' B F' L' U' U' D' F R R' D' L' D' R" # 35
    move_sequence = "R R' U F' F U' R F U' R B' L' F' B' F F' U' B F U L D' D D' U' U' R' B' U F D L R' R B' F' U R R L' U B R' U U B F U' B R' R' R' D B R' R' B' L' B' D' F' D U L' D L B B U' F' L R' F R' R' R B D' D B F' F' F B' F' F B R' F' B U D F' D' R F F' L' F F" # 36
    move_sequence = "R' B' U' B F' D' L B U D D' R R' L D' B' D' D F' L' R' F L U D R' U L' D' U U R' F F' R B' B' R' D' F' R B' U B' L L L' D F L U D D F' R' B D' R U R U D L F' D R' R' U' B R' L' R D' L' R' U B B U' L' U D D' F F' D' L R' U' L' L B' D B F B' L R L D'" # 37 # very long solve time and long solution
    move_sequence = "B D B' B' D' F R L B B' B' F R' B R' R B' D B' L U' F L' L' D F' F D R B' B' U' R U' D' R L' U B' L' L' D F' D R R F' R' R L' R' U R' R' D' D U' R' R B' L' U U D R' B' R B U B R' D B' F' B U D' R' R D' D F R D' B B' U' R L B U' R' U' L' F' R' D' U' F U'" # 38 # long solve time and long solution
    move_sequence = "F F' D F F' F' B' R' U' B L B' F' D' L' L D' R' L L' D' D L B' D' F R U F L B U' L' R L' F U F' F' U D' L' D D L' L U' L F' R' R' B D F F U L L B F' L B U B B' U' F' F' R' F L' R' U B D U' F' B L U U' F' L L U' F F R U F R' U' U' D' F' D' R' U' D' B'" # 39
    move_sequence = "R' R' B R F L' L' D' F F U U B' U U' F D' B' B U L L R' D' B' F' F F D' R D' D' B F' F B' L' U' U' B' U' L L' U' L L' B' D R' F' L F F U' L' F' D' L' L U' L' U' B F U' B' F' B F' L' D R R' R' R' B D D' R' L' U L' D' R' D' B' B B L' R B R' L D' D B D' F R' D" # 40
    # move_sequence =  # 41
    # move_sequence =  # 42
    # move_sequence =  # 43
    # move_sequence =  # 44
    # move_sequence =  # 45
    # move_sequence =  # 46
    # move_sequence =  # 47
    # move_sequence =  # 48
    # move_sequence =  # 49
    # move_sequence =  # 50

    enter_move_sequence(
        move_sequence,
        start_delay=3,
        move_delay=.025)
    
if __name__ == "__main__":
    main()