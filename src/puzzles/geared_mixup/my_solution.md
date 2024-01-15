# Solution strategy and Algorithms for the Geared Mixup puzzle

### flip 4 edges 180° in-place

6*(r r t r' r' t r r t t r' r' t' t')  
= 6*(r2 t r'2 t r2 t2 r'2 t'2)

Order: 2
6*14 = 84 moves

### cycle 2 sets of three edges
2 3-cycles of edges:  
1. front up, front down and right up edges
2. left up, back up and right down edges

each is cycled clockwise


4*(r r t r' r' t r r t t r' r' t t)  
= 4*(r2 t r'2 t r2 t2 r'2 t2)

Order: 3
4*14 = 56 moves

### cycle 4 center pieces and 1 edge piece, flip 1 edge
Cycle top, left, bottom, right center pieces and front right edge and flip the front left edge.


4*(r r t d' r r t' r r d r r d' r r d r r t')  
= 4*(r2 t d' r2 t' r2 d r2 d' r2 d r2 t')

Order: 5
4*19 = 76 moves

### cycle 2 centers and 3 edges
Cycle top and right centers along wiht the front left, front up and right up edges.
Applying the algorithm 3 times instead of 24 times results in one 2-cycle, one 4-cycle and one 5-cycle
after 12 applciations, the 2-cycle is solved and the 4-cycle has two flipped edges.

24*(t r t' l' t r' t' l)

order: 5
24*8 = 192 moves

### turn 4 edges 90° clockwise in-place

99*(r t f d t' r' d' f')

order: 4
99*8 = 792 moves