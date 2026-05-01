#!/usr/bin/env python3
"""
Convolutional Anti-Alignment — Step 3: Exhaustive Toeplitz analysis.

Key insight from Step 2: Toeplitz matrix A(c) is parameterized by n-k syndrome
coefficients, a MUCH smaller space than general conds × w matrices.

For n=10/p=11: 5 syndrome coefficients → 11^5 = 161051 subspaces.
We can exhaustively find max M_alg over ALL Toeplitz subspaces.

Experiments:
  E1. Exhaustive max M_alg over all Toeplitz subspaces (n=10)
  E2. Compare with max M_alg over all general subspaces (n=10)
  E3. Characterize the Toeplitz subspaces achieving max M_alg
  E4. M_actual for max-M_alg Toeplitz centers (via codeword enumeration)
  E5. Scaling: how does max M_alg(Toeplitz) grow with (n, p)?
"""

import itertools
import random
from collections import Counter, defaultdict

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

def make_inv(p):
    inv = [0] * p
    for a in range(1, p):
        inv[a] = pow(a, p-2, p)
    return inv

def elem_sym(B, omega, p):
    roots = [pow(omega, i, p) for i in B]
    w = len(roots)
    e = [0] * (w + 1)
    e[0] = 1
    for r in roots:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j-1] * r) % p
    return tuple(e[1:])

def compute_all_sigma(n, w, p, omega):
    results = []
    for B in itertools.combinations(range(n), w):
        sig = elem_sym(B, omega, p)
        results.append((B, sig))
    return results

def toeplitz_matrix(n, k, w, c_synd, p):
    """
    Build RS coefficient matrix from syndrome coefficients.
    c_synd = (c_k, c_{k+1}, ..., c_{n-1}), length n-k.

    Condition for m = k+w+r (r = 0,...,conds-1):
    Σ_{j=0}^{w} (-1)^j σ_j c_{m-w+j} = 0
    => Σ_{j=1}^{w} (-1)^j c_{m-w+j} σ_j = -c_{m-w}

    A[r, j-1] = (-1)^j c_{m-w+j} = (-1)^j c_{k+r+j}
    b[r] = -c_{m-w} = -c_{k+r}

    where c_{k+i} = c_synd[i].
    """
    conds = n - k - w
    A = []
    b = []
    for r in range(conds):
        row = []
        for j in range(1, w + 1):
            idx = r + j  # index into c_synd
            if idx < len(c_synd):
                coeff = ((-1)**j * c_synd[idx]) % p
            else:
                coeff = 0
            row.append(coeff)
        A.append(row)
        b.append((-c_synd[r]) % p)
    return A, b

def count_on_affine_fast(sigma_list, A_mat, b_vec, p):
    """Count σ-images on affine subspace Ax = b. Optimized."""
    conds = len(A_mat)
    count = 0
    for sig in sigma_list:
        ok = True
        for i in range(conds):
            val = 0
            for j in range(len(sig)):
                val += A_mat[i][j] * sig[j]
            if val % p != b_vec[i]:
                ok = False
                break
        if ok:
            count += 1
    return count

def experiment_1_exhaustive_toeplitz(n, k, w, p, omega, sigma_tuples):
    """E1: Exhaustive search over all Toeplitz subspaces."""
    conds = n - k - w
    n_synd = n - k
    total = p**n_synd

    print(f"\n=== E1: Exhaustive Toeplitz search ===")
    print(f"  n-k = {n_synd} syndrome coefficients, {total} total subspaces")

    max_M = 0
    max_c = None
    M_dist = Counter()
    checked = 0

    for idx in range(total):
        c_synd = []
        tmp = idx
        for _ in range(n_synd):
            c_synd.append(tmp % p)
            tmp //= p

        A, b = toeplitz_matrix(n, k, w, c_synd, p)

        # Check if A has full rank (otherwise trivial)
        # Actually just compute M
        M = count_on_affine_fast(sigma_tuples, A, b, p)
        M_dist[M] += 1

        if M > max_M:
            max_M = M
            max_c = list(c_synd)
            print(f"  New max M={M} at c_synd={c_synd}, A={A}, b={b}")

        checked += 1
        if checked % 50000 == 0:
            print(f"  ... checked {checked}/{total}, current max={max_M}")

    print(f"\n  RESULT: max M_alg over ALL Toeplitz subspaces = {max_M}")
    print(f"  Achieving syndrome: {max_c}")
    print(f"  Distribution: {M_dist.most_common(15)}")

    # Statistics
    N = len(sigma_tuples)
    expected = N / p**conds
    print(f"  Expected M = N/p^c = {expected:.2f}")
    print(f"  Max/Expected = {max_M/expected:.2f}")
    print(f"  Fraction with M > 2*expected: {sum(v for k,v in M_dist.items() if k > 2*expected)/total:.4f}")

    return max_M, max_c, M_dist

