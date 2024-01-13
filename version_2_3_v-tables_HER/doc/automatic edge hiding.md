# Automatic edge hiding

## Motivation
For several features it may be desireable to hide certain edges of a polyhedron. For example, consider a puzzle piece that consists of more than one point. That piece would have internal edges that can get confusing when looking at the puzzle. 

So it would be beneficial if only the edges are shown, that:
1. are between two different pieces, or
2. are part of an edge of the clip shape

## Detecting in-piece edges
In `automatic_piece_detection.md` we have already discussed how we can automatically detect pieces by performing moves until they no longer seperate any pieces.

Let point A and B be two points on the same piece.

Unnecessary edges that are between two points of the same piece need to fulfill two criteria:
1. 1 They must be between the two points
2. 2 They must be perpendicular to the vector connecting both points.

-----

## 1.1. Checking for corners between two points
*Remark:* We use the notation $\vec{AB} := (B-A)$ to represent vectors between two points.

Looping over corners is more efficient than looping over edges as the corners contain the same information, because each corner is shared at least three edges which might each be considered in two different directions.

Let $C$ be the corner currently considered. If $C$ is in between $A$ and $B$, the angle between vectors $\vec{AB}$ and $\vec{AC}$ is greater then $90^\circ = \frac{\pi}{2}$.

So by calculating the vector $\vec{AB}$ once and $\vec{AC}$ for every corner $C$ we can easily classify the corners belonging to point $A$.

If an edge has both end points (corners) in between $A$ and $B$, it is between them too.

-----

## 1.2. Checking orthogonality of an edge and the connection vector
For each edge left by check 1, we require the vector that connects the two corners of that edge: $\vec{C_1C_2}$. Then we have two options to check for orthogonality:
1. check that the scalar product of $\vec{C_1C_2}$ and $\vec{AB}$ is close to $0$.
2. check that the angle $\angle(\vec{C_1C_2}, \vec{AB})$ is close to $90^\circ = \frac{\pi}{2}$, which usually involves computing the scalar product and an $\arccos$ function while not being more accurate.

-----

## 2. Detecting if an edge is shared with the clip shape
It is possible that the edges seperating the polyhedra within one piece are exactly on an edge of the clip shape. In that case it is desireable to keep the edge.

To check this we can simply test whether the two end points are on one edge of the clip shape.

Let $C_1$ and $C_2$ be the two end points of the edge between the points and $D_1$ and $D_2$ the end points of a clip shape edge.

We want to test for an angle $\alpha \approx \beta$ and both are close to $0$ or $\pi$ where </br>
   $\alpha := \angle(\vec{D_1D_2}, \vec{D_1C_1})$ and </br>
   $\beta := \angle(\vec{D_1D_2}, \vec{D_1C_2})$

Since we know that the pieces are entirely within the clip shape, it is sufficient to check $\alpha \approx 0$ and $\beta \approx 0$. The angle $\alpha \approx \pi \approx \beta$ and the case $\alpha \not\approx \beta$ cannot occur in our case.

-----

## Disclaimer
Most of this reasoning relies on the fact that the pieces are calculated from a voronoi diagram.

As far as I'm aware this makes it unnecessary to check whether the two cells around the points even share the edge. The tests 1.1 and 1.2 are sufficient to make sure they do share the edge *because* they are generated from a voronoi diagram.

However if that's given, it is not strictly required that the voronoi cells after clipping are still convex (as they can be for non-convex clip shapes).