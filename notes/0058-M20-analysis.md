# Note 0058 — Why M(6,3,3) = 20 = C(6,3)

## The Striking Fact

For RS[6, 3] (rate 1/2, MDS distance 4) at w = 3:
$$M = 20 = \binom{6}{3}$$

This means: for the worst-case center $c$, EVERY 3-element subset of $[6]$ is a valid error set.

## Proof that M = C(n, w) when w = d - 1

**Claim**: For RS[n, k] (MDS) with $w = d - 1 = n - k$:
$$M(w) = \binom{n}{w}$$

**Proof**:
For each error set $B \subseteq [n]$ with $|B| = w = n-k$: the agreement set $S = [n] \setminus B$ has $|S| = k$. The Lagrange interpolant through $c|_S$ is the unique polynomial $f_B$ of degree $< k$ passing through the $k$ points $(ω^i, c_i)$ for $i \in S$.

The error condition: $f_B(ω^j) \neq c_j$ for all $j \in B$.

**Key**: the values $f_B(ω^j)$ for $j \in B$ are determined by $f_B$, which is determined by $c|_S$. The condition $f_B(ω^j) \neq c_j$ is a condition on $c_j$ (the center's value at error position $j$).

For EACH $j \in B$: $c_j \neq f_B(ω^j)$ is one condition. This excludes exactly 1 value of $c_j$ out of $p$ possible values.

Now: can we choose $c$ such that ALL $\binom{n}{w}$ error sets are valid?

For each $B$: the conditions are $c_j \neq f_B(ω^j)$ for $j \in B$, where $f_B$ depends on $c|_{[n]\setminus B}$.

This is a system of conditions on $c$ that are NOT independent (they share the center values).

**The remarkable fact**: the answer is YES for $p > $ some threshold. Here's why:

For a SPECIFIC center $c$: denote $f_S$ as the Lagrange interpolant through $c|_S$ for each $k$-subset $S$. The condition for ALL $B = [n]\setminus S$ to be valid: $f_S(ω^j) \neq c_j$ for all $j \notin S$, for ALL $k$-subsets $S$.

This is $\binom{n}{k} \times (n-k) = \binom{n}{k} \times w$ individual inequality conditions. But many of these involve the SAME $c_j$ values.

For $n=6, k=3, w=3$: there are $\binom{6}{3} = 20$ subsets, each contributing 3 inequalities. Total: 60 inequalities. But each $c_j$ (for $j = 0,...,5$) appears in... let me count.

Position $j$ appears in the error set of $\binom{n-1}{k-1} = \binom{5}{2} = 10$ subsets (those $S$ not containing $j$). For each such $S$: the condition $f_S(ω^j) \neq c_j$ constrains $c_j$ to avoid one value. If these 10 forbidden values are DISTINCT: $c_j$ must avoid 10 values, requiring $p > 10$.

For $p \geq 11$: there exist valid $c_j$ values. Hence M = 20 for all $p \geq 11$.

But actually M = 20 even for $p = 7$ (verified). So some of the 10 forbidden values must COINCIDE (reducing the number of distinct forbidden values below $p-1 = 6$).

**The detailed analysis for $p = 7$**: at each position $j$, the 10 forbidden values (from 10 different interpolants) take at most $p-1 = 6$ distinct values. Since $10 > 6$: by pigeonhole, at least 2 of the 10 interpolants give the SAME forbidden value at position $j$. So at most 6 distinct values are forbidden, and $c_j$ has at least $p - 6 = 1$ valid choice.

This is tight for $p = 7$: each position has exactly 1 valid choice. The worst-case $c$ is UNIQUE (up to symmetry).

## The General Formula

For $w = d - 1$: $M = \binom{n}{w}$. This is INDEPENDENT of $p$ for $p \geq p_0(n, k)$.

For $w < d - 1$: $M < \binom{n}{w}$ because the interpolants must have degree $< k$, which imposes additional constraints when $|S| > k$ (overconstrained system).

For $w = d - 2 = n - k - 1$: $|S| = k + 1$. The Lagrange interpolant has degree $\leq k$, but we need degree $< k$. The condition: the leading coefficient of the interpolant is 0. This is ONE extra condition on $c$, which eliminates $1/p$ of the candidates.

So $M(w = d-2) \approx \binom{n}{w} \times (1 - 1/p)^w \approx \binom{n}{w}$ for large $p$.

But for the Johnson radius (which is much smaller than $d-1$): $|S| \gg k$, and there are $|S| - k$ extra conditions. Only $O(1)$ error sets survive.

## Connection to List Decoding at Johnson

At the Johnson radius $w_J = \lceil(1-\sqrt{ρ})n\rceil$ for rate $ρ = k/n$:

$|S| = n - w_J \approx \sqrt{ρ} \cdot n = \sqrt{k \cdot n}$

Extra conditions per error set: $|S| - k \approx \sqrt{kn} - k = k(\sqrt{n/k} - 1)$

For each error set: the probability of passing all extra conditions is $\sim 1/p^{|S|-k}$.
Expected number of valid error sets: $\binom{n}{w} / p^{|S|-k}$.

For $|S| - k > 0$ and $p \gg 1$: this expected number is $O(1)$ or smaller.

But we want the WORST-CASE $c$, not the average. The worst case can have M much larger than the expected value. Our data shows M = O(1) for the worst case too.

## Key Observation

The data for rate 1/2 at Johnson:
- w = d-1 (distance = min dist - 1): M = C(n,w) (ALL error sets valid)
- w = d-2: M slightly less than C(n,w) but still large
- w at Johnson radius: M = O(1)

The transition from M = Θ(C(n,w)) to M = O(1) happens at the Johnson radius. This is exactly the "phase transition" that the Johnson bound captures: below Johnson, list decoding is unique; above Johnson but below d-1, list size is O(1); at d-1, list size explodes.

## For the Proof

The proof of M = O(1) at the Johnson radius should show:
1. Each error set B imposes $|S| - k$ extra conditions on $c$ (the "syndrome constraints")
2. The syndrome constraints for different B's are INDEPENDENT (or nearly so)
3. No center $c$ can simultaneously satisfy more than O(1) syndrome constraints

The independence of the syndrome constraints is where the MDS (Vandermonde) structure enters.

This is a problem about the GEOMETRY OF AFFINE SUBSPACES in $F_p^n$ — specifically, about the maximum number of affine subspaces (each of codimension $|S|-k$) that have a common point.

For GENERIC subspaces: the maximum intersection is bounded by codimension arguments. For the SPECIFIC subspaces defined by RS interpolation: the bound should be tighter due to the algebraic structure.
