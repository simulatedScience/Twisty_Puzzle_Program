import vpython as vpy
import time


canvas = vpy.canvas(background = vpy.vector(1,1,1)) #white background

canvas.lights=[]

# vpy.distant_light( direction=vpy.vector(-1,-1,-1), color=vpy.vector(1,0.8,0.5) )
vpy.distant_light( direction=vpy.vector(-1,0,0), color=vpy.vector(1,0.8,0.5) )

boxColor = vpy.vector(1,0.5,0)
boxHighlightColor = vpy.vector(1,0.8,0.5)

box = vpy.box(pos=vpy.vector(0,0,0),
              color=boxColor, 
              opacity=0.5,
              shininess=0)
sphere1 = vpy.sphere( pos=vpy.vector(0,1.5,0), color=vpy.vector(1,1,1), radius=0.8 )
sphere2 = vpy.sphere( pos=vpy.vector(0,-1.5,0), 
        color=vpy.vector(0.3,0.5,1), 
        radius=0.5, 
        make_trail=True, 
        retain=20 , 
        trail_color=vpy.vector(0.5,1,0.3), 
        trail_radius=0.05)

sphere1.direction = vpy.vector(-1,1,0)
vpy.attach_arrow(sphere1, "direction", scale=1.5, shaftwidth=0.1)

connector = vpy.cylinder(pos = sphere1.pos, axis=sphere2.pos-sphere1.pos, radius=0.1, color=vpy.vec(.8,.2,.6))

# vpy.local_light( position=vpy.vector(0,0,0), color=vpy.vector(1,0.8,0.5) )


while True:
    # box.rotate( angle=0.1, axis=vpy.vector(1,1,1) )
    sphere1.rotate( angle=0.02, axis = vpy.vector(1,0,0), origin=vpy.vector(0,0,0) )
    sphere2.rotate( angle=0.02, axis = vpy.vector(1,0,0), origin=vpy.vector(0,0,0) )
    connector.pos = sphere1.pos
    connector.axis = sphere2.pos - sphere1.pos
    time.sleep(0.005)
    
    # if canvas.mouse.pick == box:
    #     box.color = boxHighlightColor
    # elif box.color == boxHighlightColor:
    #     box.color = boxColor
    # vpy.rate=(30)