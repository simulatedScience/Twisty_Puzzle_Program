# Twisty Puzzle Analysis version 1.0
by ***Sebastian Jost***

around _February to April 2020_

## What can it do?
This version does not have any animation or visualisation support.

However much of the basic reasearch, which libraries to use, how to digitalize twisty puzzles and so on was done during this stage of the project.

Instead it focusses on the user interface:
 - saving puzzles and getting an overview of all the saved ones.
 - select and save a preview image for the puzzle
 - write, save and read a solving algorithm description for each puzzle
 - define moves for the puzzle as index inputs
 - write and save algorithm descriptions for each puzzle

## How does it do that?
The gui is entirely implemented with tkinter.

### Tkinter drawbacks
Sadly tkinter is quite old and does not support modern design for all it's widgets. Additionnally some widgets are an absolute nightmare to style as the height and width are sometimes only adjustable in text character units, not in pixels.

Availiability of dynamic UI elements like hover information or hover events is also very limited.

### Other issues
All save files are .txt files with very specific custom structure to seperate different data in them. This is obviously prone to errors and not very reusable.

The code is pretty much all in one file, which of course reads absolutely horrible.

The layout of the user interface was a nice first attempt but it is quite noticable that it was planned without much knowledge about the exact implementation of the project. It also got edited and expanded later on which didn't improve much.

## Conclusion
Due to the issues mentioned above, this version will not be continued.