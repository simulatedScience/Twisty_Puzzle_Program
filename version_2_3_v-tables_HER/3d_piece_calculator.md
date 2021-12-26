# calculating 3D puzzle pieces

Up until now all twisty puzzles were only represented via a few points in 3D space. But there is a way to give volume to those puzzles, make them proper 3D shapes like they are in real life. THis Document explain how this is done in a few steps:

#### 1. calculate a 3D voronoi diagram around the puzzle points
#### 2. snap the voronoi diagram to a given shape (_cube, sphere, other platonic solids, ..._)
#### 3. create polyhedra for each cell in the voronoi diagram
#### 4. color those polyhedra the same as the puzzle point in that cell
_____
## 1. calculate a 3D voronoi diagram around the puzzle points
The standard library python module `scipy.spatial` provides a class `Voronoi` (from now on `vor`), which can calculate voronoi diagrams for any number of dimensions. The calculated values are stored in a few variables:
- `vor.points` are the input points as a numpy `ndarray`
- `vor.vertices` are the intersection points where the boundries of three or more voronoi cells meet.
- `vor.ridge_vertices` is a list of lists of indices of `vor.vertices`. Each sub-list contains the indices of the vertices that form a cell boundry. 

    In 2D the ridges are lines and therefor each sublist contains exactly two vertex indices: start and end of these lines.

    In 3D the ridges are faces or more precisely: polygons. Therefor each sublist contains the vertex indices for each corner of the polygon.
- `vor.regions` is another list of lists of indices of `vor.vertices`. But this time each sublist represents one voronoi cell, not just one ridge as in `vor.ridge_vertices`. The goal is to find all faces that belong to each region and create the voronoi cell from those faces as one 3D polyhedron.

- There are also the attributes `vor.ridge_points`, `vor.point_region` and `vor.furthest_site` but they are not relevant for this application.

-----

## 2. snap the voronoi diagram to a given shape
### **Approximation:**
However we can achive an approximation of cube snapping by doing the following:

1. add a few points very far away in all cardinal directions. (i.e. (-100, 0), (100, 0), (0, -100), (0, 100))
2. calculate the voronoi diagram including those points but ignore cells on the outside (list indices include `-1`).

### Why does this work?
if the added points are sufficiently far away the resulting point setup can be approximated as one point in the center and the additional points around that. This setup results in a square (2D), cube(3D), hypercube(4D) and so on.

### Disadvantages
This is only an approximation though and comes with a few disadvantages:
- the shape is not really a cube, only close to a cube
- the size of the shape is difficult to control unless all resulting points are projected back onto a smaller shape. due to the large distance between the added outside points a large voronoi diagram cannot be avoided otherwise.
- some features of the puzzle can get lost. This is the same effect as in real life puzzle where cutting down pieces of a puzzle can reveal previously hidden pieces. This is especially noticable with some pieces being unproportionally small. (i.e. the skewb center pieces are tiny compared to the corners when using this method.)

### **Actual solution:**
We only need a fnite size of the voronoi diagram to represent the puzzles. To do that and still capture the different possible shapes of puzzles we will clip the voronoi diagram to a polyhedron.

This should be an arbitrary convex polyhedron, bigger or smaller than the finite cells of the voronoi diagram.

Similar to the approximation described above I first add six far points to the actual points. That way the final pieces of the puzzle are all already closed voronoi cells, so we don't have to deal with the faces extending to infinity.

Then we can clip each voronoi cell (convex polyhedra) to the outer shape, from now on called the clip polyhedron (`clip_poly`). We want to calculate the intersection of each voronoi cell and the clip polyhedron.