def experiment_2_exhaustive_general(n, k, w, p, omega, sigma_tuples, n_sample=100000):
    """E2: Sample max M_alg over general codim-c subspaces."""
    conds = n - k - w
    print(f"\n=== E2: Random general subspaces (sample {n_sample}) ===")

    max_M = 0
    M_dist = Counter()

    for _ in range(n_sample):
        A = [[random.randint(0, p-1) for _ in range(w)] for _ in range(conds)]
        b = [random.randint(0, p-1) for _ in range(conds)]
        M = count_on_affine_fast(sigma_tuples, A, b, p)
        M_dist[M] += 1
        if M > max_M:
            max_M = M

    N = len(sigma_tuples)
    expected = N / p**conds
    print(f"  Max M_alg (sample) = {max_M}")
    print(f"  Distribution: {M_dist.most_common(15)}")
    print(f"  Max/Expected = {max_M/expected:.2f}")

    return max_M, M_dist

def experiment_3_analyze_max(n, k, w, p, omega, sigma_tuples, all_sigma, max_c):
    """E3: Analyze the maximum-M Toeplitz subspace."""
    conds = n - k - w
    print(f"\n=== E3: Analysis of max-M Toeplitz subspace ===")

    A, b = toeplitz_matrix(n, k, w, max_c, p)
    print(f"  A = {A}")
    print(f"  b = {b}")

    # Which B's are compatible?
    hits = []
    for B, sig in all_sigma:
        ok = True
        for i in range(conds):
            val = sum(A[i][j] * sig[j] for j in range(w)) % p
            if val != b[i]:
                ok = False
                break
        if ok:
            hits.append((B, sig))

    print(f"  Compatible B's: {len(hits)}")
    for B, sig in hits:
        print(f"    B={B}, σ={sig}")

    # Are these B's at pairwise distance d_min?
    if len(hits) > 1:
        print(f"\n  Pairwise distances:")
        for i in range(len(hits)):
            for j in range(i+1, len(hits)):
                B1 = set(hits[i][0])
                B2 = set(hits[j][0])
                sym_diff = len(B1.symmetric_difference(B2))
                print(f"    d(B_{i}, B_{j}) = {sym_diff}")

    # Check: which σ_w fibers do they come from?
    print(f"\n  σ_w values of compatible B's:")
    sw_vals = [sig[w-1] for _, sig in hits]
    print(f"    {Counter(sw_vals)}")

    # Check the Toeplitz matrix structure
    print(f"\n  Toeplitz structure:")
    print(f"    Syndrome c_{k}..c_{n-1} = {max_c}")
    print(f"    σ_1 coefficients: {[A[r][0] for r in range(conds)]}")
    print(f"    σ_w coefficients: {[A[r][w-1] for r in range(conds)]}")

def experiment_4_Mactual_at_max(n, k, w, p, omega, max_c, all_sigma):
    """E4: Compute M_actual for the center achieving max M_alg."""
    print(f"\n=== E4: M_actual for max-M_alg center ===")

    if p**k > 200000:
        print(f"  SKIP: p^k = {p**k} too large")
        return

    L = [pow(omega, i, p) for i in range(n)]

    def eval_poly(coeffs, x, p):
        val = 0
        for c in reversed(coeffs):
            val = (val * x + c) % p
        return val

    # Reconstruct center evaluation from syndrome
    # c(x) = Σ c_j x^j, we need c(ω^i) for i=0,...,n-1
    # But c_synd only gives c_k,...,c_{n-1}. We can choose c_0,...,c_{k-1} freely.
    # For M_actual, the RS part of c doesn't matter (it shifts f by a constant codeword).
    # So set c_0=...=c_{k-1}=0.
    c_coeffs = [0]*k + list(max_c)
    c_eval = [eval_poly(c_coeffs, x, p) for x in L]

    # Find all codewords within distance w
    count = 0
    close_codewords = []
    for idx in range(p**k):
        coeffs = []
        tmp = idx
        for _ in range(k):
            coeffs.append(tmp % p)
            tmp //= p
        f_eval = [eval_poly(coeffs, x, p) for x in L]
        d = sum(1 for i in range(n) if f_eval[i] != c_eval[i])
        if d <= w:
            count += 1
            close_codewords.append((tuple(coeffs), d))

    print(f"  M_actual = {count}")
    for coeffs, d in close_codewords:
        print(f"    f = {coeffs}, distance = {d}")

    # Also compute M_alg for verification
    A, b = toeplitz_matrix(n, k, w, max_c, p)
    M_alg = count_on_affine_fast([s for _, s in all_sigma], A, b, p)
    print(f"  M_alg = {M_alg}")
    print(f"  Overcounting ratio = {M_alg/max(count,1):.1f}")

