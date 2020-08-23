# Ziel

Wir wollen aus einer endlichen Menge gegebener Permutationen die Ordnung der erzeugten Permutationsgruppe bestimmen.

1. Nach Satz von Lagrange wissen wir, dass die Elementordnung die Gruppenordnung teilt. Das heißt wir wissen, dass die gesuchte Gruppenordnung $\geq$ dem kgV der Elementordnungen sein muss.

2. Die Elementordnung kann einfach bestimmt werden indem die Permutation in disjunkte Zykel zerlegt wird. Das kgV der Zykellängen ist die Elementordnung.

3. Allein die Elementordnungen reichen aber nicht aus um die Gruppenordnung zu bestimmen. z.B. <(1,2,3,4,5), (1,2)> hat Ordnung $60$. dagegen hat <(1,2,3,4,5), (6,7)> nur Ordnung $10$.

4. FALSCH: Seien $\pi_i$ unsere $N$ Permutationen mit Ordnungen $n_i$. Dann können wir jede Permutation im Erzeugnis bilden als $\prod\limits_{i=1}^N \pi_{\sigma(i)}^{s_{\sigma(i)}}$, wobei $0\leq s_i < n_i$ ist und $\sigma \in S_N$

    Das heißt wir haben maximal \left(N! \prod\limits^N_{i=1} n_i \right)$ Elemente, die generiert werden können.