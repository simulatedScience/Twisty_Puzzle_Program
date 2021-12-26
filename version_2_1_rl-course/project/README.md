# Overview
This program offers an interface to greate digital twisty puzzles by importing GeoGebra (.ggb) files.

# Requirements
required python modules:

### non-standard modules:
- vpython       - *for 3d vizualisation*
- colored       - *for colored print commands in the user interaction*
- lxml - *for saving the puzzles to .xml files*

### standard library modules:
- os - *to manage files*
- xml.etree.ElementTree
- shutil - *to copy and rename files*
- zipfile - *to read .ggb files (they are renamed .zip files)*
- copy - *to make deepcopies of lists*
- time - *to manage animation speed*