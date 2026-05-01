#!/usr/bin/env python3
"""
Test the GM-MDS condition for RS codes on multiplicative subgroups.

The GM-MDS condition (from Brakensiek-Gopi-Makam, STOC 2023):
An [n, k] RS code with evaluation points alpha_1, ..., alpha_n satisfies
the GM-MDS(ell) condition if:

For any partition I_1, ..., I_{ell+1} of [n] with |I_j| >= k for all j,
and any vectors v_1, ..., v_ell in F_q^n, the polynomial system:

  sum_{i in I_j} v_r(i) / prod_{m != i, m in I_j} (alpha_i - alpha_m)  != 0

for at least one (j, r) pair, where the v_r are the "list codewords."

Actually, the precise condition is more subtle. Let me use the simplified version:

**MDS(ell) condition**: For any set S of <= ell codewords of RS[n,k],
and any set T of n - k + 1 evaluation points, the restriction of S to T
has full rank. Equivalently: no ell codewords can "conspire" to have
unusual zero patterns on evaluation subsets.

For our purposes: the key test is whether the SUBCODE DISTANCE property holds.

**Subcode distance property**: For any subcode V of RS[n,k] with dim(V) = m <= ell,
the minimum distance of V is >= n - k + 1 (same as the full code).

For MDS codes: ANY subcode has minimum distance >= n - k + 1 (since the code is MDS).
So MDS(ell) is TRIVIALLY satisfied for any ell!

Wait — this can't be right, because then ALL MDS codes would achieve list-decoding
capacity, but we know they don't (for arbitrary evaluation points).

Let me reconsider. The BGM condition must be STRONGER than just MDS.

Actually, looking at the BGM paper more carefully: the condition is about the
"GM-MDS conjecture" which says that certain MULTILINEAR conditions on the
evaluation points hold. Specifically:

For evaluation points a_1, ..., a_n, define:
  V_S = Vandermonde matrix (a_i^j)_{i in S, 0 <= j < k}  for S subset [n]

The GM-MDS condition: for any collection of subsets S_1, ..., S_m of [n]
with specific size constraints, the product det(V_{S_1}) * det(V_{S_2}) * ... != 0.

For multiplicative subgroups: a_i = omega^i. The Vandermonde determinant:
det(V_S) = prod_{i < j in S} (omega^i - omega^j)

This is ALWAYS nonzero for distinct elements. So the individual determinants
are nonzero. But the GM-MDS condition involves SUMS of products of determinants,
which could vanish.

Let me test the specific condition from the Shangguan-Tamo paper (the predecessor
of BGM). They define:

An [n,k] MDS code is (s,L)-MDS if for every L+1 pairwise disjoint subsets
T_0, T_1, ..., T_L of [n] with |T_0| = s and |T_j| = k for j >= 1, and
for every nonzero polynomials f_1, ..., f_L of degree < k:

  The vectors (f_j(alpha_i))_{i in T_0} for j = 1, ..., L are linearly independent.

This is a test of "no aliasing" on small subsets.

For RS codes: f_j are degree-<k polynomials. The evaluations on T_0 (size s) are
determined by the polynomial. For L <= s: L polynomials evaluated on s points are
linearly independent iff the s x L matrix has rank L, which holds as long as the
polynomials are pairwise distinct (and s >= L).

Wait, that's also trivially true. Let me think again...

Actually, the condition involves the f_j being SPECIFIC polynomials (related to
the list decoding problem), not arbitrary polynomials. The key is:

Given a received word c and L list codewords f_1, ..., f_L all within distance
delta*n from c, the f_j define specific error patterns. The GM-MDS condition
ensures that these error patterns cannot "conspire" to cover evaluation points
in a specific bad way.

For our computational test: let me directly check the list size for various
configurations and verify that it matches the predicted O(1) bound.

Actually, let me take a different approach. The simplest test of the GM-MDS property:

**Test**: For RS[n, k] on multiplicative subgroup, enumerate all possible list
configurations (sets of M codewords within distance w from some c) and check
the maximum M. We already did this! And found M = O(1).

But to prove it, we need to understand WHY. Let me investigate the STRUCTURE
of the list codewords.

For n=6, k=3, w=2, M=3 (all p):
- Find the 3 codewords and the center c
- Understand the algebraic structure of this configuration

For n=8, k=4, w=3, M=7 (p=17):
- Find the 7 codewords and the center c
- Check what makes this configuration possible at p=17 but not p=41

This structural analysis will guide the proof.
"""

import numpy as np
from itertools import combinations
import time

