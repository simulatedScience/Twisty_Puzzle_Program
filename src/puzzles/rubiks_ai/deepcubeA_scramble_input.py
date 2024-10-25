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
    modifier = "shift" if "'" in move else None
    move = move.replace("'", "")
    move = move.lower()
    return move, modifier

def main():
    # move_sequence: str = "B D U F F L' F' D R D' L B' D B' D R' D' L R' L' L' D U R' D F' U' R L F'" # 1
    # move_sequence: str = "D F L' R F' F' L D' D' L' L' B D U' R' B D' D' B' B' R R D U' F U' B U' F D" # 2
    move_sequence: str = "F' U' U' B' R' F D L R' D F B U' R' F' U D U D B' L U' B' U L B U B U D'" # 3
    move_sequence: str = "F F B' L R F' B L F L' L' F' U B' L U D B' B' F' R F B' U D' U' U' D L U'" # 4
    # move_sequence = "F F' U U' R R' D D' L L' B B'"
    
    enter_move_sequence(
        move_sequence,
        start_delay=5,
        move_delay=.2)
    
if __name__ == "__main__":
    main()