def experiment_5_scaling(omega_finder=find_omega):
    """E5: How does max M_alg(Toeplitz) scale with n, p?"""
    print(f"\n=== E5: Scaling of max M_alg(Toeplitz) ===")

    # We need cases where p^{n-k} is manageable for exhaustive search
    # or sample if too large
    test_cases = [
        # (n, k, w, p)
        (6, 3, 2, 7),     # conds=1, p^{n-k}=7^3=343
        (8, 4, 3, 17),    # conds=1, p^{n-k}=17^4=83521
        (10, 5, 3, 11),   # conds=2, p^{n-k}=11^5=161051
        (10, 5, 3, 31),   # conds=2, p^{n-k}=31^5=~29M → sample
        (12, 6, 4, 13),   # conds=2, p^{n-k}=13^6=~5M → sample
    ]

    results = []
    for n, k, w, p in test_cases:
        omega = omega_finder(p, n)
        conds = n - k - w
        n_synd = n - k
        total = p**n_synd
        N = 1
        for i in range(w):
            N = N * (n - i) // (i + 1)

        print(f"\n  n={n}, k={k}, w={w}, p={p}: conds={conds}, N={N}, N/p^c={N/p**conds:.2f}")

        sigma_tuples = [elem_sym(B, omega, p) for B in itertools.combinations(range(n), w)]

        if total <= 200000:
            # Exhaustive
            max_M = 0
            for idx in range(total):
                c_synd = []
                tmp = idx
                for _ in range(n_synd):
                    c_synd.append(tmp % p)
                    tmp //= p
                A, b_vec = toeplitz_matrix(n, k, w, c_synd, p)
                M = count_on_affine_fast(sigma_tuples, A, b_vec, p)
                if M > max_M:
                    max_M = M
            print(f"    Exhaustive: max M_alg = {max_M} ({total} subspaces)")
        else:
            # Sample
            max_M = 0
            n_sample = min(100000, total)
            for _ in range(n_sample):
                c_synd = [random.randint(0, p-1) for _ in range(n_synd)]
                A, b_vec = toeplitz_matrix(n, k, w, c_synd, p)
                M = count_on_affine_fast(sigma_tuples, A, b_vec, p)
                if M > max_M:
                    max_M = M
            print(f"    Sample ({n_sample}): max M_alg = {max_M}")

        expected = N / p**conds
        print(f"    N/p^c = {expected:.2f}, max/expected = {max_M/max(expected,0.01):.2f}")
        results.append((n, k, w, p, conds, max_M, expected))

    # Summary table
    print(f"\n  SCALING SUMMARY:")
    print(f"  {'n':>3} {'k':>3} {'w':>3} {'p':>4} {'c':>2} {'N/p^c':>8} {'max M':>6} {'ratio':>6}")
    for n, k, w, p, c, mM, exp in results:
        print(f"  {n:3d} {k:3d} {w:3d} {p:4d} {c:2d} {exp:8.2f} {mM:6d} {mM/max(exp,0.01):6.1f}")

def main():
    # Primary analysis: n=10, p=11
    n, k, w, p = 10, 5, 3, 11
    omega = find_omega(p, n)
    conds = n - k - w

    print(f"{'='*70}")
    print(f"PRIMARY: n={n}, k={k}, w={w}, p={p}, conds={conds}")
    print(f"{'='*70}")

    all_sigma = compute_all_sigma(n, w, p, omega)
    sigma_tuples = [s for _, s in all_sigma]
    N = len(all_sigma)
    print(f"N = {N}, N/p^c = {N/p**conds:.2f}")

    max_M, max_c, toeplitz_dist = experiment_1_exhaustive_toeplitz(
        n, k, w, p, omega, sigma_tuples)

    max_M_gen, gen_dist = experiment_2_exhaustive_general(
        n, k, w, p, omega, sigma_tuples)

    if max_c:
        experiment_3_analyze_max(n, k, w, p, omega, sigma_tuples, all_sigma, max_c)
        experiment_4_Mactual_at_max(n, k, w, p, omega, max_c, all_sigma)

    experiment_5_scaling()

if __name__ == '__main__':
    main()
