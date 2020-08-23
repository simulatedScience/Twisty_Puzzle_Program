"""

"""
import vpython as vpy


def genCubes():
    """
    generate 8 cubes around (0,0,0) each cube has sidelength 0.5
    """
    offset = vpy.vector(.5, .5, .5)
    size = vpy.vector(.2,.2,.2)
    vpy.box(pos = vpy.vector(0,0,0)-offset, color = vpy.vector(0.3,0.5,1), size = size)
    vpy.box(pos = vpy.vector(0,0,1)-offset, color = vpy.vector(0.3,0.5,1), size = size)
    vpy.box(pos = vpy.vector(0,1,0)-offset, color = vpy.vector(0.3,0.5,1), size = size)
    vpy.box(pos = vpy.vector(0,1,1)-offset, color = vpy.vector(0.3,0.5,1), size = size)

    vpy.box(pos = vpy.vector(1,0,0)-offset, color = vpy.vector(0.3,0.5,1), size = size)
    vpy.box(pos = vpy.vector(1,0,1)-offset, color = vpy.vector(0.3,0.5,1), size = size)
    vpy.box(pos = vpy.vector(1,1,0)-offset, color = vpy.vector(0.3,0.5,1), size = size)
    vpy.box(pos = vpy.vector(1,1,1)-offset, color = vpy.vector(0.3,0.5,1), size = size)


def onClick(canvas, event, selectedObjects):
    """
    add arrow between last two clicked objects
    append clicked object to given list 'selectedObjects'
    if cycle of arrows is closed: clear list 'selectedObjects'

    inputs:
        a canvas,
        a mousedown event
        a list
    returns:
        None
    outputs:
        changes given list 'selectedObjects' in-place
    """
    selectedObject = canvas.mouse.pick
    if selectedObject != None:
        if len(selectedObjects)>0:
            cycle_closed = selectedObject == selectedObjects[0]
        else:
            cycle_closed = False
        selectedObject.color = selectedObject.color + vpy.vector(.2,.2,.2)
        if not selectedObject in selectedObjects or cycle_closed:
    
            selectedObjects.append(selectedObject)

            if len(selectedObjects)>1:
                axis = selectedObjects[-1].pos-selectedObjects[-2].pos
                arrow_len = axis.mag
                vpy.arrow(pos=selectedObjects[-2].pos, axis=axis, length=arrow_len, shaftwidth = 0.05*arrow_len, color=vpy.vector(.8,0,0))

        if cycle_closed:
            for obj in selectedObjects:
                obj.color = obj.color - vpy.vector(.1,.1,.1)
            selectedObjects.clear()

        selectedObject.color = selectedObject.color - vpy.vector(.1,.1,.1)




if __name__=="__main__":
    canvas = vpy.canvas(background = vpy.vector(0.8,0.8,0.8))
    canvas.lights = []
    vpy.distant_light(direction = vpy.vector(-1, 0.8, 1.5), color = vpy.vector(0.7,0.7,0.7))
    genCubes()
    selectedObjects = []
    canvas.bind("mousedown", lambda event: onClick(canvas, event, selectedObjects))