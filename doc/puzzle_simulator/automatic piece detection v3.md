## Motivation
Current piece detection may struggle to find all pieces if it takes many moves to split the pieces (e.g. large Hungarian Rings puzzle).

Solution idea: through point/ piece orbits, find how points and pieces move. Pieces can only exchange places with other pieces of the same type.

## Algorithm

- given a set of pieces $\Psi$ and a set of moves $M_{base}$
- for each move $m \in M_{base}$, determine find where each piece $\psi \in \Psi$ maps to by applying the permutation $m$ to the points of the pieces. $m(\psi) =: \psi_m$ is the piece that $\psi$ maps to. Then, check all pieces in $\Psi$:
```latex
    For $\phi \in \Psi$:
        If $\psi_m \subsetneq \phi$:
            split $\phi$ into $\psi_m$ and $\phi \setminus \psi_m$
        Elif $\psi_m \supsetneq \phi$:
            split $\psi_m$ into $\phi$ and $\psi_m \setminus \phi$
        Elif $\psi_m = \phi$:
            mapped piece exists, do nothing
            break # no other pieces will overlap with $\psi_m$ because $\Psi$ is a partition of $X$
        Elif $\psi_m \cap \phi \neq \emptyset$:
            Add three new pieces: $\psi_m \cap \phi$, $\psi_m \setminus \phi$, and $\phi \setminus \psi_m$
        Else:
            pieces are disjoint, do nothing
            another piece $\phi$ will trigger one of the above cases
```