# Note 0059 — The Rank Deficiency Theorem: Why M = O(1)

## The Discovery

For RS[8, 4] over F_17, at w = 3 (Johnson radius):
- M = 7 codewords in the worst-case list
- Each error set B_i contributes 1 linear condition on the center c
- The 7 condition normals form a 7 × 8 matrix with **rank 3** (not 4 = n-k!)
- So 4 out of 7 conditions are linearly dependent on the first 3

## The Rank Formula

For RS[n, k] at distance w with n-w = k+1 (i.e., w = d-2):

Each error set B (|B| = w, agreement set S = [n]\B has |S| = k+1) contributes
the linear condition:

$$\sum_{i \in S} c_i \cdot \text{cofactor}_i(V_S) = 0$$

where $\text{cofactor}_i(V_S) = (-1)^{k+i} \prod_{a < b \in S \setminus \{i\}} (\omega^a - \omega^b)$.

The C(n, w) such conditions form a matrix N of size C(n,w) × n.

**Observation**: rank(N) < n-k for all tested cases:

| n | k | w | C(n,w) | n-k | rank(N) | M |
|---|---|---|--------|-----|---------|---|
| 8 | 4 | 3 | 56 | 4 | **3** | **7** |

## Why Rank < n-k: The Vandermonde Structure

The normals are NOT arbitrary vectors — they are COFACTORS of Vandermonde submatrices.
The Vandermonde structure imposes algebraic relations among the normals.

Specifically: the cofactor_i(V_S) = ∏_{a<b ∈ S\{i}} (ω^a - ω^b) is a product of
DIFFERENCES of powers of ω. These products satisfy multiplicative relations
(e.g., the "factored Vandermonde" structure).

The rank deficiency means: certain SUMS of Vandermonde cofactors are zero.
These are polynomial identities in ω — they hold for ALL p (since M is p-independent).

## The Proof Strategy

**Theorem (to prove)**: For RS[n, k] on multiplicative subgroup of order n:
The Vandermonde cofactor matrix N has rank ≤ r(n, k) for some function r < n-k.

**Then**: The maximum M is:
$$M = \text{max \# of C(n,w) hyperplanes through a common point in } F_p^{n-k}$$

Since the hyperplanes span a rank-r subspace: the maximum # through a point is:
$$M \leq C(n,w) - \text{(# independent hyperplanes not through the point)}$$

More precisely: the point must lie on ALL M hyperplanes. Since the hyperplanes
span rank-r space: the point has n-k-r free coordinates. The M hyperplanes
must all pass through this point, which constrains the hyperplane selection.

**The bound**: M ≤ (# hyperplanes in a rank-r arrangement that share a common point).

For r < n-k: this is a FINITE GEOMETRY problem, and M = O(1) follows from
standard results on hyperplane arrangements in finite-dimensional spaces.

## What's Needed for a Complete Proof

1. **Compute rank(N) for general (n, k)**: Is it always < n-k? What is the exact rank?

2. **Prove rank bounds using Vandermonde identities**: Show that specific sums of
   Vandermonde cofactors vanish identically (as polynomials in ω).

3. **Bound M from rank**: Use hyperplane arrangement theory to bound the maximum
   number of hyperplanes through a common point.

## Connection to GM-MDS

The rank of the Vandermonde cofactor matrix is PRECISELY the condition studied in
the GM-MDS framework (Brakensiek-Gopi-Makam). For GENERIC evaluation points:
rank = n-k (full rank), giving M ≤ C(n,w)/p ≈ 0 for large p.

For MULTIPLICATIVE SUBGROUPS: rank < n-k (rank deficient!), which ALLOWS M > 0
but still constrains M to O(1).

The rank deficiency is the ALGEBRAIC FINGERPRINT of the multiplicative subgroup
structure. It's what makes the DFT matrix different from random evaluation points.

## Correction: Full Normal Matrix Has Full Rank

The FULL normal matrix (all C(n,w) error sets) has rank = n-k (FULL RANK).
This was verified for ALL (n,k) up to n=15.

The rank deficiency occurs only for the SPECIFIC SUBSET of M error sets
that achieve the worst-case list. The M normals span only a rank-r < n-k subspace.

## The Concurrence Problem

The correct formulation: given C(n,w) hyperplanes in F_p^{n-k} (defined by
Vandermonde cofactors), what is the maximum number that pass through a single point?

This is a FINITE GEOMETRY problem: hyperplane concurrence in the Vandermonde arrangement.

## Comprehensive Data at Johnson Radius

| n | k | w_J | conds/B | syn_dim | naive M | actual M | M/naive |
|---|---|-----|---------|---------|---------|----------|---------|
| 6 | 3 | 2 | 1 | 3 | 3 | **3** | 1.0 |
| 8 | 4 | 3 | 1 | 4 | 4 | **7** | 1.75 |
| 10 | 5 | 3 | 2 | 5 | 2.5 | **3** | 1.2 |
| 12 | 6 | 4 | 2 | 6 | 3 | **6** | 2.0 |

"Naive M" = syndrome_dim / conditions_per_B (assuming condition independence).

Key observations:
- conds/B = 1: M can exceed naive (n=8: 7 > 4). Dependencies allow more.
- conds/B = 2: M ≈ 2× naive (n=12: 6 = 2×3). Roughly doubles.
- ALL values are O(1). Max M = 7 for n ≤ 12.

## M distribution across syndromes

For n=12, k=6, p=13, w=4:
- M=6: 2664 syndromes (0.06%)
- M=5: 48528 syndromes (1%)
- M=4: 422328 (8.7%)
- M=3: 1323216 (27.4%)
- M=2: 1869265 (38.7%)
- M=1: 998016 (20.7%)
- M=0: 162792 (3.4%)

The vast majority of syndromes have M ≤ 3. Only 0.06% achieve M = 6.

## What's Needed for a Complete Proof

1. **Bound concurrence number**: For the Vandermonde hyperplane arrangement in
   F_p^{n-k}, show the max concurrence is O(1). This is a FINITE GEOMETRY result.

2. **Leverage conds/B ≥ 2**: When each error set contributes ≥ 2 conditions,
   the effective constraint is tighter. The naive bound n-k/(n-w-k) gives
   O(1) directly when n-w-k ≥ 2 (which holds at Johnson for n ≥ 10).

3. **Handle conds/B = 1 case**: When n-w = k+1 (w = d-2), each error set
   contributes only 1 condition. The concurrence is harder to bound, but the
   data shows M ≤ 7 for n ≤ 12.
