# using VPython (visual) and Tkinter together
# with the help of Python module thread
# tested with VPython 5.4.1 and Python 2.7.1 by vegaseat
import vpython as vpy
import tkinter as tk
import threading

class myThread (threading.Thread):
    def __init__(self, threadID, function, name="thread 1", counter="1"):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.function = function
        self.name = name
        self.counter = counter
    def run(self):
        print ("Starting " + self.name)
        # print_time(self.name, 5, self.counter)
        self.function()
        print ("Exiting " + self.name)

# will be global
sphere = None
def vthread():
    global sphere
    vpy.scene.title = "Sphere in space (3D drag with right mouse button)"
    vpy.scene.autoscale = False
    sphere = vpy.sphere(pos=vpy.vector(0, 0, 0), color=vpy.color.green)

def move_sphere_incr_x(event=None):
    """moves along the x axis incrementing x"""
    x, y, z = sphere.pos
    sphere.pos = (x+1, y, z)

def move_sphere_decr_x(event=None):
    """moves along the x axis decrementing x"""
    x, y, z = sphere.pos
    sphere.pos = (x-1, y, z)
root = tk.Tk()
w = 300
h = 200
x = 450
y = 100
# use width x height + x_offset + y_offset (no spaces!)
root.geometry("%dx%d+%d+%d" % (w, h, x, y))
root.title("Control Sphere from here")
b_incr_x = tk.Button(root, text="move on x axis increment x")
# bind passes an event to function
b_incr_x.bind("<Button-1>", move_sphere_incr_x)
b_incr_x.grid(row=0, column=0, padx=20, pady=10)
b_decr_x = tk.Button(root, text="move on x axis decrement x")
# bind passes an event to function
b_decr_x.bind("<Button-1>", move_sphere_decr_x)
b_decr_x.grid(row=1, column=0, padx=10)
# use thread to do run VPython and Tkinter simultaneously
# thread.start_new_thread(function, args)
# args is an empty tuple here
# sphere = thread.start_new_thread(vthread, ())
thread1 = myThread(1, vthread)
thread1.run()
root.mainloop()