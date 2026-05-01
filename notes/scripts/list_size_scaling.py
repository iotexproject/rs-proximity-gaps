#!/usr/bin/env python3
"""
Compute list size M(delta) for larger n to check if M stays O(1).
Focus on: does M grow with n for fixed rate and delta above Johnson?

Cases:
- n=10, k=5, p=11  (p^5 = 161K)
- n=10, k=5, p=31  (p^5 = 28.6M — might be tight)
- n=12, k=6, p=13  (p^6 = 4.8M)
- n=14, k=7, p=29  (p^7 = 17B — too large for full FFT)
- n=16, k=8, p=17  (p^8 = 6.9B — too large)

For large cases: use random sampling instead of exact computation.
"""

import numpy as np
from collections import Counter
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
    assert (p - 1) % n == 0
    g = find_primitive_root(p)
    return pow(g, (p - 1) // n, p)

def krawtchouk(w, j, n, q):
    val = 0
    for s in range(min(w, j) + 1):
        if w - s > n - j:
            continue
        val += (-1)**s * (q-1)**(w-s) * comb(j, s) * comb(n-j, w-s)
    return val

def exact_list_size(n, k, p, verbose=True):
    """Exact computation via FFT for feasible cases."""
    t0 = time.time()
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    d = n - k
    total = p ** d

    if verbose:
        print(f"n={n}, k={k}, p={p}, total syndromes={total}")

    # Precompute L_powers
    L_powers = np.zeros((n, d), dtype=np.int64)
    for i in range(n):
        L_powers[i, 0] = 1
        for r in range(1, d):
            L_powers[i, r] = L_powers[i, r-1] * L[i] % p

    # All u in F_p^d
    indices = np.arange(total)
    u_matrix = np.zeros((total, d), dtype=np.int64)
    for dim in range(d):
        u_matrix[:, dim] = (indices // (p ** dim)) % p

    # Compute weights
    eval_matrix = u_matrix @ L_powers.T % p
    weights = np.count_nonzero(eval_matrix, axis=1)

    shape = tuple([p] * d)
    wt_array = np.zeros(shape, dtype=np.int32)
    for idx in range(total):
        wt_array[tuple(u_matrix[idx])] = weights[idx]

    weight_dist = Counter(weights.tolist())
    if verbose:
        print(f"Weight distribution: {dict(sorted(weight_dist.items()))}")

    # Compute B_j via FFT
    Bj_complex = {}
    for j in sorted(weight_dist.keys()):
        if j == 0 or weight_dist[j] == 0:
            continue
        indicator = (wt_array == j).astype(np.complex128)
        Bj_complex[j] = np.conj(np.fft.fftn(indicator))

    # Krawtchouk values
    K = {}
    for w in range(n+1):
        for j in weight_dist:
            K[(w,j)] = krawtchouk(w, j, n, p)

    # List size M(delta) excluding s=0
    delta_J = 1 - np.sqrt(k / n)
    zero_syn = tuple([0]*d)

    if verbose:
        print(f"Johnson bound delta_J = {delta_J:.4f}")
        print(f"\n{'delta':>6} {'w_max':>5} {'main_cum':>10} {'M':>6} {'M*':>6} {'above_J':>8}")

    results = {}
    for delta_pct in range(20, 60, 5):
        delta = delta_pct / 100.0
        w_max = int(delta * n)

        M_array = np.zeros(shape, dtype=np.float64)
        main_cum = 0
        for w in range(w_max + 1):
            Nw = np.zeros(shape, dtype=np.float64)
            for j, Bj in Bj_complex.items():
                Nw += K.get((w,j), 0) * np.real(np.conj(Bj))
            Nw += krawtchouk(w, 0, n, p)
            Nw /= p**d
            M_array += Nw
            main_cum += krawtchouk(w, 0, n, p) / p**d

        M = np.max(M_array)
        M_excl = M_array.copy()
        M_excl[zero_syn] = main_cum
        M_star = np.max(M_excl)

        above_J = "***" if delta > delta_J else ""
        results[delta] = (M, M_star)

        if verbose:
            print(f"{delta:6.2f} {w_max:5d} {main_cum:10.4f} {M:6.1f} {M_star:6.1f} {above_J:>8}")

    if verbose:
        print(f"Time: {time.time()-t0:.2f}s")
    return results

def sampling_list_size(n, k, p, n_samples=100000, verbose=True):
    """
    Estimate list size by sampling random syndromes and computing N_w directly.
    For each syndrome s, enumerate all codewords f and count agreements.
    """
    t0 = time.time()
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    if verbose:
        print(f"n={n}, k={k}, p={p} (sampling {n_samples} syndromes)")

    delta_J = 1 - np.sqrt(k / n)

    # Generate random syndromes (random points in F_p^n)
    # For each c, find all codewords within various distances
    # Codewords: evaluations of degree-<k polynomials on L

    # Enumerate ALL codewords (p^k of them)
    num_codewords = p ** k
    if verbose:
        print(f"Enumerating {num_codewords} codewords...")

    # Generate codeword matrix: each row is a codeword
    L_eval = np.zeros((n, k), dtype=np.int64)
    for i in range(n):
        L_eval[i, 0] = 1
        for j in range(1, k):
            L_eval[i, j] = L_eval[i, j-1] * L[i] % p

    # All coefficient vectors
    coeff_indices = np.arange(num_codewords)
    coeff_matrix = np.zeros((num_codewords, k), dtype=np.int64)
    for dim in range(k):
        coeff_matrix[:, dim] = (coeff_indices // (p ** dim)) % p

    # Codeword matrix: shape (num_codewords, n)
    codeword_matrix = coeff_matrix @ L_eval.T % p  # shape (num_codewords, n)

    if verbose:
        print(f"Generated {num_codewords} codewords")

    # Sample random syndromes (random c in F_p^n)
    rng = np.random.default_rng(42)
    max_M = {}  # delta -> max list size seen

    batch_size = min(n_samples, 10000)
    n_batches = (n_samples + batch_size - 1) // batch_size

    for batch in range(n_batches):
        actual_batch = min(batch_size, n_samples - batch * batch_size)
        if actual_batch <= 0:
            break

        # Random c vectors
        c_batch = rng.integers(0, p, size=(actual_batch, n))

        for idx in range(actual_batch):
            c = c_batch[idx]

            # Compute distance from c to each codeword
            # distance = number of positions where c[i] != codeword[i]
            agreements = np.sum(codeword_matrix == c[np.newaxis, :], axis=1)  # shape (num_codewords,)
            distances = n - agreements

            for delta_pct in range(20, 60, 5):
                delta = delta_pct / 100.0
                w_max = int(delta * n)
                M = np.sum(distances <= w_max)
                if delta not in max_M or M > max_M[delta]:
                    max_M[delta] = int(M)

    if verbose:
        print(f"\nMax list size from {n_samples} random syndromes:")
        print(f"{'delta':>6} {'w_max':>5} {'M_max':>6} {'above_J':>8}")
        for delta_pct in range(20, 60, 5):
            delta = delta_pct / 100.0
            w_max = int(delta * n)
            above_J = "***" if delta > delta_J else ""
            print(f"{delta:6.2f} {w_max:5d} {max_M.get(delta, 0):6d} {above_J:>8}")

    # Also check: worst-case c = weight-1 error vectors
    if verbose:
        print(f"\nWorst-case search: weight-1 error vectors...")

    worst_M = {}
    for i in range(n):
        for v in range(1, min(p, 20)):  # sample some values
            c = np.zeros(n, dtype=np.int64)
            c[i] = v
            agreements = np.sum(codeword_matrix == c[np.newaxis, :], axis=1)
            distances = n - agreements
            for delta_pct in range(20, 60, 5):
                delta = delta_pct / 100.0
                w_max = int(delta * n)
                M = int(np.sum(distances <= w_max))
                if delta not in worst_M or M > worst_M[delta]:
                    worst_M[delta] = M

    if verbose:
        print(f"{'delta':>6} {'w_max':>5} {'M_max':>6} {'above_J':>8}")
        for delta_pct in range(20, 60, 5):
            delta = delta_pct / 100.0
            w_max = int(delta * n)
            above_J = "***" if delta > delta_J else ""
            print(f"{delta:6.2f} {w_max:5d} {worst_M.get(delta, 0):6d} {above_J:>8}")

    if verbose:
        print(f"Time: {time.time()-t0:.2f}s")
    return max_M, worst_M

# ================================================================
# EXACT COMPUTATIONS
# ================================================================

print("=" * 70)
print("EXACT: n=10, k=5, p=11")
print("=" * 70)
exact_list_size(10, 5, 11)

print("\n" + "=" * 70)
print("EXACT: n=12, k=6, p=13")
print("=" * 70)
exact_list_size(12, 6, 13)

# ================================================================
# SAMPLING FOR LARGER CASES
# ================================================================

print("\n" + "=" * 70)
print("SAMPLING: n=10, k=5, p=31")
print("=" * 70)
sampling_list_size(10, 5, 31, n_samples=50000)

print("\n" + "=" * 70)
print("SAMPLING: n=12, k=6, p=37")
print("=" * 70)
sampling_list_size(12, 6, 37, n_samples=20000)

print("\n" + "=" * 70)
print("SAMPLING: n=16, k=8, p=17")
print("=" * 70)
sampling_list_size(16, 8, 17, n_samples=20000)

print("\n" + "=" * 70)
print("SAMPLING: n=20, k=10, p=41")
print("=" * 70)
sampling_list_size(20, 10, 41, n_samples=10000)

# ================================================================
# SCALING STUDY: Fixed rate 1/2, delta = 0.35, vary n and p
# ================================================================
print("\n" + "=" * 70)
print("SCALING: rate=1/2, delta=0.35, M vs n")
print("=" * 70)
print(f"{'n':>4} {'k':>4} {'p':>5} {'M_random':>10} {'M_wt1':>10}")

cases = [
    (6, 3, 7), (6, 3, 13), (6, 3, 31),
    (8, 4, 17), (8, 4, 41),
    (10, 5, 11), (10, 5, 31),
    (12, 6, 13), (12, 6, 37),
    (16, 8, 17),
    (20, 10, 41),
]

for n, k, p in cases:
    if (p - 1) % n != 0:
        continue
    max_M, worst_M = sampling_list_size(n, k, p, n_samples=10000, verbose=False)
    delta = 0.35
    print(f"{n:4d} {k:4d} {p:5d} {max_M.get(delta, 0):10d} {worst_M.get(delta, 0):10d}")
