import vpython as vpy

def init_spheres(n=6):
    spheres = []
    colors = []
    for i in range(n):
        pos = vpy.vec(i%3-1, i//3,0)
        color = vpy.vec( i%3/2, (i+1)%3/2, (i+2)%3/2 )
        spheres.append(vpy.sphere(radius=0.3, color=color, pos=pos))
        colors.append(color)
    return spheres, colors


def test_func(event):
    print(event)
    try: print(event.key())
    except: pass
    try: print(event.pos())
    except: pass
    # try: print(event.)
    # except: pass


if __name__=="__main__":
    canvas = vpy.canvas(background=vpy.vec(.8,.8,.8))
    spheres, colors = init_spheres(6)
    canvas.bind("button-3", test_func)