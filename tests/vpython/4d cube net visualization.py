import vpython as vpy

canvas = vpy.canvas(background = vpy.vector(1,1,1)) #white background

tensor = [
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [1, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 1, 1],
                [0, 1, 1, 0],
                [1, 1, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [1, 0, 0, 0],
                [0, 0, 0, 0],
            ],
        ]

boxColor = vpy.vector(1,0.5,0)
boxes = []
for z, plane in enumerate(tensor):
    for y, line in enumerate(plane):
        for x, value in enumerate(line):
            if value==1:
                boxes.append(vpy.box(pos=vpy.vec(x-1.5,y-1.5,z-1.5), color=boxColor))