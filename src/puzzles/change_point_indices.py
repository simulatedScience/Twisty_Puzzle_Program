"""
go through a given file line by line. In each line, find all numbers k greater than a threshold n and replace them with k-3.
save all lines to a new file.
"""

def replace_numbers(input_file: str, output_file: str, n: int) -> None:
    with open(input_file, 'r') as f:
        lines = f.readlines()
    with open(output_file, 'w') as f:
        for line in lines:
            number_str: str = ""
            new_line: str = ""
            for char in line:
                if char in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
                    number_str += char
                elif number_str != "":
                    number = int(number_str)
                    new_line += str(number - 3) if number > n else number_str
                    new_line += char
                    number_str = ""
                else: # add char to new_line as is
                    new_line += char
            f.write(new_line)
            
input_file = "src/puzzles/geared_5x5_2/to_change.xml"
output_file = "src/puzzles/geared_5x5_2/changed.xml"
replace_numbers(input_file, output_file, 85)