To do that, I implemented a 3D variant of the [Sutherland-Hodgman-Algorithm](https://en.wikipedia.org/wiki/Sutherland%E2%80%93Hodgman_algorithm) vor polygon clipping. Looping over each face (`clip_plane`) of the clip polyhedron I calculate for each point in the voronoi cell whether or not it is above or below the clip plane. Then we get three possible cases:

1. If all points are above (outside) the clip plane, the intersection is empty and we are done.
2. If all points are below or on the clip plane, this clip plane doesn't change the intersection and we can continue with the nect clip face.
3. Otherwise there are edges which intersect the clip plane.

In the third case I loop over all faces of the voronoi cell. Any point of a face which is above (outside) of the clip plane gets deleted, the others get added to a new face list. if an edge connected an inside and outside point, the intersection point with the clip plane is added to the new face.
This operation preserves the order of the face points, which is very important.

Additionally we save a list of all points that were an intersection with the clip_plane. These will form a new face that is entirely in the clip_plane. However this list is not necessarily ordered correctly. So we need to sort the points of that new face before adding it to the current polyhedron. The direction of sorting (clockwise or counterclockwise) doesn't matter. It just needs to be sorted in order to loop over the edges of a face later.

Repeating this process for all clip faces yields a new polyhedron which is entirely within the clip polyhedron.

This process for intersections only works for convex polyhedra. For non-convex polyhedra the voronoi cells are cut down too much.

-----

## 3. creating polyhedra
We use the python module `vpython` because it is very intuitive to use but still very efficient for 3D animation. However `vpython` does not implement polyhedra. Instead it only includes triangles and quadrilaterals to build your own shapes.

So I defined my own polyhedra by doing the following:

### 3D Polyhedra class `polyhedron`:
#### **Inputs:**
- `corners` - a list of all corners of the polyhedron
- `faces` - a list of lists of corner indices that make up each face. This is very similar to the `vor.ridge_vertices` described before.
- `color` - vpython vector for the color of the polyhedron
- `opacity` - float in [0,1] determining the opacity of the faces of the polyhedron

The corners and faces are all the information necessary to draw the polyhedron. But some further automatic preprocessing may be required.

#### **Drawing a face**
Let `face_indices` be a sublist of the input `faces`. To draw a face with `n` corners we use `n-2` triangles. These triangles all have the common corner given by the first element of `face_indices`: `face_indices[0]` Then we construct the triangles clockwise or counterclockwise using two of the remaining points each.

So the first triangle has vertices given by `face_indices[0]`, `face_indices[1]` and `face_indices[2]`, the second traingle has vertices determined by `face_indices[0]`, `face_indices[2]`, `face_indices[3]` and so on until we reach the final triangle with vertices `face_indices[0]`, `face_indices[n-2]` and `face_indices[n-1]`.

However this process is not guarantied to actually fill the whole polygon. It only works if the vertices pointed to by `face_indices` are sorted either clockwise or counterclockwise around the centerpoint of the face.

#### **sorting face vertices**
So before drawing a face we have to sort all the vertices. To do this we first calculate a point on the inside of the face as the center of mass of all face points. We call this point `face_com`.

We can then sort the face points by the angle between the vector connecting each point to `face_com` and a reference vector `start_vec`.

We set `start_vec = corners[face_indices[0]] - face_com`, the vector from the face center to the first corner. Now we need a function that yields the angle in a range from $[-\pi, \pi]$ or $[0, 2\pi]$.

We can calculate the angle in range $[0, \pi]$ using the formula
$$|v_s| |v_i|\cos(\alpha) = \langle \vec v_s, \vec v_i \rangle \iff \alpha = \arccos \left(\frac{\langle \vec v_s, \vec v_i \rangle}{|\vec v_s| |\vec v_i|}\right) \in [0, \pi]$$

This is implemented in the vpython function `vpy.diff_angle(v_s, v_i)`. Where $\vec v_s$ is `starting_vec` and $\vec v_i$ is the vector from the face center to the face corner `i`: `current_vec = corners[face_indices[i]] - face_com` for `i > 0`.

But we want the signed angle in range $[-\pi, \pi]$. To get the sign we first calculate the face normal $\vec v_n$ as the cross product of the first two face corners ($\vec v_n = \vec v_s \times \vec v_1$).

The sign of the angle is then equal to: 
$$sign \left( \langle v_s \times v_i, \vec v_n \rangle \right)$$

So to get the angle we want we use the formula:
$$\alpha = \arccos \left(\frac{\langle \vec v_s, \vec v_i \rangle}{|\vec v_s| |\vec v_i|}\right)\cdot sign \left( \langle v_s \times v_i, \vec v_n \rangle \right)  \in [-\pi, \pi]$$

Using this angle we simply sort the face corners.

#### **drawing the polyhedron**
Once all face vertices are sorted we can just loop over all faces and draw them to get the whole polyhedron.

If requested we can also draw all edges of those faces by just connecting all the sorted vertices (don't forget to connect `face_indices[-1]` to `face_indices[0]`)

finally we can convert all triangles to a vpython compound object so that it can be easily handled like every other vpython object.

-----

## 4. color the polyhedra
We want each polyhedron to be the color of the point inside the polyhedron.

Using the `vor.point_region` attribute of the `Voronoi` object we can get the index of the region associated to each input point. That way we can easily loop over the input point colors and `vor.point_ragion` to get the polyhedron and it's color.