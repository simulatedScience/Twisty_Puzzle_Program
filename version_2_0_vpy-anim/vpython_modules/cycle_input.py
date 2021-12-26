"""
a module providing methods for visually defining cycles and moves
"""
import vpython as vpy

def on_click(canvas, selected_objects, cycle_list, object_list, arrow_list):
    """
    add arrow between last two clicked objects
    append clicked object to given list 'selectedObjects'
    if cycle of arrows is closed: clear list 'selectedObjects'

    inputs:
    -------
        canvas - (vpython canvas) - the clicked vpython canvas object
        selected_objects - (list) - list of objects currently in the cycle
            this list will be changed in-place
        cycle_list - (list) - a list where finished cycles will be saved
            this list will be changed in-place
        object_list - (list) - list of objects that can be added to a cycle
        arrow_list - (list) - list of vpython arrow objects
            this list will be changed in-place

    returns:
    --------
        None

    outputs:
    --------
        changes given list 'selected_objects' in-place
        changes given list 'cycle_list' in-place
        changes given list 'arrow_list' in-place
    """
    selected_object = canvas.mouse.pick
    if selected_object != None and selected_object in object_list:
        add_arrow = True
        cycle_closed = False
        # if there is at least one object selected already:
        if len(selected_objects)>0:
            # check whether or not the cycle is closed
            cycle_closed = selected_object == selected_objects[0]

            # delete last point and arrow if it was clicked twice
            if selected_object == selected_objects[-1]:
                #reset object color
                selected_object.color = selected_object.color - vpy.vector(.1,.1,.1)
                #delete last object
                del(selected_objects[-1])
                #delete last arrow if existent
                if len(arrow_list) > 0:
                    arrow_list[-1].visible = False
                    del(arrow_list[-1])
                add_arrow = False

        if add_arrow and ((not selected_object in selected_objects) or cycle_closed):
            selected_object.color = selected_object.color + vpy.vector(.2,.2,.2)

            selected_objects.append(selected_object)

            if len(selected_objects)>1:
                axis = selected_objects[-1].pos-selected_objects[-2].pos
                arrow_len = axis.mag
                arrow_list.append(vpy.arrow(pos=selected_objects[-2].pos,
                                            axis=axis,
                                            length=arrow_len*0.9,
                                            shaftwidth = 0.02*arrow_len,
                                            color=vpy.vector(.8,0,0),
                                            opacity=0.8))
            #reset object color
            selected_object.color = selected_object.color - vpy.vector(.1,.1,.1)


        if add_arrow and cycle_closed:
            if len(selected_objects) > 2: #cycle contains at least two different points
                cycle_list.append(make_cycle(selected_objects, object_list))
            for arrow in arrow_list:
                arrow.opacity = 0.1
            for obj in selected_objects:
                obj.color = obj.color - vpy.vector(.1,.1,.1)
            selected_objects.clear()



def bind_click(canvas, cycle_list, object_list, arrow_list):
    """
    bind the mousedown event on the given canvas to the onClick function
    """
    selected_objects = []
    def bound_method(event):
        on_click(canvas, selected_objects, cycle_list, object_list, arrow_list)
    canvas.bind("mousedown", bound_method)
    return bound_method


def make_cycle(selected_objects, object_list):
    """
    creates a cycle given by 'selected_objects' as a list of integers

    inputs:
    -------
        selected_objects - (list) - a list of vpython objects
        object_list - (list) - list containing every element of selected_objects
            the cycle will hold the indeces of the selected_objects in object_list
    
    returns:
    --------
        (list) of ints - permutation on object_list in cycle notation
    """
    cycle = []
    for obj in selected_objects[:-1]:
        cycle.append(object_to_index(obj, object_list))
    return cycle


def object_to_index(obj, object_list):
    """
    returns the index of the given object 'obj' in object_list

    inputs:
    -------
        obj - (vpython object) - any vpython object i.e. a vpy.sphere or vpy.box
        object_list - (list) of vpython objects - list containing obj
    
    returns:
    --------
        (int) - index of 'obj' in 'object_list'

    errors:
    -------
        raises a ValueError if obj is not in object_list
    """
    for i, test_obj in enumerate(object_list):
        if test_obj == obj:
            return i
    raise ValueError(f"'object' {obj} not in 'object_list'")


if __name__=="__main__":
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


    canvas = vpy.canvas(background = vpy.vector(0.8,0.8,0.8))
    canvas.lights = []
    vpy.distant_light(direction = vpy.vector(-1, 0.8, 1.5), color = vpy.vector(0.7,0.7,0.7))
    genCubes()