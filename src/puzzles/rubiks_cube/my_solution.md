# Solution strategy and Algorithms for the 3x3x3 Rubik's Cube

## Algorithms

### Swap two corners

This algorithm swaps the upper front two corners while also changing four edge pieces.

r r t d' r r t' r r d r r d' r r d r r t'  
= r2 t d' r2 t' r2 d r2 d' r2 d r2 t'

Order: 4

### Flip two edges

Flip the upper front and upper back edges in-place without changing any other pieces.

slice_y t slice_y t slice_y t slice_y t slice_y' t' slice_y' t' slice_y' t' slice_y' t'  
= 4*(slice_y t) 4*(slice_y' t')

Order: 2

### cycle three edges counterclockwise

Cycle the upper front, upper right, and upper back edges counterclockwise without changing any other pieces and without flipping them.

2*(r r t r r t r r t t r r t t)  
= 2*(r2 t r2 t r2 t2 r2 t2)  
= 2*(r2 t) 2*(r2 t2)

Order: 3

### Cycle three corners counterclockwise

Cycle all upper corners but the front right one counterclockwise without changing any other pieces. This also rotates each corner arount its axis through the COM 120° clockwise.

t r t' l' t r' t' l

Order: 3

### rotate 2 or 3 corners clockwise

Rotate the bottom front right corner clockwise 120°. Repeat if it needs to be rotated 240°, otherwise follow with d or d', then repeat to get a total of 360° rotation on 2 or 3 corners. AFterwards, reverse all d/ d' moves.

2*(r t r' t')

Order: 3

Example:

1. rotate bottom 3 corners clockwise except the front left one:  
2*(r t r' t') d' 2*(r t r' t') d' 2*(r t r' t') d d

2. rotate bottom front two corners clockwise, right by 120°, left by 240°:
2*(r t r' t') d 4*(r t r' t') d'

### turn upper center 180°

Rotate the upper center 180°, also changes rotation of some other centers.

8*(slice_y t)

Order: 2

## Solution strategy
1. Solve first layer's corners intuitively with correct orientation.
2. Try to cycle bottom layer's corners to get correct positions.
3. If necessary, swap two of the bottom corners.
4. Rotate bottom layer's corners to get correct orientation.
5. solve first layers edges intuitively.
6. solve second layer's edge positions by cycling 3 at a time.
7. solve top layer edge positions by cycling 3 at a time.
8. flip edges pairwise.