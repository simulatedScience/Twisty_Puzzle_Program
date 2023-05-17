import vpython as vpy

def create_canvas():
    """
    create a vpython canvas with two light sources
    """
    canvas = vpy.canvas(background=vpy.vector(0.8,0.8,0.8),
                        up=vpy.vector(0,0,1),
                        forward=vpy.vector(-1,0,0),
                        width=1280,
                        height=720)
    canvas.lights = []
    canvas.ambient = vpy.vec(1, 1, 1) * 0.7
    # Front light
    vpy.distant_light(direction = vpy.vector(1, 1, 1), color = vpy.vector(0.4, 0.4, 0.4))
    # Back light
    vpy.distant_light(direction = vpy.vector(-1, -1, -1), color = vpy.vector(0.4, 0.4, 0.4))
    return canvas


def next_color(canvas, availiable_colors):
    """
    change the color of the clicked object

    inputs:
    -------
        canvas - (vpython.canvas) - the canvas displaying the puzzle
        availiable_colors - (list) - a list of all colors in the puzzle

    returns:
    --------
        None
    """
    selected_object = canvas.mouse.pick
    if not selected_object == None:
        for i, color in enumerate(availiable_colors):
            if selected_object.color == color:
                try:
                    selected_object.color = availiable_colors[i+1]
                except IndexError:
                    selected_object.color = availiable_colors[0]
                break


def bind_next_color(canvas, availiable_colors):
    def temp_func(*_):
        next_color(canvas, availiable_colors)
    canvas.bind("mousedown", temp_func)
    return temp_func