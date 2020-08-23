import vpython as vpy

def genSpheres():
    vpy.sphere(pos = vpy.vector(0,0,0), color = vpy.vector(0.3,0.5,1), radius = 0.25)
    vpy.sphere(pos = vpy.vector(0,0,1), color = vpy.vector(0.3,0.5,1), radius = 0.25)
    vpy.sphere(pos = vpy.vector(0,1,0), color = vpy.vector(0.3,0.5,1), radius = 0.25)
    vpy.sphere(pos = vpy.vector(0,1,1), color = vpy.vector(0.3,0.5,1), radius = 0.25)
    # vpy.sphere(pos = vpy.vector(1,0,0), color = vpy.vector(0.3,0.5,1), radius = 0.25)
    # vpy.sphere(pos = vpy.vector(1,0,1), color = vpy.vector(0.3,0.5,1), radius = 0.25)
    # vpy.sphere(pos = vpy.vector(1,1,0), color = vpy.vector(0.3,0.5,1), radius = 0.25)
    # vpy.sphere(pos = vpy.vector(1,1,1), color = vpy.vector(0.3,0.5,1), radius = 0.25)

def genCubes():
    # vpy.box(pos = vpy.vector(0,0,0), color = vpy.vector(0.3,0.5,1), size = vpy.vector(.5,.5,.5))
    # vpy.box(pos = vpy.vector(0,0,1), color = vpy.vector(0.3,0.5,1), size = vpy.vector(.5,.5,.5))
    # vpy.box(pos = vpy.vector(0,1,0), color = vpy.vector(0.3,0.5,1), size = vpy.vector(.5,.5,.5))
    # vpy.box(pos = vpy.vector(0,1,1), color = vpy.vector(0.3,0.5,1), size = vpy.vector(.5,.5,.5))
    vpy.box(pos = vpy.vector(1,0,0), color = vpy.vector(0.3,0.5,1), size = vpy.vector(.5,.5,.5))
    vpy.box(pos = vpy.vector(1,0,1), color = vpy.vector(0.3,0.5,1), size = vpy.vector(.5,.5,.5))
    vpy.box(pos = vpy.vector(1,1,0), color = vpy.vector(0.3,0.5,1), size = vpy.vector(.5,.5,.5))
    vpy.box(pos = vpy.vector(1,1,1), color = vpy.vector(0.3,0.5,1), size = vpy.vector(.5,.5,.5))

def onHover(canvas, event):
    selectedObject = canvas.mouse.pick
    print(event.event, type(event.event))
    if selectedObject != None:
        print(selectedObject, type(selectedObject))
        selectedObject.color = selectedObject.color + vpy.vector(0.1,0.1,0.1)

if __name__=="__main__":
    canvas = vpy.canvas(background = vpy.vector(0.8,0.8,0.8))
    canvas.lights = []
    # vpy.distant_light(direction = vpy.vector( 1, .5, .2), color = vpy.vector(0.7,0.7,0.7))
    # vpy.distant_light(direction = vpy.vector( 1, 0, 0), color = vpy.vector(0.7,0.7,0.7))
    vpy.distant_light(direction = vpy.vector(-1, 0, 0), color = vpy.vector(0.7,0.7,0.7))
    # vpy.distant_light(direction = vpy.vector( 0, 1, 0), color = vpy.vector(0.7,0.7,0.7))
    # vpy.distant_light(direction = vpy.vector( 0,-1, 0), color = vpy.vector(0.7,0.7,0.7))
    # vpy.distant_light(direction = vpy.vector( 0, 0, 1), color = vpy.vector(0.7,0.7,0.7))
    # vpy.distant_light(direction = vpy.vector( 0, 0,-1), color = vpy.vector(0.7,0.7,0.7))
    genSpheres()
    genCubes()
    canvas.bind("mousedown", lambda event: onHover(canvas, event))