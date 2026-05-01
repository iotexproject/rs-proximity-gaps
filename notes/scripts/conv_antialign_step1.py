#!/usr/bin/env python3
"""
Convolutional Anti-Alignment — Step 1: σ-image on generic vs aligned subspaces.

Key question: For codim-c affine subspaces V of F_p^w,
              what determines whether |σ^{-1}(V)| is large?

Hypothesis: Large M only when V is "aligned" with σ_w fibers
            (i.e., the normal vectors of V have small σ_w component).

Experiments:
  E1. Random codim-c subspaces: distribution of M
  E2. σ_w-aligned subspaces: M distribution
  E3. RS conditions: coefficient matrix structure and M
  E4. Identify normal-vector property that predicts large M
"""

import itertools
import random
from collections import Counter

def make_field(p):
    """Precompute F_p arithmetic tables."""
    inv = [0] * p
    for a in range(1, p):
        for b in range(1, p):
            if (a * b) % p == 1:
                inv[a] = b
                break
    return inv

def elem_sym(B, omega, p):
    """Elementary symmetric polynomials of {omega^i : i in B}."""
    roots = [pow(omega, i, p) for i in B]
    w = len(roots)
    # e[j] = σ_j
    e = [0] * (w + 1)
    e[0] = 1
    for r in roots:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j-1] * r) % p
    return e[1:]  # (σ_1, ..., σ_w)

