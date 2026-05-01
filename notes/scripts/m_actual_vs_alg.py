"""
M_actual vs M_alg: separate overcounting from genuine list size.

M_alg = # degree-w error-locators with all roots in L, compatible with syndrome
M_actual = # distinct codewords within distance w of center

The overcounting: a codeword at distance d < w contributes C(n-d, w-d) to M_alg.

Strategy: for each syndrome s, find all codewords f at distance ≤ w by:
  1. Enumerate all f ∈ RS_k (for small p^k)
  2. Compute d(f, c) for a center c with syndrome s
  3. M_actual = #{f : d(f,c) ≤ w}

We also compute M_alg via the σ-image intersection for comparison.
"""

import numpy as np
from math import comb
from itertools import combinations
import time

def find_primitive_root(p):
    for g in range(2, p):
        seen = set()
        x = 1
        for i in range(1, p):
            x = x * g % p
            seen.add(x)
            if x == 1 and i < p-1:
                break
        if len(seen) == p-1:
            return g
    return None

def get_subgroup(p, n):
    if (p-1) % n != 0:
        return None
    g = find_primitive_root(p)
    omega = pow(g, (p-1)//n, p)
    return [pow(omega, i, p) for i in range(n)]

def rs_evaluate(coeffs, L, p):
    """Evaluate polynomial with coefficients coeffs at all points of L."""
    vals = []
    for x in L:
        v = 0
        xp = 1
        for c in coeffs:
            v = (v + c * xp) % p
            xp = xp * x % p
        vals.append(v)
    return tuple(vals)

def hamming_dist(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)

def build_sigma_image(L, w, p):
    """Build σ-image."""
    N = comb(len(L), w)
    sigma_list = []
    subsets = []
    for B in combinations(range(len(L)), w):  # indices into L
        elems = tuple(L[i] for i in B)
        e = [0] * (w + 1)
        e[0] = 1
        for x in elems:
            for j in range(w, 0, -1):
                e[j] = (e[j] + e[j-1] * x) % p
        sigma_list.append(tuple(e[1:]))
        subsets.append(B)
    return sigma_list, subsets

def build_toeplitz_check(syndrome, w, p):
    """Build Toeplitz matrix and vector for checking σ-compatibility."""
    nk = len(syndrome)
    c = nk - w
    if c <= 0:
        return None, None

    T = np.zeros((c, w), dtype=np.int64)
    b = np.zeros(c, dtype=np.int64)

    for ell in range(c):
        for j in range(1, w + 1):
            idx = w + ell - j
            if 0 <= idx < nk:
                sign = pow(-1, j, p)
                T[ell, j-1] = (sign * syndrome[idx]) % p
        rhs_idx = w + ell
        b[ell] = (-syndrome[rhs_idx]) % p if rhs_idx < nk else 0
    return T, b

def compute_M_alg(sigma_list, syndrome, w, p):
    """Count M_alg = # σ-image points on Toeplitz flat."""
    T, b = build_toeplitz_check(syndrome, w, p)
    if T is None:
        return len(sigma_list)  # no conditions

    count = 0
    matching_indices = []
    for i, sigma in enumerate(sigma_list):
        s_arr = np.array(sigma, dtype=np.int64)
        check = (T @ s_arr) % p
        if np.array_equal(check, b):
            count += 1
            matching_indices.append(i)
    return count, matching_indices

def compute_syndrome(center, L, k, p):
    """Compute syndrome of center: s_j = Σ c(ω^i) (ω^i)^j for j=k,...,n-1."""
    n = len(L)
    nk = n - k
    syndrome = []
    for j in range(k, n):
        s_j = 0
        for i in range(n):
            s_j = (s_j + center[i] * pow(L[i], j, p)) % p
        syndrome.append(s_j)
    return syndrome

def run_experiment(n, k, p, w, n_centers=500):
    """Run M_actual vs M_alg comparison."""
    L = get_subgroup(p, n)
    if L is None:
        print(f"  No subgroup of order {n} in F_{p}*")
        return

    c = n - k - w
    d = w - c
    if c <= 0 or d <= 0:
        print(f"  Invalid: c={c}, d={d}")
        return

    print(f"\n{'='*70}")
    print(f"n={n}, k={k}, p={p}, w={w}, c={c}, d={d}")
    print(f"C(n,w)={comb(n,w)}, C(n,d)/C(w,d)={comb(n,d)/comb(w,d):.1f}, "
          f"Bézout={(n-w+1)**d}")
    print(f"density={comb(n,w)/p**c:.4f}")
    print(f"{'='*70}")

    # Build σ-image
    sigma_list, subsets = build_sigma_image(L, w, p)
    N = len(sigma_list)
    print(f"|σ-image| = {N}")

    # Enumerate ALL RS codewords
    t0 = time.time()
    n_codewords = p ** k
    print(f"Enumerating {n_codewords} RS codewords...", end=" ", flush=True)

    codewords = []
    for val in range(n_codewords):
        coeffs = []
        v = val
        for _ in range(k):
            coeffs.append(v % p)
            v //= p
        cw = rs_evaluate(coeffs, L, p)
        codewords.append(cw)

    print(f"done ({time.time()-t0:.1f}s)")

    # For each center (random sample): compute M_actual and M_alg
    rng = np.random.RandomState(42)

    max_M_actual = 0
    max_M_alg = 0
    max_actual_center = None

    results = []

    print(f"Testing {n_centers} random centers...")
    t0 = time.time()

    for trial in range(n_centers):
        # Random center
        center = tuple(rng.randint(0, p, size=n))

        # M_actual: count codewords within distance w
        M_actual = 0
        close_codewords = []
        for cw in codewords:
            dist = hamming_dist(center, cw)
            if dist <= w:
                M_actual += 1
                close_codewords.append((dist, cw))

        # Compute syndrome
        syndrome = compute_syndrome(list(center), L, k, p)

        # M_alg: count σ-image points on Toeplitz flat
        result = compute_M_alg(sigma_list, syndrome, w, p)
        if isinstance(result, tuple):
            M_alg, matching_idx = result
        else:
            M_alg = result
            matching_idx = []

        results.append((M_actual, M_alg))

        if M_actual > max_M_actual:
            max_M_actual = M_actual
            max_actual_center = center
            max_actual_info = close_codewords

        if M_alg > max_M_alg:
            max_M_alg = M_alg

    elapsed = time.time() - t0
    print(f"Done ({elapsed:.1f}s, {n_centers/elapsed:.0f} centers/s)")

    # Also test: exhaustive over all syndromes (for small cases)
    if p ** (n-k) <= 50000:
        print(f"\nExhaustive over all {p**(n-k)} syndromes for max M_alg...")
        sigma_arr = np.array(sigma_list, dtype=np.int64)
        exhaustive_max_alg = 0
        for val in range(p**(n-k)):
            syn = []
            v = val
            for _ in range(n-k):
                syn.append(v % p)
                v //= p
            T, b = build_toeplitz_check(syn, w, p)
            if T is None:
                continue
            product = (T @ sigma_arr.T) % p
            matches = np.all(product == b.reshape(-1,1), axis=0)
            M = int(np.sum(matches))
            if M > exhaustive_max_alg:
                exhaustive_max_alg = M
        print(f"Exhaustive max M_alg = {exhaustive_max_alg}")
        max_M_alg = max(max_M_alg, exhaustive_max_alg)

    # Also do exhaustive M_actual for ALL centers (if feasible)
    if p**n <= 500000:
        print(f"\nExhaustive M_actual over all {p**n} centers...")
        exhaustive_max_actual = 0
        for val in range(p**n):
            center = []
            v = val
            for _ in range(n):
                center.append(v % p)
                v //= p
            center = tuple(center)
            M_actual = sum(1 for cw in codewords if hamming_dist(center, cw) <= w)
            if M_actual > exhaustive_max_actual:
                exhaustive_max_actual = M_actual
        print(f"Exhaustive max M_actual = {exhaustive_max_actual}")
        max_M_actual = max(max_M_actual, exhaustive_max_actual)

    # Summary
    incidence = comb(n, d) / comb(w, d)
    print(f"\n{'='*50}")
    print(f"RESULTS for n={n}, k={k}, p={p}, w={w} (c={c}, d={d})")
    print(f"{'='*50}")
    print(f"  max M_actual  = {max_M_actual}")
    print(f"  max M_alg     = {max_M_alg}")
    print(f"  overcounting  = {max_M_alg / max(max_M_actual,1):.1f}x")
    print(f"  C(n,d)/C(w,d) = {incidence:.1f}")
    print(f"  Bézout        = {(n-w+1)**d}")
    print(f"  density       = {comb(n,w)/p**c:.4f}")
    print(f"  actual ≤ inci = {'✓' if max_M_actual <= incidence else '✗'}")
    print(f"  alg ≤ inci    = {'✓' if max_M_alg <= incidence else '✗'}")

    # Distribution
    M_act_dist = {}
    M_alg_dist = {}
    for ma, ml in results:
        M_act_dist[ma] = M_act_dist.get(ma, 0) + 1
        M_alg_dist[ml] = M_alg_dist.get(ml, 0) + 1

    print(f"\nM_actual distribution (from {n_centers} random centers):")
    for m in sorted(M_act_dist.keys()):
        pct = 100 * M_act_dist[m] / n_centers
        print(f"  M_actual={m}: {M_act_dist[m]:>5} ({pct:>5.1f}%)")

    if max_actual_center is not None:
        print(f"\nWorst-case center (M_actual={max_M_actual}):")
        for dist, cw in max_actual_info[:5]:
            print(f"  f at dist {dist}: {cw[:6]}...")

    return {
        'n': n, 'k': k, 'p': p, 'w': w, 'c': c, 'd': d,
        'max_actual': max_M_actual, 'max_alg': max_M_alg,
        'incidence': incidence, 'bezout': (n-w+1)**d,
        'density': comb(n,w)/p**c
    }

def main():
    print("=" * 70)
    print("M_actual vs M_alg: Overcounting Analysis")
    print("=" * 70)

    # Test cases — keep p^k small enough to enumerate codewords
    test_cases = [
        # (n, k, p, w)
        (10, 5, 11, 3),   # c=2, d=1, p^k=161K
        (10, 5, 11, 4),   # c=1, d=3, p^k=161K
        (8, 4, 17, 3),    # c=1, d=2, p^k=83K
        (10, 4, 11, 4),   # c=2, d=2, p^k=14K
        (12, 6, 13, 4),   # c=2, d=2, p^k=4.8M  — might be slow
        (10, 3, 11, 4),   # c=3, d=1, p^k=1331
        (14, 7, 29, 5),   # c=2, d=3, p^k=17B — TOO LARGE
    ]

    # Filter feasible cases
    feasible = []
    for n, k, p, w in test_cases:
        c = n - k - w
        d = w - c
        if c <= 0 or d <= 0:
            continue
        if (p-1) % n != 0:
            continue
        if p**k > 5_000_000:
            print(f"Skipping n={n},k={k},p={p}: p^k={p**k} too large")
            continue
        feasible.append((n, k, p, w))

    all_results = []
    for n, k, p, w in feasible:
        res = run_experiment(n, k, p, w)
        if res:
            all_results.append(res)

    # Summary table
    print(f"\n\n{'='*80}")
    print("SUMMARY: M_actual vs M_alg vs Incidence Bound")
    print(f"{'='*80}")
    hdr = f"{'n':>3} {'k':>3} {'p':>3} {'w':>3} {'c':>2} {'d':>2} " \
          f"{'M_act':>5} {'M_alg':>5} {'ratio':>5} {'incid':>6} " \
          f"{'act≤inc':>7}"
    print(hdr)
    print("-" * 70)
    for r in all_results:
        ratio = r['max_alg'] / max(r['max_actual'], 1)
        ok = "✓" if r['max_actual'] <= r['incidence'] else "✗"
        print(f"{r['n']:>3} {r['k']:>3} {r['p']:>3} {r['w']:>3} "
              f"{r['c']:>2} {r['d']:>2} "
              f"{r['max_actual']:>5} {r['max_alg']:>5} {ratio:>5.1f} "
              f"{r['incidence']:>6.1f} {ok:>7}")

if __name__ == "__main__":
    main()
