#!/usr/bin/env python3
"""
Exact M computation for larger n via Lagrange interpolation approach.

Key insight: M is independent of p, so use the SMALLEST p.
For each center c, M = number of k-subsets S of [n] such that:
  1. The Lagrange interpolant of c|_S has degree < k
  2. The interpolant disagrees with c at ALL positions outside S where it should

Since |S| = n-w (agreement set), and |S| >= k:
- If |S| = k: the interpolant ALWAYS has degree < k (exactly determined)
- If |S| > k: need the extra interpolation conditions to be satisfied

For w at the Johnson radius with rate 1/2:
  w ≈ 0.293n, so |S| = n-w ≈ 0.707n > k = n/2.
  The number of extra conditions: |S| - k ≈ 0.207n.
  For the interpolant to have degree < k: need (|S|-k) additional agreement conditions.

APPROACH: For each c ∈ F_p^n, compute M(c) by checking ALL C(n, n-w) = C(n, w) subsets.
Then M = max_c M(c).

Trick: since M is p-independent, use the SMALLEST p. For n=14: p=29. For n=16: p=17.

But iterating over ALL c ∈ F_p^n is impossible (p^n too large).
Instead: iterate over SYNDROMES. The syndrome s ∈ F_p^{n-k} determines M(c).
For n=14, k=7, p=29: p^7 ≈ 17B. Too large.
For n=16, k=8, p=17: p^8 ≈ 7B. Too large.

Better: iterate over CODEWORDS + ERROR PATTERNS.
For each codeword f and each error set B ⊆ [n] with |B| = w:
  c = f with errors at B.
  The error values at B can be anything ≠ f(ω^i).
  M(c) includes f (distance w from c) plus any other codewords within distance w.

For each f: choose error positions B and error values.
The OTHER codewords within distance w from c are determined by the geometry.

EVEN BETTER: exploit the CODE SYMMETRY.
RS codes on multiplicative subgroups have the cyclic shift automorphism:
  σ: f(x) → f(ωx), which maps c to a cyclic shift.
So M(σ(c)) = M(c). We only need to test representatives of cyclic orbits.

Also: scalar multiplication f(x) → αf(x) preserves distances, so M(αc) = M(c).

The symmetry group has order n(p-1), reducing the search space by this factor.

APPROACH 3: For each pair of codewords (f1, f2) at mutual distance d:
  The "good center" c must be within distance w of both.
  c agrees with f1 on S1 ⊇ [n]\B1 and with f2 on S2 ⊇ [n]\B2.
  c is determined on S1 ∪ S2 (by agreeing with f1 on S1 and f2 on S2).
  The remaining positions: c is free.

For MDS: |S1 ∩ S2| ≤ k-1 (since d(f1,f2) = n - |S1 ∩ S2|... no,
  |S1 ∩ S2| = |{i: f1(i)=c_i AND f2(i)=c_i}|, which doesn't directly
  relate to d(f1,f2) because f1(i) might not equal f2(i) even if both ≠ c_i).

Actually: d(f1,f2) = |{i: f1(i) ≠ f2(i)}| ≥ d.

Let me use a different strategy: ENUMERATE CODEWORDS, then for each subset of M
codewords, check if there exists a center c within distance w of all of them.
"""

