#!/usr/bin/env python3
"""
Convolutional Anti-Alignment — Step 4: Clean proof-oriented analysis.

KEY INSIGHT: Split the problem into two cases:
  Case 1: center c is within distance < w of some codeword f.
    → By MDS + triangle inequality, M_actual = 1 when d < conds+1.
    → For conds+1 ≤ d < w, need separate analysis.
  Case 2: center c is at distance ≥ w from all codewords.
    → M_alg = M_actual (no overcounting).
    → Bound M_alg via convolutional anti-alignment.

Experiments:
  E1. Verify Case 1: for centers near codewords, is M_actual = 1?
  E2. Case 2: for "far" centers (d ≥ w), what is M_alg = M_actual?
  E3. Non-trivial max M_alg over Toeplitz subspaces (exclude near-codeword centers)
  E4. Distribution of M_alg for far centers: is it concentrated around N/p^c?
"""

import itertools
import random
from collections import Counter

def primitive_root(p):
    for g in range(2, p):
        if all(pow(g, (p-1)//q, p) != 1 for q in prime_factors(p-1)):
            return g

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
    g = primitive_root(p)
    return pow(g, (p-1)//n, p)

def eval_poly(coeffs, x, p):
    val = 0
    for c in reversed(coeffs):
        val = (val * x + c) % p
    return val

def precompute_codewords(n, k, p, omega):
    """Precompute all RS[n,k] codewords as evaluation tuples."""
    L = [pow(omega, i, p) for i in range(n)]
    codewords = []
    for idx in range(p**k):
        coeffs = []
        tmp = idx
        for _ in range(k):
            coeffs.append(tmp % p)
            tmp //= p
        f_eval = tuple(eval_poly(coeffs, x, p) for x in L)
        codewords.append(f_eval)
    return codewords, L

def hamming_dist(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)

def elem_sym(B, omega, p):
    roots = [pow(omega, i, p) for i in B]
    w = len(roots)
    e = [0] * (w + 1)
    e[0] = 1
    for r in roots:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j-1] * r) % p
    return tuple(e[1:])

def dft_coeffs(c_eval, omega, p, n):
    """Compute DFT coefficients of c from evaluation."""
    omega_inv = pow(omega, p-2, p)
    n_inv = pow(n, p-2, p)
    coeffs = []
    for j in range(n):
        val = 0
        for i in range(n):
            val = (val + c_eval[i] * pow(omega_inv, i*j, p)) % p
        coeffs.append((val * n_inv) % p)
    return coeffs

def toeplitz_matrix(n, k, w, c_synd, p):
    conds = n - k - w
    A = []
    b = []
    for r in range(conds):
        row = []
        for j in range(1, w + 1):
            idx = r + j
            coeff = ((-1)**j * c_synd[idx]) % p if idx < len(c_synd) else 0
            row.append(coeff)
        A.append(row)
        b.append((-c_synd[r]) % p)
    return A, b

def count_on_affine_fast(sigma_tuples, A_mat, b_vec, p, w):
    conds = len(A_mat)
    count = 0
    for sig in sigma_tuples:
        ok = True
        for i in range(conds):
            val = 0
            for j in range(w):
                val += A_mat[i][j] * sig[j]
            if val % p != b_vec[i]:
                ok = False
                break
        if ok:
            count += 1
    return count

def experiment_1_case1(n, k, w, p, omega, codewords, L):
    """E1: Verify that centers near codewords have M_actual ≤ 1 (for d < conds+1)."""
    conds = n - k - w
    d_min = n - k + 1
    print(f"\n=== E1: Case 1 — Centers near codewords ===")
    print(f"  d_min = {d_min}, w = {w}, conds = {conds}")
    print(f"  Claim: d(c, f) < conds+1 = {conds+1} → M_actual = 1")
    print(f"  Triangle: any g ≠ f with d(g,c) ≤ w needs d(f,g) ≤ d+w,")
    print(f"  but d(f,g) ≥ d_min = {d_min}. So need d ≥ d_min - w = {d_min - w}")

    # For each distance d = 1, ..., w-1, sample centers near codewords
    for d in range(1, w):
        M_max = 0
        n_tested = 0
        for f_idx in range(min(100, len(codewords))):
            f = codewords[f_idx]
            # Create center at distance d from f
            positions = random.sample(range(n), d)
            c_eval = list(f)
            for pos in positions:
                c_eval[pos] = (c_eval[pos] + random.randint(1, p-1)) % p
            c_eval = tuple(c_eval)
            # Count M_actual
            M_actual = sum(1 for g in codewords if hamming_dist(g, c_eval) <= w)
            M_max = max(M_max, M_actual)
            n_tested += 1

        print(f"  d={d}: max M_actual = {M_max} (over {n_tested} tests)")

def experiment_2_case2(n, k, w, p, omega, codewords, all_sigma, sigma_tuples, L, n_trials=500):
    """E2: Case 2 — centers at distance ≥ w from all codewords."""
    conds = n - k - w
    print(f"\n=== E2: Case 2 — Far centers (d ≥ w from all codewords) ===")

    far_M = []
    far_Malg = []
    near_count = 0

    for trial in range(n_trials):
        # Random center
        c_eval = tuple(random.randint(0, p-1) for _ in range(n))

        # Check distance to nearest codeword
        min_d = min(hamming_dist(c_eval, f) for f in codewords)
        M_actual = sum(1 for f in codewords if hamming_dist(f, c_eval) <= w)

        if min_d >= w:
            far_M.append(M_actual)
            # Also compute M_alg
            c_coeffs = dft_coeffs(c_eval, omega, p, n)
            c_synd = c_coeffs[k:]
            A, b = toeplitz_matrix(n, k, w, c_synd, p)
            M_alg = count_on_affine_fast(sigma_tuples, A, b, p, w)
            far_Malg.append(M_alg)

            if M_actual != M_alg:
                print(f"  WARNING: M_actual={M_actual} ≠ M_alg={M_alg} at trial {trial}!")
        else:
            near_count += 1

    if far_M:
        print(f"  Far centers: {len(far_M)}/{n_trials} ({near_count} near)")
        print(f"  M_actual: avg={sum(far_M)/len(far_M):.2f}, max={max(far_M)}")
        print(f"  M_alg:    avg={sum(far_Malg)/len(far_Malg):.2f}, max={max(far_Malg)}")
        print(f"  M_actual == M_alg in all cases: {all(a == b for a, b in zip(far_M, far_Malg))}")
        print(f"  Distribution of M_actual: {Counter(far_M).most_common(10)}")
    else:
        print(f"  No far centers found ({near_count} all near)")

    return far_M, far_Malg

def experiment_3_toeplitz_nontrivial(n, k, w, p, omega, codewords, sigma_tuples, L):
    """E3: Non-trivial max M_alg over Toeplitz subspaces."""
    conds = n - k - w
    n_synd = n - k
    total = p**n_synd
    print(f"\n=== E3: Non-trivial max M_alg over Toeplitz subspaces ===")

    if total > 500000:
        print(f"  Too many syndromes ({total}), sampling...")
        mode = "sample"
        n_check = 200000
    else:
        mode = "exhaustive"
        n_check = total

    max_M_far = 0  # max M_alg for centers far from codewords
    max_M_far_synd = None
    max_M_overall = 0  # max M_alg (including near-codeword overcounting)
    max_M_overall_synd = None
    M_far_dist = Counter()
    M_near_dist = Counter()

    checked = 0
    for idx in (range(total) if mode == "exhaustive" else range(n_check)):
        if mode == "exhaustive":
            c_synd = []
            tmp = idx
            for _ in range(n_synd):
                c_synd.append(tmp % p)
                tmp //= p
        else:
            c_synd = [random.randint(0, p-1) for _ in range(n_synd)]

        A, b = toeplitz_matrix(n, k, w, c_synd, p)
        M_alg = count_on_affine_fast(sigma_tuples, A, b, p, w)

        # Check if center is near a codeword
        # c_eval = IDFT of (c_0,...,c_{k-1}, c_synd)
        # For now, set c_0=...=c_{k-1}=0 (adding a codeword doesn't change M_actual)
        c_coeffs = [0]*k + list(c_synd)
        c_eval = tuple(eval_poly(c_coeffs, x, p) for x in L)
        min_d = min(hamming_dist(c_eval, f) for f in codewords)
        M_actual = sum(1 for f in codewords if hamming_dist(f, c_eval) <= w)

        if min_d >= w:
            M_far_dist[M_alg] += 1
            if M_alg > max_M_far:
                max_M_far = M_alg
                max_M_far_synd = list(c_synd)
        else:
            M_near_dist[M_actual] += 1

        if M_actual > max_M_overall:
            max_M_overall = M_actual
            max_M_overall_synd = list(c_synd)

        checked += 1
        if checked % 50000 == 0:
            print(f"  ... checked {checked}/{n_check}, max_M_far={max_M_far}, max_M_actual={max_M_overall}")

    N = len(sigma_tuples)
    expected = N / p**conds

    print(f"\n  Mode: {mode} ({n_check} syndromes)")
    print(f"  N/p^c = {expected:.2f}")
    print(f"\n  FAR centers (d ≥ w): M_alg = M_actual")
    print(f"    Count: {sum(M_far_dist.values())}")
    print(f"    Max M_alg = {max_M_far}")
    print(f"    Distribution: {M_far_dist.most_common(10)}")
    if max_M_far_synd:
        print(f"    Achieving syndrome: {max_M_far_synd}")

    print(f"\n  NEAR centers (d < w): M_actual (not M_alg)")
    print(f"    Count: {sum(M_near_dist.values())}")
    print(f"    Max M_actual = {max(M_near_dist.keys()) if M_near_dist else 0}")
    print(f"    Distribution: {M_near_dist.most_common(10)}")

    print(f"\n  OVERALL max M_actual = {max_M_overall}")
    if max_M_overall_synd:
        print(f"    Achieving syndrome: {max_M_overall_synd}")

    return max_M_far, max_M_overall

def experiment_4_concentration(n, k, w, p, omega, sigma_tuples, L, codewords, n_trials=50000):
    """E4: Is M_alg concentrated around N/p^c for far centers?"""
    conds = n - k - w
    N = len(sigma_tuples)
    expected = N / p**conds

    print(f"\n=== E4: Concentration of M_alg for far centers ===")
    print(f"  Expected M = N/p^c = {expected:.2f}")

    M_vals = []
    for _ in range(n_trials):
        c_synd = [random.randint(0, p-1) for _ in range(n - k)]
        # Skip trivial
        if all(c == 0 for c in c_synd):
            continue

        A, b = toeplitz_matrix(n, k, w, c_synd, p)
        M = count_on_affine_fast(sigma_tuples, A, b, p, w)

        # Quick check: is this a far center?
        c_coeffs = [0]*k + list(c_synd)
        c_eval = tuple(eval_poly(c_coeffs, x, p) for x in L)

        # Fast check: just check if M might be overcounted
        # If M > N/p^c * 5, it's likely overcounting from a near codeword
        M_vals.append(M)

    print(f"  Sampled {len(M_vals)} non-trivial centers")
    print(f"  M distribution: {Counter(M_vals).most_common(15)}")
    print(f"  avg={sum(M_vals)/len(M_vals):.2f}, max={max(M_vals)}")

    # Moments
    mean = sum(M_vals) / len(M_vals)
    var = sum((m - mean)**2 for m in M_vals) / len(M_vals)
    print(f"  mean={mean:.3f}, var={var:.3f}, var/mean={var/max(mean,0.001):.3f}")
    print(f"  If Poisson: expect var/mean ≈ 1")

    # Tail probabilities
    for threshold in [2, 3, 5, 8, 10]:
        frac = sum(1 for m in M_vals if m >= threshold) / len(M_vals)
        if expected > 0:
            poisson_tail = 1  # rough
            for i in range(threshold):
                poisson_tail -= (expected**i / factorial(i)) * (2.718**(-expected))
            poisson_tail = max(poisson_tail, 0)
        else:
            poisson_tail = 0
        print(f"  P(M ≥ {threshold}) = {frac:.5f} (Poisson: ~{poisson_tail:.5f})")

def factorial(n):
    r = 1
    for i in range(2, n+1):
        r *= i
    return r

def main():
    test_cases = [
        (10, 5, 3, 11),   # conds=2, manageable
        (8, 4, 3, 17),    # conds=1
        (12, 6, 4, 13),   # conds=2, p^k too large for codeword enum
    ]

    for n, k, w, p in test_cases:
        omega = find_omega(p, n)
        conds = n - k - w
        L = [pow(omega, i, p) for i in range(n)]

        print(f"\n{'='*70}")
        print(f"n={n}, k={k}, w={w}, p={p}, conds={conds}")
        print(f"{'='*70}")

        all_sigma = [(B, elem_sym(B, omega, p)) for B in itertools.combinations(range(n), w)]
        sigma_tuples = [s for _, s in all_sigma]
        N = len(sigma_tuples)
        print(f"N = {N}, N/p^c = {N/p**conds:.2f}")

        if p**k <= 200000:
            codewords, _ = precompute_codewords(n, k, p, omega)
            print(f"Precomputed {len(codewords)} codewords")

            experiment_1_case1(n, k, w, p, omega, codewords, L)
            experiment_2_case2(n, k, w, p, omega, codewords, all_sigma, sigma_tuples, L)
            experiment_3_toeplitz_nontrivial(n, k, w, p, omega, codewords, sigma_tuples, L)
        else:
            print(f"p^k = {p**k} too large for codeword enumeration")
            print(f"Running M_alg analysis only")

        experiment_4_concentration(n, k, w, p, omega, sigma_tuples, L,
                                   codewords if p**k <= 200000 else None)

if __name__ == '__main__':
    main()