def find_primitive_root(p):
    for g in range(2, p):
        factors = set()
        temp = p - 1
        d = 2
        while d * d <= temp:
            while temp % d == 0:
                factors.add(d)
                temp //= d
            d += 1
        if temp > 1:
            factors.add(temp)
        if all(pow(g, (p-1)//q, p) != 1 for q in factors):
            return g

def find_omega(n, p):
    assert (p - 1) % n == 0
    g = find_primitive_root(p)
    return pow(g, (p - 1) // n, p)

def analyze_list_structure(n, k, p, w_target):
    """Find and analyze the maximum list configuration."""
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    # Generate all codewords
    L_eval = np.zeros((n, k), dtype=np.int64)
    for i in range(n):
        L_eval[i, 0] = 1
        for j in range(1, k):
            L_eval[i, j] = L_eval[i, j-1] * L[i] % p

    num_cw = p ** k
    coeff = np.zeros((num_cw, k), dtype=np.int64)
    idx = np.arange(num_cw)
    for dim in range(k):
        coeff[:, dim] = (idx // (p ** dim)) % p

    cw = coeff @ L_eval.T % p

    print(f"n={n}, k={k}, p={p}, w={w_target}")
    print(f"Generated {num_cw} codewords")

    # Find the maximum list size at distance <= w_target
    # Check random + structured points
    rng = np.random.default_rng(42)

    best_M = 0
    best_c = None
    best_list = None

    # Try all codewords + small errors
    for cw_idx in range(min(num_cw, 500)):
        base = cw[cw_idx]
        # Try all weight-2 errors from this codeword
        for pos1 in range(n):
            for pos2 in range(pos1+1, n):
                for v1 in range(1, min(p, 5)):
                    for v2 in range(1, min(p, 5)):
                        c = base.copy()
                        c[pos1] = (c[pos1] + v1) % p
                        c[pos2] = (c[pos2] + v2) % p

                        dist = np.sum(cw != c[np.newaxis, :], axis=1)
                        M = np.sum(dist <= w_target)

                        if M > best_M:
                            best_M = M
                            best_c = c.copy()
                            best_list = np.where(dist <= w_target)[0]

    # Also try random points
    for _ in range(10000):
        c = rng.integers(0, p, size=n)
        dist = np.sum(cw != c[np.newaxis, :], axis=1)
        M = np.sum(dist <= w_target)
        if M > best_M:
            best_M = M
            best_c = c.copy()
            best_list = np.where(dist <= w_target)[0]

    print(f"Best M = {best_M}")

    if best_M > 0 and best_list is not None:
        print(f"\nCenter c = {best_c}")
        print(f"\nList codewords (distance <= {w_target}):")
        for idx in best_list:
            f = cw[idx]
            d = int(np.sum(f != best_c))
            diff_pos = np.where(f != best_c)[0]
            coefficients = coeff[idx]
            print(f"  f = {f} (coeff={coefficients}, dist={d}, diff_pos={diff_pos})")

        # Analyze pairwise distances
        print(f"\nPairwise distances:")
        for i, idx_i in enumerate(best_list):
            for j, idx_j in enumerate(best_list):
                if i < j:
                    d_ij = int(np.sum(cw[idx_i] != cw[idx_j]))
                    print(f"  d(f_{i}, f_{j}) = {d_ij}")

        # Analyze error sets
        print(f"\nError sets (positions where f_i != c):")
        for i, idx in enumerate(best_list):
            f = cw[idx]
            err_pos = set(np.where(f != best_c)[0].tolist())
            err_vals = {pos: (int(best_c[pos]), int(f[pos])) for pos in err_pos}
            print(f"  B_{i} = {err_pos} (c[pos]->f[pos]: {err_vals})")

        # Check error set intersections
        print(f"\nError set intersections:")
        for i, idx_i in enumerate(best_list):
            for j, idx_j in enumerate(best_list):
                if i < j:
                    B_i = set(np.where(cw[idx_i] != best_c)[0].tolist())
                    B_j = set(np.where(cw[idx_j] != best_c)[0].tolist())
                    inter = B_i & B_j
                    print(f"  |B_{i} ∩ B_{j}| = {len(inter)} ({inter})")

    return best_M, best_c, best_list

# ================================================================
# Analyze specific cases
# ================================================================

# Case 1: n=6, k=3, p=7, w=2, expected M=3
print("=" * 60)
analyze_list_structure(6, 3, 7, 2)

print("\n" + "=" * 60)
# Case 2: n=6, k=3, p=13, w=2, expected M=3
analyze_list_structure(6, 3, 13, 2)

print("\n" + "=" * 60)
# Case 3: n=8, k=4, p=17, w=3, expected M=7
analyze_list_structure(8, 4, 17, 3)

print("\n" + "=" * 60)
# Case 4: n=10, k=5, p=11, w=3, expected M=3
analyze_list_structure(10, 5, 11, 3)
