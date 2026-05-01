#!/usr/bin/env python3
"""
Packing bound for list decoding via MDS weight enumerator.

If M codewords are within distance w of a center c, they form a
"cluster" with pairwise distances in [n-k+1, 2w].

Bound M using:
1. MDS weight enumerator (number of low-weight codewords)
2. Plotkin-type bound on cluster size
3. Delsarte LP bound (if applicable)

Key constraint for multiplicative subgroups:
Pairwise differences f_i - f_j are codewords of RS[n,k], and they
all have weight in [n-k+1, 2w]. How many such codewords can form
a "packing" (with all pairwise differences in this range)?
"""

import math
from collections import Counter

def mds_weight_count(n, k, q, d):
    """Number of codewords of weight d in an MDS[n,k,n-k+1] code over F_q."""
    if d < n - k + 1 or d > n:
        return 0
    result = math.comb(n, d)
    s = 0
    for j in range(d - n + k):
        s += (-1)**j * math.comb(d, j) * (q**(d - n + k - j) - 1)
    return result * s


print("=" * 70)
print("PACKING BOUND VIA MDS WEIGHT ENUMERATOR")
print("=" * 70)

for n in [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26]:
    k = n // 2
    w = math.ceil((1 - math.sqrt(k / n)) * n)
    d_min = n - k + 1
    d_max = 2 * w

    print(f"\nn={n}, k={k}, w={w}, d_min={d_min}, d_max={d_max}")
    print(f"  Distance window: [{d_min}, {d_max}], width = {d_max - d_min + 1}")

    # For p = smallest valid prime
    for p in range(n + 1, 300):
        if all(p % d != 0 for d in range(2, int(p**0.5) + 1)) and (p - 1) % n == 0:
            break

    # Weight distribution
    total_in_window = 0
    print(f"  p={p}:")
    for d in range(d_min, min(d_max + 1, n + 1)):
        Ad = mds_weight_count(n, k, p, d)
        total_in_window += Ad
        print(f"    A_{d} = {Ad}")

    print(f"  Total codewords with weight in [{d_min},{d_max}]: {total_in_window}")
    print(f"  Total codewords: p^k - 1 = {p**k - 1}")
    print(f"  Ratio: {total_in_window / (p**k - 1):.6f}")

    # Plotkin-type bound on cluster size
    # If M vectors have pairwise distance ≥ d_min and ≤ d_max:
    # Sum of all pairwise distances S satisfies:
    # d_min * M(M-1)/2 ≤ S ≤ d_max * M(M-1)/2
    #
    # Also, S = Σ_{pos} (number of (i,j) pairs disagreeing at pos)
    # For a cluster centered at c: position pos has at most
    # M values {f_1(ω^pos), ..., f_M(ω^pos)} in F_p.
    # The number of disagreeing pairs at pos is:
    # M(M-1)/2 - Σ_v C(m_v, 2) where m_v = #{i: f_i(pos) = v}
    #
    # Summing over positions and using the MDS property...
    # This gets complicated. Let me use a simpler bound.

    # SINGLETON-type argument:
    # The M codewords, restricted to any n-k+1 positions, must be distinct
    # (since the code has distance n-k+1). So M ≤ p^{n-k+1}... too weak.

    # PLOTKIN bound: if d_min > n(1-1/p), then M ≤ d_min·p / (d_min·p - n(p-1))
    plotkin_threshold = n * (1 - 1/p)
    print(f"  Plotkin threshold: {plotkin_threshold:.2f}")
    if d_min > plotkin_threshold:
        M_plotkin = d_min * p / (d_min * p - n * (p - 1))
        print(f"  Plotkin bound: M ≤ {M_plotkin:.2f}")
    else:
        print(f"  d_min ≤ Plotkin threshold, bound not applicable")

    # Better: ELIAS-BASSALYGO bound
    # For a code with M codewords of length n over F_p,
    # all pairwise distances ≥ d_min:
    # M ≤ p^n / V(n, floor((d_min-1)/2))
    # where V(n,t) is the volume of Hamming ball of radius t.
    # This is the HAMMING bound on M, treating the list as a code.

    # But our "code" has additional structure: it's a subset of an RS code.
    # And pairwise distances are ALSO ≤ 2w.

    # DUAL PLOTKIN: upper bound on d_max
    # The average pairwise distance in a random subset of RS[n,k] is
    # n(1-1/p)(1 - (size-1)/(p^k-1))... hmm.

    # Let me just compute: for M codewords with pairwise distance
    # in [d_min, d_max], what's the max M?
    #
    # Using the JOHNSON BOUND:
    # If all codewords are within radius w of a common center,
    # and the code has minimum distance d = n-k+1:
    #
    # M ≤ (d * q) / (d * q - (q-1) * 2w * (2w+1-d))... complicated.

    # Simple upper bound: "sphere packing" in the distance-2w ball
    # centered at c. Volume = Σ_{d=0}^{w} C(n,d)(p-1)^d.
    # Each codeword claims a "distance d_min/2" ball around it.
    vol_w = sum(math.comb(n, d) * (p-1)**d for d in range(w+1))
    vol_half = sum(math.comb(n, d) * (p-1)**d for d in range(d_min // 2 + 1))
    M_packing = vol_w / vol_half
    print(f"  Packing bound: M ≤ {M_packing:.2f}")


# ================================================================
print("\n\n" + "=" * 70)
print("KEY RESULT: PAIRWISE DISTANCE CONSTRAINTS")
print("=" * 70)

# The KEY constraint is: for M codewords in the list,
# ALL M(M-1)/2 pairwise differences are NONZERO codewords of RS[n,k].
# These differences have weight in [n-k+1, 2w].
#
# The number of such differences available is A = Σ_{d=d_min}^{2w} A_d.
# So M(M-1)/2 ≤ A, giving M ≤ (1 + √(1+8A)) / 2.
#
# BUT: the differences are NOT independent! If f_1-f_2 = g and f_1-f_3 = h,
# then f_2-f_3 = h-g (also a codeword). So the differences form a
# SUBSPACE (or coset) of the code.
#
# A subspace of RS[n,k] with all nonzero elements having weight ≤ 2w
# has dimension at most ... what?
#
# A SUBCODE with minimum distance ≥ d_min and maximum weight ≤ 2w
# has rate at most (2w/n) by the Singleton bound applied to the "dual"...
# Actually, this is the rate of a code with min distance ≥ n - 2w + 1 on
# the SUPPORT set. Hmm.
#
# Let me think about it differently.
# The M codewords {f_1,...,f_M} span a subspace V of RS[n,k].
# V has dimension dim(V) = rank{f_1,...,f_M} ≤ k.
# All elements of V have weight ≤ 2w + wt(center contribution).
# Wait, V is a coset, not a subspace (unless c is a codeword).
#
# The DIFFERENCES V - V = {f_i - f_j} form a subspace.
# This subspace has all nonzero elements with weight in [d_min, 2w].
#
# By the Singleton bound: a linear code of length n, minimum distance d_min
# has dimension ≤ n - d_min + 1 = k. This is trivially satisfied.
#
# By the Plotkin bound: if d_min > n(1-1/p), then dim ≤ 1, so |V-V| ≤ p.
# For ρ=1/2: d_min = n/2+1 and n(1-1/p) = n-n/p ≈ n. So d_min < n(1-1/p)
# for p > 2. Plotkin not helpful.

# What about the CONSTRAINT d_max = 2w?
# A code where ALL weights are ≤ 2w has support ≤ 2w.
# So it's a code of effective length 2w (zero outside the support).
# By Singleton: dimension ≤ 2w - d_min + 1 = 2w - (n-k+1) + 1 = 2w - n + k.
#
# For ρ = 1/2: 2w - n + k = 2(1-√(1/2))n - n/2 ≈ 2(0.293)n - 0.5n = 0.086n.
#
# So the difference subspace has dimension ≤ 0.086n!
# And size ≤ p^{0.086n}.
# M ≤ p^{0.086n} + 1. Still exponential.

# BUT: the support is NOT fixed! Different elements of V-V have
# different supports. The constraint is: EACH element has support ≤ 2w,
# but the UNION of supports could be larger.

# Hmm, but elements of V-V have support ONLY on positions where
# at least two list members disagree. The TOTAL disagreement set
# is at most 2w (from the triangle inequality)...
# Wait, that's not right. The disagreement set of f_i - f_j is
# {pos : f_i(pos) ≠ f_j(pos)}, which has size ≤ d(f_i,f_j) ≤ 2w.
# But the UNION over all pairs could be up to n.

# KEY INSIGHT: Each f_i agrees with c on ≥ n-w positions.
# So f_i disagrees with c on ≤ w positions. Call these D_i.
# |D_i| ≤ w for all i.
# The total disagreement set D = ∪ D_i has |D| ≤ M·w... not useful.
# But each pair: D_i ∩ D_j = support of (f_i - f_j) restricted to ...
# Actually: f_i and f_j agree on positions where BOTH agree with c
# (positions outside D_i ∪ D_j). So:
# support(f_i - f_j) ⊆ D_i ∪ D_j, giving wt(f_i-f_j) ≤ |D_i|+|D_j| ≤ 2w.

# The union D = ∪ D_i: since each |D_i| ≤ w, and pairwise
# |D_i ∩ D_j| ≥ |D_i| + |D_j| - 2w + n - 2w... hmm, let me redo.
# |D_i ∪ D_j| = |D_i| + |D_j| - |D_i ∩ D_j|
# wt(f_i-f_j) ≤ |D_i ∪ D_j| = |D_i| + |D_j| - |D_i ∩ D_j|
# And wt(f_i-f_j) ≥ n-k+1.
# So |D_i ∩ D_j| ≤ |D_i| + |D_j| - (n-k+1).

# For |D_i| = |D_j| = w: |D_i ∩ D_j| ≤ 2w - n + k - 1.
# For ρ = 1/2: ≤ 2·0.293n - 0.5n - 1 ≈ 0.086n - 1.

# By inclusion-exclusion for M sets each of size ≤ w
# with pairwise intersections ≤ 2w-n+k-1:
# |∪ D_i| ≥ M·w - C(M,2)·(2w-n+k-1)
# ≤ n (since it's a subset of [n])
# So: M·w - M(M-1)/2 · (2w-n+k-1) ≤ n
# M[w - (M-1)/2 · (2w-n+k-1)] ≤ n
# For M large: (M-1)(2w-n+k-1)/2 ≈ Mw → M·[(n+k-1)/2 - (M-1)(2w-n+k-1)/2] ≤ n

# Let δ = 2w - n + k - 1 ≈ 0.086n (the max pairwise overlap).
# M·w - M(M-1)δ/2 ≤ n
# M(2w - (M-1)δ) ≤ 2n
# M ≤ 2n / (2w - (M-1)δ)
# Self-consistently: 2w - (M-1)δ > 0 → M < 2w/δ + 1

print("\nBound from overlap constraint: M < 2w/δ + 1")
for n in [10, 12, 14, 16, 18, 20, 22, 24, 26, 50, 100]:
    k = n // 2
    w = math.ceil((1 - math.sqrt(k / n)) * n)
    delta = 2 * w - n + k - 1
    if delta > 0:
        M_bound = 2 * w / delta + 1
        print(f"  n={n}: w={w}, δ={delta}, M ≤ {M_bound:.1f}")
    else:
        print(f"  n={n}: w={w}, δ={delta} ≤ 0 (unique decoding)")
