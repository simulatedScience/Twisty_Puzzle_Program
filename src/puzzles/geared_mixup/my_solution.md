# Solution strategy and Algorithms for the Geared Mixup puzzle


### cycle 3 edges
cycle front right -> left back -> front bottom edges

8*(d' l' r r b l' r' d b t)  
= 8*(d' l' r2 b l' r' d b t)

order: 3
8*10 = 80 moves

When preparing this algorithm with (l' l'), all cycled edges are on the front face:
(front right -> front left -> front top) edges cycled clockwise.

avoid back moves:
8*(d' r' l l f r' l' d f t)

inverse:
8*(t' f' d' l r f' l' l' r d)

top-down mirrored version:
8*(t l r' r' b' l r t' b' d')  
= 8*(t l r'2 b' l r t' b' d')  
cycles front right -> left back -> front top edges

inverse: 8*(d b t r' l' b r r l' t')  
cycles front right <- left back <- front top edges

avoid back moves => rotate everything by 180°:  
8*(d f t l' r' f l l r' t')

inverse: 8*(t r l' l' f' r l t' f' d')


### cycle one center with two edges and 3 edges
One 3-cycle includes 3 edges, the other 2 edges and one center.

20*(d' t' b' d' r)

order: 3
20*5 = 100 moves


analogous to turning the cube around up axis by 180° and then applying the following algorithm:  
20*(d' t' f' d' l)

### turn four centers 180° in-place
turn all but the top and bottom centers in-place by 180°.

4*(f b' b' f' l b' f t)

order: 2
4*8 = 32 moves

### flip four edges in-place
Flip all top and bottom edges on the two side faces by 180° in-place.

12*(b' r l f)

order: 2
12*4 = 48 moves

### cycle 2 sets of three edges
2 3-cycles of edges:  
1. front up, front down and right up edges
2. left up, back up and right down edges

each is cycled clockwise


4*(r r t r' r' t r r t t r' r' t t)  
= 4*(r2 t r'2 t r2 t2 r'2 t2)

Order: 3
4*14 = 56 moves

Inverse: 4*(t' t' r r t' t' r' r' t' r r t' r' r')

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

### swap two centers with adjacent edges, flip one edge

210*(f f f r t)  
= 210*(f3 r t)

order: 2
210*5 = 1050 moves

### flip two edges, (& turn two centers 180°?)
Flip left top and left bottom edges 180°. Other changes are not visible.

24*(f t t r f' t' t' r')

order: 2
24*8 = 192 moves

### cycle one center and 4 edges


16*(b' f d b' d r f)

order: 5
16*7 = 112 moves

