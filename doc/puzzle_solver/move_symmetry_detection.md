# Move based symmetry detection

An algorithm to replace the geometry based symmetry detection.


## Requirements
- preserve move overlap:
    - let $aff(m) be the set of points in $X$ affected by m
    - for any $m_1, m_2 \in M$, require: $\Big|aff(m_1) \cap aff(m_2)\Big| = \Big|aff(p(m_1)) \cap aff(p(m_2))\Big|$
- preserve move orientation (moves that previously turned clockwise should still turn clockwise):
    - consider the average rotation vector of a move m: $rot(m)$
    - let $COM_m = \sum_{x\in aff(m)} x / |aff(m)|$
    - let $COM_X = \sum_{x\in X} x / |X|$
    - then require: $< rot(m), (COM_m-COM_X)> \approx <rot(\pi(m)), (COM_{\pi(m)}-COM_X)>$  
    $=>$ geometry-independent symmetry detection may not be possible?

## Algorithm idea

1. calculate move signatures (piececount, (cycleorder1, cyclecount1), (cycleorder2, cyclecount2), ...) for each move:
   1. remove 1-cycles
   2. count number of points affected by move
   3. for each cycle order, count how many cycles of that order are in the move (sort by increasing cycle order)
2. Group moves by move signatures
3. choose smallest set $M$ of moves
4. for each $m \in M$:
   - for each $n \in M$:
