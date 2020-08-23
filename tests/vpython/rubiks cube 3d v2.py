import vpython as vpy
import time
import numpy as np

class rubiksCube():
    def __init__(self):
        self.black = vpy.vector(0.2,0.2,0.2)
        self.light = vpy.vector(0.7,0.7,0.7)

        self.red = vpy.vector(1,0.1,0)
        self.orange = vpy.vector(1,0.5,0)
        self.green = vpy.vector(0.5,1,0.3)
        self.blue = vpy.vector(0.3,0.5,1)
        self.white = vpy.vector(1,1,1)
        self.yellow = vpy.vector(1,1,0)

        self.faceColors = [self.green, self.blue, self.yellow, self.white, self.red, self.orange]
        self.zero = vpy.vector(0,0,0)

        self.canvas = vpy.canvas(background=vpy.vector(0.8,0.8,0.8))
        self.canvas.lights = []

        vpy.distant_light(direction=vpy.vector( 1, 0, 0), color=self.light)
        vpy.distant_light(direction=vpy.vector(-1, 0, 0), color=self.light)
        vpy.distant_light(direction=vpy.vector( 0, 1, 0), color=self.light)
        vpy.distant_light(direction=vpy.vector( 0,-1, 0), color=self.light)
        vpy.distant_light(direction=vpy.vector( 0, 0, 1), color=self.light)
        vpy.distant_light(direction=vpy.vector( 0, 0,-1), color=self.light)

        # self.faceIndexDict = {"t":3, "g":2, "f":1, "b":0, "r":5, "l":4}
        self.faceIndexDict = dict()
        
        self.currentCycleList = []
        self.currentMoveList = []
        self.moves = []

        self.genCube()

        self.canvas.bind("mousedown", self.defineMove)


    def genCube(self):
        """
        generates the cube out of 26 black cube-shaped boxes and 9 colored, flat cuboid boxes per face
        """
        self.boxList = [ [ ['' for _ in range(3)] for _ in range(3) ] for _ in range(3) ]
        # generate black cube base
        for xi in range(-1,2,1):
            for yi in range(-1,2,1):
                for zi in range(-1,2,1):
                    if not (xi==0 and yi==0 and zi==0):
                        box = vpy.box(pos=vpy.vector(xi,yi,zi), color=self.black)#, opacity=0.5)
                        # box = vpy.box(pos=vpy.vector(xi,yi,zi), color=self.faceColors[(xi+yi+zi)%6], opacity=0.5)
                        self.boxList[xi+1][yi+1][zi+1] = box
        # generate colored faces
        # -> one coordinate 1.5, the others looping through (-1,0,1)x(-1,0,1)
        self.faceBoxList = [[] for _ in range(6)]
        for faceIndex in range(6):
            x = (faceIndex-2)%6//2%2 * (faceIndex%2*2-1) * 1.07
            y = (faceIndex  )%6//2%2 * (faceIndex%2*2-1) * 1.07
            z = (faceIndex+2)%6//2%2 * (faceIndex%2*2-1) * 1.07
            for faceX in range(-1,2,1):
                for faceZ in range(-1,2,1):
                    y0 = y
                    if x == 0:
                        x0 = faceX
                    elif y == 0:
                        y0 = faceX
                        x0 = x
                    if z == 0:
                        z0 = faceZ
                    elif y == 0:
                        y0 = faceZ
                        z0 = z
                    
                    box = vpy.box( pos=vpy.vector(x0,y0,z0), color=self.faceColors[faceIndex], size=vpy.vector(.9,.9,.9) )
                    # c = (3*(faceX+1) + faceZ + 1)/9
                    # box = vpy.box( pos=vpy.vector(x0,y0,z0), color=vpy.vector(c,c,c), size=vpy.vector(.9,.9,.9) )
                    self.faceBoxList[faceIndex].append(box)



    def getLayer(self,layer):
        """
        returns all boxes of a given layer (t,g,r,l,f,b) (black boxes and colored ones)
        t = top layer
        g = bottom layer (ground)
        r = right layer
        l = left layer
        f = front layer
        b = back layer
        """
        faceIndex = self.faceIndexDict[layer]
        
        # boxList = []
        boxList = self.faceBoxList[ faceIndex ][:]

        x = 2 - (faceIndex-2)%6//2%2 * ((faceIndex+1)%2*2)
        y = 2 - (faceIndex  )%6//2%2 * ((faceIndex+1)%2*2)
        z = 2 - (faceIndex+2)%6//2%2 * ((faceIndex+1)%2*2)
        axis = vpy.vector(
                (faceIndex-2)%6//2%2,
                (faceIndex  )%6//2%2,
                (faceIndex+2)%6//2%2)
        for faceX in range(0,3):
            for faceZ in range(0,3):
                if (faceIndex-2)%6//2%2 == 1: #x
                    y = faceX
                    z = faceZ
                elif (faceIndex  )%6//2%2 == 1: #y
                    x = faceX
                    z = faceZ
                else:
                    x = faceX
                    y = faceZ
                # print(x,y,z, self.boxList[x][y][z])
                boxList.append(self.boxList[x][y][z])
        return boxList, axis


    # def rotate(self,layer,n=45):
    #     toplayer, axis = self.getLayer(layer)
    #     time.sleep(0.1)
    #     # print(axis)
    #     # vpy.arrow(canvas = self.canvas, axis=axis, pos=vpy.vector(5,0,0))
    #     # vpy.arrow(canvas = self.canvas, axis=axis, pos=vpy.vector(0,5,0))
    #     # vpy.arrow(canvas = self.canvas, axis=axis, pos=vpy.vector(0,0,5))
    #     for i in range(n):
    #         for box in toplayer:
    #             box.rotate(angle=vpy.radians(90/n), axis=axis, origin = R.zero)
    #         time.sleep(0.02)


    def defineMove(self):
        """
        adds the clicked object to the current cycle.
        if the object is already in the cycle it closes the cycle and starts a new one.
        """
        selectedObject = self.canvas.mouse.pick
        if selectedObject != None:
            selectedObject.color = selectedObject.color + vpy.vec(.1,.1,.1)
            if not selectedObject in self.currentCycleList:
                self.currentCycleList.append(selectedObject)
                print("saved object\n", selectedObject)
            elif selectedObject == self.currentCycleList[0]:
                self.currentMoveList.append( self.currentCycleList )
                print("saved cycle\n", self.currentCycleList)
                self.currentCycleList = []
            time.sleep(0.1)
            selectedObject.color = selectedObject.color - vpy.vec(.1,.1,.1)


    def saveMove(self):
        """
        saves all current cycles as a move
        requests user input for the move name
        """
        print(self.currentMoveList)
        self.moves.append(self.currentMoveList)
        moveName = input("move name (must be one character): ")
        self.faceIndexDict[ moveName ] = len(self.moves)-1
        self.currentMoveList = []


    def rotate(self, layer, n = 45):
        # print(layer)
        layerIndex = self.faceIndexDict[layer]
        move = self.moves[layerIndex]
        for cycle in move:
            # print("cycle:",cycle)
            objectPositions = [vObject.pos for vObject in cycle]
            print("positions:",objectPositions)
            center = vpy.vector(0,0,0)
            for pos in objectPositions:
                center += pos
            center = center/len(objectPositions)
            # center = sum(objectPositions)/len(objectPositions)
            print("center of mass",center)
            for object1, object2 in zip( cycle, cycle[1:]+[cycle[0]] ):
                print(object1, object2)
                object1pos = object1.pos-center
                object2pos = object2.pos-center

                coefficientMatrix = [[object1pos.x, object1pos.y],
                                     [object2pos.x, object2pos.y]]
                solutionVector = [-object1pos.z, -object2pos.z]     # z = 1

                x,y = np.linalg.solve(coefficientMatrix, solutionVector)
                print(f"axis: ({x},{y},1)")
                # y = ( (object1pos.z - object1pos.x) / (object2pos.y * object2pos.z) ) / ((object1pos.y - object1pos.x) / object2pos.y * object2pos.y )
                # x = (object1pos.z - object1pos.y * y) / object1pos.x
                # z = -1
                axis = vpy.vector( x,y,1 )
                
                for _ in range(n):
                    object1.rotate(angle=vpy.radians(90/n), axis = axis, origin = center)
                    time.sleep(0.02)


if __name__=="__main__":
    n = 45
    R = rubiksCube()

    # time.sleep(8)
    while True:
        event = R.canvas.waitfor("keyup")
        # try:
        if type(event) != bool and event.event != "mousedown":# and type(event) != vpy.event_return:
            # print(event, type(event), event.event)
            if event.key in R.faceIndexDict.keys():
                R.rotate(event.key, n = n)
            if event.key == "m":
                print("save")
                R.saveMove()
        # except AttributeError:
        #     pass
    
