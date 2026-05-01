# Note 0056 — List Structure: Error Set Packing + Algebraic Constraints

## The Packing Interpretation

For RS[n, k, d=n-k+1] and a list of M codewords $f_1, ..., f_M$ within distance $w$ from center $c$:

**Error sets**: $B_i = \{j : f_i(\omega^j) \neq c_j\}$ with $|B_i| \leq w$.

**Pairwise constraint**: $d(f_i, f_j) \geq d$, which gives:
$$|B_i \triangle B_j| + |\{j \in B_i \cap B_j : f_i(j) \neq f_j(j)\}| \geq d$$

**Key implication**: $|B_i \cap B_j| \leq t$ where $t$ depends on $w$ and $d$:
- If $|B_i \cap B_j| = s$: $d(f_i, f_j) \leq |B_i| + |B_j| - s = 2w - s$
- Need $2w - s + s = 2w \geq d$... wait, more carefully:
- $d(f_i, f_j) = |B_i \triangle B_j| + t_{ij}$ where $t_{ij}$ = disagreements at overlap
- $|B_i \triangle B_j| = |B_i| + |B_j| - 2s$ where $s = |B_i \cap B_j|$
- $t_{ij} \leq s$
- So $d(f_i, f_j) \leq 2w - 2s + s = 2w - s$
- Need $\geq d$: $s \leq 2w - d$

## Observed Configurations

### n=6, k=3, w=2: M = 3 (all p ≥ 7)

Error sets: {4,5}, {0,3}, {1,2} — DISJOINT 2-subsets of [6].

$2w - d = 4 - 4 = 0$, so $s = 0$ (forced disjoint).
Max packing: $\lfloor 6/2 \rfloor = 3$. TIGHT!

All pairwise distances = 4 = d (minimum distance). Each pair at distance exactly 2 from each other through the center.

### n=8, k=4, w=3: M = 7 (p=17), M = 5 (p=41)

Error sets for M=7 (p=17):
{4,6,7}, {1,3,5}, {0,2,7}, {0,4,5}, {1,2,6}, {2,3,4}, {0,3,6}

$2w - d = 6 - 5 = 1$, so $|B_i \cap B_j| \leq 1$.

This forms a **partial Steiner triple system** on [8]: 7 triples with pairwise intersection ≤ 1. The maximum packing number $D(8, 3, 1) = 8$.

When $|B_i \cap B_j| = 1$: the codewords MUST disagree at the overlap position (to achieve $d = 5$). When $|B_i \cap B_j| = 0$: $d = 6 > d$.

The combinatorial bound gives M ≤ 8. The ALGEBRAIC constraint (RS polynomial structure) brings it down to 7 (p=17) or 5 (p=41).

### Position occupancy (M=7 case):
Each position appears in 2-3 triples. The constraint: at each position used by $r$ codewords, the $r$ error values must be PAIRWISE DISTINCT and all ≠ $c_j$. This requires $p - 1 \geq r$, which is trivially satisfied.

## The General Packing Bound

**Theorem (combinatorial)**: $M \leq D(n, w, 2w - d)$ where $D(n, w, t)$ is the maximum number of $w$-subsets of $[n]$ with pairwise intersection $\leq t$.

For rate 1/2 ($d = n/2 + 1$) and $w$ just above the Johnson radius ($w \approx 0.29n$):

$t = 2w - d \approx 0.58n - 0.5n = 0.08n$

$D(n, w, t)$ grows polynomially in $n$ (roughly $O(n^t)$). NOT O(1).

**So the combinatorial bound alone cannot prove M = O(1).** The algebraic structure of RS codes on multiplicative subgroups is essential.

## Why M Decreases with p (Algebraic Constraint)

For larger p: more field elements, so MORE flexibility in choosing error values at overlap positions. But the RS polynomial constraint ($f_i$ must have degree $< k$) LIMITS the achievable error patterns.

The key: for each position $j$, the values $\{f_i(\omega^j) : i \in [M]\}$ lie on the evaluation of distinct degree-$< k$ polynomials at $\omega^j$. These values are constrained by the polynomial structure.

**Conjecture (algebraic packing bound)**: For RS[n, k] on multiplicative subgroup with $p > n^C$:
$$M \leq M_0(n, k, w)$$
where $M_0$ depends only on $n, k, w$ (not $p$), and $M_0 = O(1)$ for $w$ above the Johnson radius.

## Connection to BGM/Guo-Zhang

For RANDOM evaluation points: BGM (2023) proved M = O(1) using the "GM-MDS" framework. The key property: the Vandermonde matrix of random evaluation points satisfies certain "generalized MDS" conditions.

For multiplicative subgroups: the Vandermonde matrix is the DFT matrix. Whether it satisfies GM-MDS conditions is OPEN.

**The gap**: Proving that the DFT matrix (evaluation at $1, \omega, \omega^2, ..., \omega^{n-1}$) satisfies the GM-MDS conditions required by BGM's theorem. This would immediately give M = O(1) for RS codes on multiplicative subgroups.

This verification could potentially use character sums / Weil bounds — exactly the tools from the Gong-Helleseth-Golomb tradition.

## What We Need from Gong

The precise mathematical problem for Prof. Gong:

**Problem**: For the DFT matrix $V = (\omega^{ij})_{0 \leq i < n, 0 \leq j < k}$ where $\omega$ is a primitive $n$-th root of unity in $\mathbb{F}_p$, verify the GM-MDS($\ell$) condition for $\ell = O(1/\epsilon)$.

This reduces to showing that certain polynomial identities involving $\omega$ (specifically, certain subdeterminants and their products) are nonzero in $\mathbb{F}_p$. The non-vanishing conditions are polynomial inequalities in $\omega$, and can potentially be verified using Weil bounds over finite fields.

This is a CONCRETE, WELL-DEFINED algebraic problem that bridges:
1. BGM's coding-theoretic framework
2. The multiplicative subgroup structure
3. Character sum techniques from sequence theory
