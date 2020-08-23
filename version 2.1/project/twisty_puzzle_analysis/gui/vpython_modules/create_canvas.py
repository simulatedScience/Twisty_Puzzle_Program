import vpython as vpy

def create_canvas():
    """
    create a vpython canvas with a few light sources
    """
    canvas = vpy.canvas(background = vpy.vector(0.8,0.8,0.8),
                        up = vpy.vector(0,0,1),
                        forward = vpy.vector(-1,0,0))
    canvas.lights = []
    canvas.ambient = vpy.vec(1,1,1)*0.3
    vpy.distant_light(direction = vpy.vector( 1, 1, 1), color = vpy.vector(0.7,0.7,0.7))
    vpy.distant_light(direction = vpy.vector(-1,-1,-1), color = vpy.vector(0.7,0.7,0.7))

    return canvas