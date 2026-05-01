#!/usr/bin/env python3
"""
Two studies:
1. M vs p for n=6, k=3, w=3 with EXACT (FFT) computation for large p
   - Track the decrease of M with p
   - Find the asymptotic M_∞
2. M for large n via TARGETED sampling
   - For n=16,20,24: can't enumerate codewords (p^k too large)
   - BUT: can use the FFT approach if syndrome space is manageable
   - Or: use random polynomial evaluation + Hamming ball counting
"""

import numpy as np
import time
from collections import Counter
from math import comb

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

def krawtchouk(w, j, n, q):
    val = 0
    for s in range(min(w, j) + 1):
        if w - s > n - j:
            continue
        val += (-1)**s * (q-1)**(w-s) * comb(j, s) * comb(n-j, w-s)
    return val

def exact_M_via_fft(n, k, p, w_target):
    """Exact M(w) via FFT over syndrome space."""
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    d = n - k
    total = p ** d

    # Precompute L_powers
    L_powers = np.zeros((n, d), dtype=np.int64)
    for i in range(n):
        L_powers[i, 0] = 1
        for r in range(1, d):
            L_powers[i, r] = L_powers[i, r-1] * L[i] % p

    # Weight array
    shape = tuple([p] * d)
    wt_array = np.zeros(shape, dtype=np.int32)

    indices = np.arange(total)
    u_matrix = np.zeros((total, d), dtype=np.int64)
    for dim in range(d):
        u_matrix[:, dim] = (indices // (p ** dim)) % p

    eval_matrix = u_matrix @ L_powers.T % p
    weights = np.count_nonzero(eval_matrix, axis=1)

    for idx in range(total):
        wt_array[tuple(u_matrix[idx])] = weights[idx]

    weight_dist = Counter(weights.tolist())

    # Compute B_j(s) via FFT
    Bj = {}
    for j in sorted(weight_dist.keys()):
        if j == 0 or weight_dist[j] == 0:
            continue
        indicator = (wt_array == j).astype(np.complex128)
        Bj[j] = np.conj(np.fft.fftn(indicator))

    # Compute cumulative N_w(s) for w <= w_target
    K = {}
    for w in range(w_target + 1):
        for j in weight_dist:
            K[(w, j)] = krawtchouk(w, j, n, p)

    M_array = np.zeros(shape, dtype=np.float64)
    for w in range(w_target + 1):
        Nw = np.zeros(shape, dtype=np.float64)
        for j, Bj_arr in Bj.items():
            kval = K.get((w, j), 0)
            if kval != 0:
                Nw += kval * np.real(np.conj(Bj_arr))
        Nw += krawtchouk(w, 0, n, p)
        Nw /= p ** d
        M_array += Nw

    # Exclude s=0 (codeword syndrome)
    zero_syn = tuple([0] * d)
    main_cum = sum(krawtchouk(w, 0, n, p) for w in range(w_target + 1)) / p**d
    M_array[zero_syn] = main_cum

    M_exact = int(np.round(np.max(M_array)))
    return M_exact

def M_via_polynomial_sampling(n, k, p, w_target, n_centers=100000):
    """
    For large p^k: instead of enumerating ALL codewords,
    for each test center c, enumerate polynomials f of degree < k
    and count agreements.

    But with p^k potentially huge, we can't enumerate all polynomials.

    Alternative: for each center c, the list of codewords within distance w
    is the same as the list of polynomials f with deg < k and
    |{i : f(omega^i) = c_i}| >= n-w.

    We can find these by: for each (n-w)-subset S of [n], check if there
    exists a polynomial f of degree < k agreeing with c on S.
    If |S| >= k: f is uniquely determined (Lagrange interpolation).
    Then check if f agrees with c on any additional positions.
    """
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    # Precompute evaluation matrix for Lagrange interpolation
    # For a set S of size k, the unique polynomial agreeing with c on S
    # is given by Lagrange interpolation.

    # For efficiency, precompute Vandermonde inverses for all k-subsets.
    # But C(n, k) can be large. Let's just do Lagrange on the fly.

    from itertools import combinations

    def lagrange_interp(points, values, eval_pts, p):
        """Lagrange interpolation mod p.
        points: list of x-coordinates (size k)
        values: list of y-values (size k)
        eval_pts: list of points to evaluate at
        Returns: list of evaluations
        """
        k = len(points)
        result = [0] * len(eval_pts)
        for i in range(k):
            # Compute Lagrange basis polynomial L_i evaluated at eval_pts
            num = 1
            den = 1
            for j in range(k):
                if j != i:
                    den = den * (points[i] - points[j]) % p
            den_inv = pow(den, p - 2, p)  # Fermat's little theorem

            for idx, x in enumerate(eval_pts):
                basis = 1
                for j in range(k):
                    if j != i:
                        basis = basis * (x - points[j]) % p
                basis = basis * den_inv % p
                result[idx] = (result[idx] + values[i] * basis) % p
        return result

    rng = np.random.default_rng(42)
    best_M = 0

    agree_threshold = n - w_target  # minimum agreement for list membership

    for trial in range(n_centers):
        # Generate test center
        if trial < n_centers // 3:
            c = [rng.integers(0, p) for _ in range(n)]
        elif trial < 2 * n_centers // 3:
            # Near-codeword
            coeffs = [rng.integers(0, p) for _ in range(k)]
            c = [sum(coeffs[j] * pow(L[i], j, p) for j in range(k)) % p for i in range(n)]
            err_wt = rng.integers(1, w_target + 1)
            err_pos = rng.choice(n, err_wt, replace=False)
            for pos in err_pos:
                c[pos] = (c[pos] + rng.integers(1, p)) % p
        else:
            # Random codeword + weight-2 error
            coeffs = [rng.integers(0, p) for _ in range(k)]
            c = [sum(coeffs[j] * pow(L[i], j, p) for j in range(k)) % p for i in range(n)]
            pos1, pos2 = rng.choice(n, 2, replace=False)
            c[pos1] = (c[pos1] + rng.integers(1, p)) % p
            c[pos2] = (c[pos2] + rng.integers(1, p)) % p

        # For this center c, find all codewords within distance w_target.
        # Strategy: for each k-subset S of [n], interpolate through c|_S,
        # check if the resulting polynomial agrees with c on more positions.
        M = 0
        seen_coeffs = set()

        for S in combinations(range(n), k):
            S_list = list(S)
            points = [L[i] for i in S_list]
            values = [c[i] for i in S_list]

            # Lagrange interpolation
            all_evals = lagrange_interp(points, values, L, p)

            # Check degree: the interpolated polynomial has degree < k
            # (guaranteed by Lagrange with k points)

            # Check agreement
            agree = sum(1 for i in range(n) if all_evals[i] == c[i])

            if agree >= agree_threshold:
                # This is a list codeword! Count it.
                coeff_key = tuple(all_evals)  # use evaluations as key
                if coeff_key not in seen_coeffs:
                    seen_coeffs.add(coeff_key)
                    M += 1

        if M > best_M:
            best_M = M

        if trial % 10000 == 0 and trial > 0:
            print(f"  Trial {trial}/{n_centers}: best M so far = {best_M}", flush=True)

    return best_M

# ================================================================
# STUDY 1: M vs p for n=6, k=3, w=3 (EXACT)
# ================================================================
print("=" * 70)
print("STUDY 1: n=6, k=3 — EXACT M via FFT for various w and p")
print("=" * 70)

print(f"{'p':>5} {'M(w=2)':>7} {'M(w=3)':>7} {'M(w=4)':>7}")
for p in [7, 13, 19, 31, 37, 43, 61, 67, 73, 79, 97, 103, 109, 127]:
    if (p - 1) % 6 != 0:
        continue
    # Check if p is prime
    is_prime = all(p % d != 0 for d in range(2, int(p**0.5)+1))
    if not is_prime:
        continue

    t0 = time.time()
    M2 = exact_M_via_fft(6, 3, p, 2)
    M3 = exact_M_via_fft(6, 3, p, 3)
    M4 = exact_M_via_fft(6, 3, p, 4)
    print(f"{p:5d} {M2:7d} {M3:7d} {M4:7d}  ({time.time()-t0:.1f}s)", flush=True)

# ================================================================
# STUDY 2: M vs p for n=8, k=4 (EXACT where feasible)
# ================================================================
print("\n" + "=" * 70)
print("STUDY 2: n=8, k=4 — EXACT M via FFT")
print("=" * 70)

print(f"{'p':>5} {'M(w=2)':>7} {'M(w=3)':>7} {'M(w=4)':>7}")
for p in [17, 41, 73, 89, 97]:
    if (p - 1) % 8 != 0:
        continue
    is_prime = all(p % d != 0 for d in range(2, int(p**0.5)+1))
    if not is_prime:
        continue
    if p ** 4 > 20_000_000:  # limit for FFT
        print(f"{p:5d} (skipped: p^4 = {p**4} too large)", flush=True)
        continue

    t0 = time.time()
    M2 = exact_M_via_fft(8, 4, p, 2)
    M3 = exact_M_via_fft(8, 4, p, 3)
    M4 = exact_M_via_fft(8, 4, p, 4)
    print(f"{p:5d} {M2:7d} {M3:7d} {M4:7d}  ({time.time()-t0:.1f}s)", flush=True)

# ================================================================
# STUDY 3: Large n via polynomial sampling
# ================================================================
print("\n" + "=" * 70)
print("STUDY 3: Large n via Lagrange interpolation sampling")
print("=" * 70)

# For each center c, enumerate all C(n,k) possible k-subsets for interpolation.
# C(n,k) for n=16, k=8 is C(16,8) = 12870 — feasible per center!
# For n=20, k=10: C(20,10) = 184756 — feasible but slow per center.
# For n=24, k=12: C(24,12) = 2704156 — slow.

cases_large = [
    (14, 7, 29, 5),  # w_J = ceil(0.293*14) = 5
    (14, 7, 43, 5),
    (16, 8, 17, 5),  # w_J = ceil(0.293*16) = 5
    (16, 8, 97, 5),
    (18, 9, 19, 6),  # w_J = ceil(0.293*18) = 6
    (20, 10, 11, 6), # w_J = ceil(0.293*20) = 6, C(20,10) = 184756
    (20, 10, 41, 6),
]

for n, k, p, w in cases_large:
    if (p - 1) % n != 0:
        print(f"n={n}, k={k}, p={p}: SKIP (n does not divide p-1)")
        continue

    n_subsets = comb(n, k)
    n_centers = min(5000, max(1000, 100000 // n_subsets))

    print(f"\nn={n}, k={k}, p={p}, w={w}, C(n,k)={n_subsets}, testing {n_centers} centers...", flush=True)
    t0 = time.time()
    M = M_via_polynomial_sampling(n, k, p, w, n_centers=n_centers)
    elapsed = time.time() - t0

    d = n - k + 1
    delta_J = 1 - np.sqrt(k / n)
    overlap = 2 * w - d

    print(f"  d={d}, delta_J={delta_J:.4f}, 2w-d={overlap}")
    print(f"  M = {M} (from {n_centers} centers, {elapsed:.1f}s)")