def primitive_root(p):
    """Find primitive root mod p."""
    for g in range(2, p):
        if all(pow(g, (p-1)//q, p) != 1 for q in prime_factors(p-1)):
            return g
    return None

def prime_factors(n):
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors

def find_omega(p, n):
    """Find element of order n in F_p."""
    g = primitive_root(p)
    return pow(g, (p-1)//n, p)

def compute_all_sigma(n, w, p, omega):
    """Compute σ(B) for all w-subsets B of Z/nZ."""
    results = []
    for B in itertools.combinations(range(n), w):
        sig = elem_sym(B, omega, p)
        results.append((B, tuple(sig)))
    return results

def gauss_elim(mat, rhs, p, inv_table):
    """Solve Ax = b over F_p. Return solution space as (particular, nullspace)."""
    m = len(mat)
    n_cols = len(mat[0])
    # Augmented matrix
    aug = [list(mat[i]) + [rhs[i]] for i in range(m)]

    pivot_cols = []
    row = 0
    for col in range(n_cols):
        # Find pivot
        found = -1
        for r in range(row, m):
            if aug[r][col] % p != 0:
                found = r
                break
        if found == -1:
            continue
        aug[row], aug[found] = aug[found], aug[row]
        pivot_cols.append(col)
        # Scale
        scale = inv_table[aug[row][col] % p]
        aug[row] = [(x * scale) % p for x in aug[row]]
        # Eliminate
        for r in range(m):
            if r != row and aug[r][col] % p != 0:
                factor = aug[r][col]
                aug[r] = [(aug[r][j] - factor * aug[row][j]) % p for j in range(n_cols + 1)]
        row += 1

    return aug, pivot_cols

def count_on_affine(all_sigma, A_mat, b_vec, p):
    """Count σ-images lying on affine subspace {x : Ax = b}."""
    count = 0
    hits = []
    for B, sig in all_sigma:
        # Check Ax = b
        ok = True
        for i in range(len(A_mat)):
            val = sum(A_mat[i][j] * sig[j] for j in range(len(sig))) % p
            if val != b_vec[i] % p:
                ok = False
                break
        if ok:
            count += 1
            hits.append(B)
    return count, hits

def rs_coefficient_matrix(n, k, w, c_coeffs, p):
    """
    Build the RS compatibility coefficient matrix.
    Condition m: Σ_{j=0}^{w} (-1)^j σ_j c_{m-w+j} = 0
    for m = k+w, ..., n-1.

    Rewrite: c_{m-w} + Σ_{j=1}^{w} (-1)^j c_{m-w+j} σ_j = 0
    => Σ_{j=1}^{w} (-1)^j c_{m-w+j} σ_j = -c_{m-w}

    So A[row, j-1] = (-1)^j * c_{m-w+j}, b[row] = -c_{m-w}
    for row index corresponding to m = k+w, ..., n-1.
    """
    conds = n - k - w
    A = []
    b = []
    for r in range(conds):
        m = k + w + r
        row = []
        for j in range(1, w + 1):
            idx = (m - w + j) % n  # c is periodic mod n? No, c has n coeffs
            coeff = ((-1)**j * c_coeffs[m - w + j]) % p
            row.append(coeff)
        A.append(row)
        b.append((-c_coeffs[m - w]) % p)
    return A, b

def experiment_1_random_subspaces(n, k, w, p, omega, all_sigma, inv_table, n_trials=500):
    """E1: Random codim-c subspaces — M distribution."""
    conds = n - k - w
    print(f"\n=== E1: Random codim-{conds} affine subspaces in F_{p}^{w} ===")

    M_vals = []
    for _ in range(n_trials):
        # Random A (conds × w) and b (conds × 1)
        A = [[random.randint(0, p-1) for _ in range(w)] for _ in range(conds)]
        b = [random.randint(0, p-1) for _ in range(conds)]
        M, _ = count_on_affine(all_sigma, A, b, p)
        M_vals.append(M)

    ctr = Counter(M_vals)
    print(f"  N = C({n},{w}) = {len(all_sigma)}")
    print(f"  Expected M ~ N/p^{conds} = {len(all_sigma)/p**conds:.2f}")
    print(f"  Distribution: min={min(M_vals)}, max={max(M_vals)}, avg={sum(M_vals)/len(M_vals):.2f}")
    print(f"  Top-10 values: {ctr.most_common(10)}")
    return M_vals

def experiment_2_aligned_subspaces(n, k, w, p, omega, all_sigma, inv_table, n_trials=500):
    """E2: σ_w-ALIGNED subspaces (conditions independent of σ_w)."""
    conds = n - k - w
    print(f"\n=== E2: σ_w-ALIGNED codim-{conds} subspaces (σ_w coefficient = 0) ===")

    M_vals = []
    for _ in range(n_trials):
        # Random A with last column = 0 (σ_w not involved)
        A = [[random.randint(0, p-1) for _ in range(w-1)] + [0] for _ in range(conds)]
        b = [random.randint(0, p-1) for _ in range(conds)]
        M, _ = count_on_affine(all_sigma, A, b, p)
        M_vals.append(M)

    ctr = Counter(M_vals)
    print(f"  Distribution: min={min(M_vals)}, max={max(M_vals)}, avg={sum(M_vals)/len(M_vals):.2f}")
    print(f"  Top-10 values: {ctr.most_common(10)}")
    return M_vals

def experiment_2b_partial_aligned(n, k, w, p, omega, all_sigma, inv_table, n_trials=500):
    """E2b: Partially aligned — only SOME conditions lack σ_w."""
    conds = n - k - w
    if conds < 2:
        print("\n=== E2b: SKIP (need conds >= 2) ===")
        return []

    print(f"\n=== E2b: Partially aligned (first row σ_w=0, rest random) ===")
    M_vals = []
    for _ in range(n_trials):
        A = []
        for r in range(conds):
            if r == 0:
                A.append([random.randint(0, p-1) for _ in range(w-1)] + [0])
            else:
                A.append([random.randint(0, p-1) for _ in range(w)])
        b = [random.randint(0, p-1) for _ in range(conds)]
        M, _ = count_on_affine(all_sigma, A, b, p)
        M_vals.append(M)

    ctr = Counter(M_vals)
    print(f"  Distribution: min={min(M_vals)}, max={max(M_vals)}, avg={sum(M_vals)/len(M_vals):.2f}")
    print(f"  Top-10 values: {ctr.most_common(10)}")
    return M_vals

def experiment_3_rs_conditions(n, k, w, p, omega, all_sigma, inv_table, n_trials=200):
    """E3: RS coefficient matrix structure."""
    conds = n - k - w
    print(f"\n=== E3: RS conditions (Toeplitz structure) ===")

    M_vals = []
    sigma_w_coeffs_list = []

    for trial in range(n_trials):
        # Random center: c_0,...,c_{k-1} are RS part (irrelevant); c_k,...,c_{n-1} are syndrome
        c_coeffs = [random.randint(0, p-1) for _ in range(n)]

        A, b = rs_coefficient_matrix(n, k, w, c_coeffs, p)
        M, hits = count_on_affine(all_sigma, A, b, p)
        M_vals.append(M)

        # Extract σ_w coefficients from A
        sigma_w_coeffs = [A[r][w-1] for r in range(conds)]
        sigma_w_coeffs_list.append(sigma_w_coeffs)

        if M > 2 * len(all_sigma) / p**conds:
            # High-M case: print details
            if trial < 20 or M > max(M_vals[:-1], default=0):
                print(f"  Trial {trial}: M={M}, σ_w coeffs = {sigma_w_coeffs}")
                print(f"    A = {A}")

    ctr = Counter(M_vals)
    print(f"\n  Distribution: min={min(M_vals)}, max={max(M_vals)}, avg={sum(M_vals)/len(M_vals):.2f}")
    print(f"  Top-10 values: {ctr.most_common(10)}")

    # Check: are σ_w coefficients ever all zero?
    all_zero_count = sum(1 for sc in sigma_w_coeffs_list if all(c == 0 for c in sc))
    print(f"\n  σ_w coefficients all zero: {all_zero_count}/{n_trials}")

    # σ_w coefficient structure
    print(f"\n  σ_w coefficient in RS conditions:")
    print(f"    For condition m: coeff = (-1)^w * c_m")
    print(f"    m ranges over {k+w}..{n-1}")
    print(f"    All-zero iff c_{{k+w}}=...=c_{{n-1}}=0")
    print(f"    This means syndrome supported on c_k,...,c_{{k+w-1}} only ({w} out of {n-k} syndrome positions)")

    return M_vals

def experiment_4_alignment_metric(n, k, w, p, omega, all_sigma, inv_table, n_trials=1000):
    """E4: Quantify alignment — correlation between σ_w coefficient magnitude and M."""
    conds = n - k - w
    print(f"\n=== E4: Alignment metric vs M ===")

    results = []
    for _ in range(n_trials):
        A = [[random.randint(0, p-1) for _ in range(w)] for _ in range(conds)]
        b = [random.randint(0, p-1) for _ in range(conds)]
        M, _ = count_on_affine(all_sigma, A, b, p)

        # "Alignment score": how much σ_w is involved
        # Use sum of |σ_w coefficients|^2 (or similar)
        sigma_w_coeffs = [A[r][w-1] for r in range(conds)]
        # Normalize: count how many rows have nonzero σ_w
        n_nonzero = sum(1 for c in sigma_w_coeffs if c != 0)

        results.append((M, n_nonzero, sigma_w_coeffs))

    # Bin by n_nonzero
    by_nz = {}
    for M, nz, _ in results:
        by_nz.setdefault(nz, []).append(M)

    print(f"  M distribution by # nonzero σ_w coefficients:")
    for nz in sorted(by_nz):
        vals = by_nz[nz]
        print(f"    {nz}/{conds} nonzero: count={len(vals)}, avg M={sum(vals)/len(vals):.2f}, max M={max(vals)}")

    # Also check: for high-M cases, what's the alignment structure?
    threshold = 2 * len(all_sigma) / p**conds
    high_M = [(M, nz, sc) for M, nz, sc in results if M > threshold]
    print(f"\n  High-M (>{threshold:.1f}) cases: {len(high_M)}/{n_trials}")
    if high_M:
        nz_dist = Counter(nz for _, nz, _ in high_M)
        print(f"    By # nonzero σ_w: {dict(nz_dist)}")

    return results

def experiment_5_which_coordinate(n, k, w, p, omega, all_sigma, inv_table, n_trials=500):
    """E5: Is σ_w special, or does ANY coordinate alignment give large M?"""
    conds = n - k - w
    print(f"\n=== E5: Alignment with σ_j for each j ===")

    for j_zero in range(w):
        M_vals = []
        for _ in range(n_trials):
            A = []
            for r in range(conds):
                row = [random.randint(0, p-1) for _ in range(w)]
                row[j_zero] = 0  # Zero out σ_{j+1} coefficient
                A.append(row)
            b = [random.randint(0, p-1) for _ in range(conds)]
            M, _ = count_on_affine(all_sigma, A, b, p)
            M_vals.append(M)

        print(f"  σ_{j_zero+1}=0 alignment: avg={sum(M_vals)/len(M_vals):.2f}, max={max(M_vals)}, "
              f"high rate={sum(1 for m in M_vals if m > 2*len(all_sigma)/p**conds)/len(M_vals):.3f}")

def main():
    # Test cases with conds >= 2
    test_cases = [
        (10, 5, 3, 11),   # conds=2
        (12, 6, 4, 13),   # conds=2
        (10, 5, 3, 31),   # conds=2, larger p
    ]

    for n, k, w, p in test_cases:
        omega = find_omega(p, n)
        inv_table = make_field(p)
        conds = n - k - w

        print(f"\n{'='*70}")
        print(f"n={n}, k={k}, w={w}, p={p}, conds={conds}, omega={omega}")
        print(f"{'='*70}")

        all_sigma = compute_all_sigma(n, w, p, omega)
        N = len(all_sigma)
        print(f"N = C({n},{w}) = {N}, N/p^c = {N/p**conds:.2f}")

        M1 = experiment_1_random_subspaces(n, k, w, p, omega, all_sigma, inv_table)
        M2 = experiment_2_aligned_subspaces(n, k, w, p, omega, all_sigma, inv_table)
        experiment_2b_partial_aligned(n, k, w, p, omega, all_sigma, inv_table)
        M3 = experiment_3_rs_conditions(n, k, w, p, omega, all_sigma, inv_table)
        experiment_4_alignment_metric(n, k, w, p, omega, all_sigma, inv_table)
        experiment_5_which_coordinate(n, k, w, p, omega, all_sigma, inv_table)

        # Summary comparison
        print(f"\n--- SUMMARY ---")
        print(f"  Random:    avg={sum(M1)/len(M1):.2f}, max={max(M1)}")
        print(f"  σ_w-align: avg={sum(M2)/len(M2):.2f}, max={max(M2)}")
        print(f"  RS:        avg={sum(M3)/len(M3):.2f}, max={max(M3)}")

if __name__ == '__main__':
    main()
