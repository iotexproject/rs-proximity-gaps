# P0 Attack Plan: Rigorous Density Bound

## Goal
Prove Conjecture 9.4 (paper.tex line 337):
  M ≤ C_w · C(n,w) / p^c + O(1)
where c = n-k-w is the syndrome codimension.

## What we know works (from this session's computation)

### The bound IS true empirically
- Tested for all n ≤ 30, p ≤ 631, w = 3, c = 2 (line case)
- Max M tracks C(n,3)/p^2 precisely
- p/n ≥ 8 → max M ≤ 2 (over 2000 random lines)

### Fiber bound (PROVED, for lines only)
- Non-pinned-pair lines: M ≤ n/w (Theorem 9.2)
- Rate 1/2: M ≤ 3
- ONLY works when c = w-1 (compatible subspace is a line)

### What DOESN'T work
1. **9 conditions from C^n = I**: equivalent to 3 conditions (Cayley-Hamilton)
2. **Stepanov classical**: all zeros are simple (multiplicity 1)
3. **Weil bound on character sums**: gives O(√p) per term, accumulates to O(p) — TOO WEAK
4. **Resultant of r0-1, r1**: res = 0 for 74% of lines (they DO share factors)

## Three promising attack directions

### Direction A: Generalize fiber bound to dim > 1
For d-dimensional subspace (d = w - c):
- The "rational function" becomes a rational MAP g: P^1 → P^d
- Each fiber has ≤ w elements (same argument)
- But a valid w-subset needs all w elements mapping to the SAME point in P^d
- Need: fiber counting in the image variety

Key question: for a degree-w map g: L → F_p^d, how many values v ∈ F_p^d
have |g^{-1}(v) ∩ L| ≥ w?

For d = 1 (line): answer is n/w (proved).
For d > 1: answer should be much smaller (intersection of curves).

### Direction B: Schwartz-Zippel on the σ-image variety
The σ-image is the image of the map φ: L^w → F_p^w, (x_1,...,x_w) ↦ (e_1,...,e_w).
The compatible subspace V imposes c linear conditions on (e_1,...,e_w).
Pulling back: c polynomial conditions on (x_1,...,x_w).
Each condition has degree ≤ w.
By Schwartz-Zippel: #solutions in L^w ≤ w^c · n^{w-c} / w!
Then M = #solutions / w! ≤ w^c · n^{w-c} / (w!)^2

For w=3, c=2: M ≤ 9 · n / 36 = n/4. Still O(n), not O(1).

Issue: Schwartz-Zippel doesn't use that L is a SUBGROUP of F_p^*.

### Direction C: Polynomial method (Dvir-style)
Construct a low-degree polynomial vanishing on σ-image ∩ V.
The σ-image has N = C(n,w) points. If V has p^d points and N/p^d < 1,
then there exists a polynomial of degree O(1) vanishing on σ-image ∩ V but not on V.
This gives M = O(1).

Issue: need N/p^d < 1, i.e., C(n,w) < p^{w-c}. For c = 2, w = 3: C(n,3) < p.
For BabyBear (p ≈ 2^31, n ≈ 2^20): C(n,3) ≈ 2^60 >> 2^31 = p. FAILS.

But with the STRUCTURE of σ-image (not just cardinality): maybe the variety
dimension helps. The σ-image variety has dimension w (as a constructible set
in F_p^w), but the fibers over V are lower-dimensional.

### Direction D: Additive combinatorics / sum-product
The σ-image points have BOTH additive structure (σ_1 = sum) and multiplicative
structure (σ_w = product). Sum-product estimates (Bourgain-Katz-Tao) bound
the concentration of sets with both structures.

For L (multiplicative subgroup): the exponential sum
  |Σ_{x ∈ L} ψ(f(x))| ≤ C · deg(f) · √p
is the Weil bound. Apply to f = linear combination of elementary symmetric polys.

The KEY technical lemma needed:
  Σ_{u ∈ V^⊥} |Σ_{B ∈ C(L,w)} ψ(u · σ(B))|^2 ≤ C · p^c · C(n,w)

This is a RESTRICTED PARSEVAL identity. If it holds, then by Cauchy-Schwarz:
  |M - C(n,w)/p^c| ≤ √(C · C(n,w))

and M ≤ C(n,w)/p^c + O(√(C(n,w))). For C(n,w)/p^c = O(1): M = O(1) + O(n^{w/2}).
Still too big.

Need: BETTER cancellation in the restricted sum, exploiting Toeplitz structure.

## Recommendation for next session
1. Start with Direction A (generalize fiber bound) — most likely to succeed
2. If stuck, try Direction D (Weil bound approach) with Gong's help
3. As fallback: state the conditional theorem (assuming Conjecture 9.4)
   and compute the FRI soundness improvement

## Key files
- paper.tex §9 (lines 279-360): current state of fiber bound
- notes/0071-fiber-bound-and-pinned-pair.md: full analysis
- notes/scripts/pinned_pair_analysis.py: transition data
- notes/scripts/fiber_theorem.py: fiber bound verification
