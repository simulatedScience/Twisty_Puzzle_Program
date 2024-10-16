Given a cube with colored sides, we want to automatically find rotations (axis & angle) such that given any initial position (front face and top face color), we can reach any other position (front face and top face color) by applying a single rotation.

This is possible for a regular cube and may also be possible for all other shapes. A position 

# Algorithm for Rotational Symmetry Detection according to Hruda et al. 2021 [2]
- [1] [reflection symmetry detection](https://doi.org/10.1007/s00371-020-02034-w)  
- [2] [rotational symmetry detection](https://doi.org/10.1016/j.cagd.2022.102138)

---

- 3D point $x \in \mathbb{R}^3$
- plane $p \subset \mathbb{R}^3$
- reflections $r(p_1, x)$, $r(p_2, x)$ for non-parallel planes $p_1$, $p_2$

r(p, x) = "reflection of x across plane p"

from Sec. 2.1
Symmetry plane detection:

Input: set of points $X \subset \mathbb{R}^3 = \{x_1, x_2, ..., x_n\}$
Define symmetry measure $s_X(T)$ for a transformation $T$ of $X$ (e.g. $T=r(p,x)$):

$$s_X(T) = \sum_{i=1}^n\sum_{j=1}^n \varphi(||T(x_i)-x_j||)$$

For a similarity function $\varphi$ s.t. $\varphi(0)=1$ and $\varphi(l) \to 0$ monotonically decreasing for $l\to \infty$.  
Recommended similarity function:
$$\varphi(l) = \begin{cases}
\left( 1-\frac{l}{2.6}\alpha l \right)^5 \left( 8 \left( \frac{1}{2.6}\alpha l \right)^2 + 5\frac{1}{2.6} \alpha l + 1 \right) & \alpha l \leq 2.6 \\
0 & \alpha l > 2.6
\end{cases}$$
Set $\alpha = \frac{15}{l_{avg}}$ with $l_{avg}$ the average distance between a point in $X$ and the centroid (=COM) of $X$.
<!-- Set $\alpha \geq 2 \frac{2.6}{l_{min}}$ with $l_{min}$ the minimum distance between two points in $X$. -->

***Optimization:*** check distance with a cell structure first (cell-size $\frac{2.6}{\alpha}$).

## Algorithm for Symmetry plane detection
1. Create set of initial symmetry planes $P$ (e.g. 1000 random planes) 
   1. choose symmetry plane between two arbitrary points in $X$.
   2. Check distance $\delta$ of plane to all other plane candidates in $P$ (see Sec. 4.1.1, Eq. 4, 5)
   3. if $\delta < 0.1$, plane is too close.
   4. else: add plane to $P$.
2. For each plane $p \in P$
3. $\quad$ translate points $X$ and initial plane $p$ to origin.
4. $\quad$ (Optimization) simplify point set to ~1000 points by 3D cell based averaging
5. $\quad$ Evaluate symmetry measure $s_X(r(p_i, x))$ for all planes $p_i \in P$.
6. end for
7. Choose $S=5$ best planes by their symmetry measure
8. Find local maximum of symmetry measure $s_X(T)$ by optimizing over $p$ e.g. using L-BFGS (quasi-Newtown). $T$ are the reflections about the $S$ best planes
9. Only accept planes with symmetry measure >70% (adjust as needed) of best plane's measure.


## Algorithm for Rotational symmetry detection
Given a quarternion $Q$ and a point $s \in \mathbb{R}^3$ we define a new symmetry measure:

$$s_X(Q, s) = \left( \sum_{i=1}^n\sum_{j=1}^n \varphi(||\text{rot}(Q, s, x_i)-x_j||) \right) \text{Pen}(Q)$$

With a penalty function $\text{Pen}$ that penalizes rotations by small angles. Paper chooses $\text{Pen}(\leq 30°) = 0$, gradually increasing up to $\text{Pen}(43°)=1$ we likely want to choose lower angles here since rotations of 30° are not too uncommon in twisty puzzles.

In similarity function $s_X(T)$, set $\alpha = \frac{\textbf{20}}{l_{avg}}$ with $l_{avg}$ the average distance between a point in $X$ and the centroid (=COM) of $X$.

(Steps 1-8 are the same as for symmetry plane detection, with some slightly changed parameters)
1. Create set of initial symmetry planes $P$ (e.g. 1000 random planes) 
   1. choose symmetry plane between two arbitrary points in $X$.
   2. Check distance $\delta$ of plane to all other plane candidates in $P$ (see [SYM] Sec. 4.1.1, Eq. 4, 5)
   3. (Optimization) further pruning and averaging of similar planes
   4. if $\delta < 0.1$, plane is too close.
   5. else: add plane to $P$.
2. For each plane $p_i \in P$
3. $\quad$ translate points $X$ and initial plane $p$ to origin.
4. $\quad$ (Optimization) simplify point set to **~3000** points by 3D cell based averaging
5. $\quad$ Evaluate symmetry measure $s_X(r(p_i, x))$.
6. end for
7. Choose $S=30$ best planes by their symmetry measure
8. Find local maximum of symmetry measure $s_X(T)$ by optimizing over $p$ e.g. using L-BFGS (quasi-Newtown). $T$ are the reflections about the $S$ best planes
---
1.  Calculate intersection line and angle for each pair of planes found in step 8.
2.  For each intersection line, choose the point $s$ on the line that is closest to the centroid of $X$.
3.  (Optimization) prune similar rotations (see [ROT] Sec. 2.3)
4.  Start optimization of $Q, s$ with $s_X(Q, s)$ as objective function.
5.  Search around found rotation axes to detect lowest/ all angles of circular symmetries (see [ROT] Sec. 2.5)

## Potential modification

To reduce the point count, we could break down the puzzle into one point per move. For each move, calculate the COM of all points affected by it. Add this point to the new point set Y.
Then detect symmetries on Y. Then, use the symmetry axes of Y to get permutations of X using `rotations_to_permutations()`.

This naive approach might not work if multiple moves have the same COM. For example:
-  a 3x3x3 cube where opposite faces always turn together. In this case, all moves have COM equal to the whole puzzle's COM.
   -  Idea: generate a plane to separate the move into two halves, then only consider one half for the COM calculation. (Reliably generating such a plane could be hard. E.g. find the plane that minimizes the sum of all point's distances to the plane., but this may not be reliable.)
- Concentric moves can have the same COM.
- a nxnxn with n>=5: one move simultaneously turns two layers with an odd number of layers in between, another move turns the layer in the center between the first two.
  - Similar to case 1, this could possibly be resolved by finding a plane to remove a few points from each move's COM calculation.