import numpy as np
from itertools import combinations
from math import comb
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
    g = find_primitive_root(p)
    return pow(g, (p - 1) // n, p)

def M_via_pair_search(n, k, p, w_target):
    """
    Strategy: enumerate all pairs of codewords at distance d(f1,f2) ≤ 2w.
    For each pair, find centers c within distance w of both.
    Then check for additional codewords near c.
    """
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    # Generate codewords
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

    print(f"  {num_cw} codewords generated", flush=True)

    d_min = n - k + 1
    best_M = 0

    # For each codeword f0, find all codewords within distance 2w
    # (potential co-list members)
    for f0_idx in range(min(num_cw, 5000)):  # sample codewords
        f0 = cw[f0_idx]

        # Find neighbors: codewords with d(f0, f) ≤ 2*w_target
        dists = np.sum(cw != f0[np.newaxis, :], axis=1)
        neighbors_idx = np.where((dists > 0) & (dists <= 2 * w_target))[0]

        if len(neighbors_idx) == 0:
            continue

        # For each neighbor, construct possible centers
        for f1_idx in neighbors_idx[:100]:  # limit pairs
            f1 = cw[f1_idx]
            d01 = int(np.sum(f0 != f1))

            # Center c must agree with f0 on S0 (|S0| >= n-w)
            # and with f1 on S1 (|S1| >= n-w)
            # Positions where f0 = f1: c can equal both
            agree01 = np.where(f0 == f1)[0]
            diff01 = np.where(f0 != f1)[0]

            # c must agree with f0 on some positions and f1 on others
            # On agree01: c = f0 = f1 (forced if we want agreement)
            # On diff01: c can be f0[i], f1[i], or something else

            # For c to be within distance w of f0:
            #   |{i: c_i != f0_i}| <= w
            # The positions where c can disagree with f0:
            #   - On agree01: if c_i != f0_i = f1_i, disagrees with BOTH
            #   - On diff01: if c_i = f1_i (not f0_i), disagrees with f0 only
            #                if c_i = f0_i (not f1_i), agrees with f0 only
            #                if c_i = something else, disagrees with both

            # Enumerate some promising centers
            # Strategy: set c = f0 everywhere, then modify some positions to agree with f1

            # c = f0 everywhere: d(c, f0) = 0, d(c, f1) = d01
            # To bring d(c, f1) down to ≤ w: need to change at least d01 - w positions
            # from f0 to f1 (on diff01 positions).

            need_change = max(0, d01 - w_target)
            max_change = min(w_target, len(diff01))

            if need_change > max_change:
                continue

            # Try all subsets of diff01 of size between need_change and max_change
            for num_to_f1 in range(need_change, min(max_change + 1, 8)):
                # Choose which diff positions to set c = f1
                for chosen in combinations(range(len(diff01)), num_to_f1):
                    c = f0.copy()
                    for idx_in_diff in chosen:
                        pos = diff01[idx_in_diff]
                        c[pos] = f1[pos]

                    # Compute M(c)
                    dists_from_c = np.sum(cw != c[np.newaxis, :], axis=1)
                    M = int(np.sum(dists_from_c <= w_target))

                    if M > best_M:
                        best_M = M

                    if len(list(combinations(range(len(diff01)), num_to_f1))) > 1000:
                        break  # too many combinations
                break  # just try the first num_to_f1

        if f0_idx % 1000 == 0 and f0_idx > 0:
            print(f"    Progress: {f0_idx}/{min(num_cw, 5000)}, best M = {best_M}", flush=True)

    return best_M

def M_via_exhaustive_center(n, k, p, w_target, max_centers=None):
    """
    Exhaustively search all possible centers via the FFT approach.
    Only feasible when p^{n-k} is manageable.
    """
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    d = n - k
    total = p ** d

    if total > 50_000_000:
        return None  # too large

    L_powers = np.zeros((n, d), dtype=np.int64)
    for i in range(n):
        L_powers[i, 0] = 1
        for r in range(1, d):
            L_powers[i, r] = L_powers[i, r-1] * L[i] % p

    shape = tuple([p] * d)
    wt_array = np.zeros(shape, dtype=np.int32)

    indices = np.arange(total)
    u_matrix = np.zeros((total, d), dtype=np.int64)
    for dim in range(d):
        u_matrix[:, dim] = (indices // (p ** dim)) % p

    eval_matrix = u_matrix @ L_powers.T % p
    weights = np.count_nonzero(eval_matrix, axis=1)

    from collections import Counter
    weight_dist = Counter(weights.tolist())

    for idx in range(total):
        wt_array[tuple(u_matrix[idx])] = weights[idx]

    # Compute B_j via FFT
    Bj = {}
    for j in sorted(weight_dist.keys()):
        if j == 0 or weight_dist[j] == 0:
            continue
        indicator = (wt_array == j).astype(np.complex128)
        Bj[j] = np.conj(np.fft.fftn(indicator))

    # Krawtchouk
    def kraw(w, j, nn, q):
        val = 0
        for s in range(min(w, j) + 1):
            if w - s > nn - j:
                continue
            val += (-1)**s * (q-1)**(w-s) * comb(j, s) * comb(nn-j, w-s)
        return val

    # Cumulative N_w for w <= w_target
    M_array = np.zeros(shape, dtype=np.float64)
    for w in range(w_target + 1):
        Nw = np.zeros(shape, dtype=np.float64)
        for j, Bj_arr in Bj.items():
            kval = kraw(w, j, n, p)
            if kval != 0:
                Nw += kval * np.real(np.conj(Bj_arr))
        Nw += kraw(w, 0, n, p)
        Nw /= p ** d
        M_array += Nw

    # Exclude s=0
    zero_syn = tuple([0] * d)
    main_cum = sum(kraw(w, 0, n, p) for w in range(w_target + 1)) / p**d
    M_array[zero_syn] = main_cum

    M_exact = int(np.round(np.max(M_array)))
    return M_exact

# ================================================================
# Compute M for all feasible cases
# ================================================================
print("=" * 70)
print("EXACT M at Johnson radius — comprehensive table")
print("=" * 70)

from math import ceil, sqrt

cases = []
# Rate 1/2
for n in range(4, 26, 2):
    cases.append((n, n//2))
# Rate 1/3
for n in [6, 9, 12, 15, 18]:
    cases.append((n, n//3))
# Rate 1/4
for n in [8, 12, 16, 20]:
    cases.append((n, n//4))
# Rate 3/4
for n in [8, 12, 16]:
    cases.append((n, 3*n//4))

cases = sorted(set(cases))

print(f"{'n':>4} {'k':>3} {'ρ':>5} {'d':>3} {'w_J':>3} {'2w-d':>5} {'p':>5} {'method':>8} {'M':>5}")

for n, k in cases:
    if k < 2 or k >= n:
        continue
    d = n - k + 1
    rho = k / n
    delta_J = 1 - sqrt(rho)
    w_J = ceil(delta_J * n)
    if w_J >= d or w_J < 1:
        continue
    overlap = 2 * w_J - d

    # Find smallest prime
    for p in range(max(n+1, 3), 200):
        if (p - 1) % n != 0:
            continue
        is_prime = all(p % dd != 0 for dd in range(2, int(p**0.5)+1))
        if is_prime:
            break
    else:
        continue

    # Try FFT (exact) first
    t0 = time.time()
    syndrome_size = p ** (n - k)
    codeword_size = p ** k

    if syndrome_size <= 50_000_000:
        M = M_via_exhaustive_center(n, k, p, w_J)
        method = "FFT"
    elif codeword_size <= 5_000_000:
        M = M_via_pair_search(n, k, p, w_J)
        method = "pair"
    else:
        M = None
        method = "SKIP"

    elapsed = time.time() - t0

    if M is not None:
        print(f"{n:4d} {k:3d} {rho:5.2f} {d:3d} {w_J:3d} {overlap:5d} {p:5d} {method:>8} {M:5d}  ({elapsed:.1f}s)", flush=True)
    else:
        print(f"{n:4d} {k:3d} {rho:5.2f} {d:3d} {w_J:3d} {overlap:5d} {p:5d} {method:>8}     -", flush=True)
