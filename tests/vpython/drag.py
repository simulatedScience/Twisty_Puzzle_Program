from vpython import *

scene = canvas(background=color.white)

scene.range = 5
box()

drag = False
s = None # declare s to be used below

def down():
    global drag, s
    s = sphere(pos=scene.mouse.pos,
        color=color.red,
        size=0.2*vec(1,1,1))
    drag = True

def move():
    global drag, s
    if drag: # mouse button is down
        s.pos = scene.mouse.pos

def up():
    global drag, s
    s.color = color.cyan
    drag = False

scene.bind("mousedown", down)

scene.bind("mousemove", move)

scene.bind("mouseup", up)

# It is also possible to use "anonymous" (unnamed) functions, an extended feature of the RapydScript Python-to-JavaScript compiler, as shown here:

# scene.range = 5
# box()

# drag = False
# s = None # declare s to be used below

# scene.bind("mousedown", def ():
#     nonlocal drag, s
#     s = sphere(pos=scene.mouse.pos,
#                color=color.red,
#                size=0.2*vec(1,1,1))
#     drag = True
# )

# scene.bind("mousemove", def ():
#     nonlocal drag, s
#     if drag: # mouse button is down
#         s.pos = scene.mouse.pos
# )

# scene.bind("mouseup", def ():
#     nonlocal drag, s
#     s.color = color.cyan
#     drag = False
# )