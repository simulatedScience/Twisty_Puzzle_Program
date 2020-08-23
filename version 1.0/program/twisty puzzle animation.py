"""
this program should be able to store different twisty puzzles as well as algorithms for them.
it should offer an interface to create new puzzles and save algorithms for them.

the gui will be written in tkinter running on a separate thread/process 
to be able to control the vpython animation in real time.
"""

import vpython as vpy

class twistyPuzzle():
    def __init__(self):
        self.colors = {"red":       vpy.vector(1  ,0.1,0  ),
                       "orange":    vpy.vector(1  ,0.5,0  ),
                       "yellow":    vpy.vector(1  ,1  ,0  ),
                       "green":     vpy.vector(0.5,1  ,0.3),
                       "darkGreen": vpy.vector(0.1,0.6,0.1),
                       "blue":      vpy.vector(0.3,0.5,1  ),
                       "lightBlue": vpy.vector(0.6,0.8,1  ),
                       "lightPink": vpy.vector(0.7,0.4,1  ),
                       "pink":      vpy.vector(0.6,0.1,1  ),
                       "purple":    vpy.vector(0.4,0.1,1  ),
                       "black":     vpy.vector(0.1,0.1,0.1),
                       "darkGrey":  vpy.vector(0.4,0.4,0.4),
                       "lightGrey": vpy.vector(0.7,0.7,0.7),
                       "white":     vpy.vector(1  ,1  ,1  ),
                       "beige":     vpy.vector(1  ,0.9,0.7)}

        self.light = self.colors["lightGrey"] #light color
        self.canvas = vpy.canvas(background=self.colors["lightGrey"])

        self.genMenu()

    def buttonPressed(self):
        print("gedrückt")


    def genRubiksCube(self):
        self.boxList = []

if __name__=="__main__":
    T = twistyPuzzle()