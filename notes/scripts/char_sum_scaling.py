#!/usr/bin/env python3
"""
Character sum scaling analysis.

Key question: how does max|S(α)| / N scale with n and p?

For M = O(1), we need: max|S(α)| = O(p^c) (which is trivially ≤ N for fixed n).

But the interesting regime is: for FIXED n, how does max|S(α)|/N behave as p grows?
And for GROWING n at fixed rate, what happens?

Also: decompose S(α) into its components when α has specific structure.
"""

import math
import cmath
from itertools import combinations, product
import random

PI2 = 2 * math.pi


def find_primitive_root(p):
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
    for g in range(2, p):
        if all(pow(g, (p - 1) // q, p) != 1 for q in factors):
            return g


def find_omega(n, p):
    g = find_primitive_root(p)
    return pow(g, (p - 1) // n, p)


def elem_sym(roots, p):
    w = len(roots)
    e = [0] * (w + 1)
    e[0] = 1
    for r in roots:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j - 1] * r) % p
    return e


def primes_cong_1(n, count=5):
    result = []
    pp = n + 1
    while len(result) < count:
        if pp % n == 1:
            is_prime = pp > 1
            for d in range(2, int(pp ** 0.5) + 1):
                if pp % d == 0:
                    is_prime = False
                    break
            if is_prime:
                result.append(pp)
        pp += 1
    return result


def johnson_radius(n, k):
    return math.ceil((1 - math.sqrt(k / n)) * n)


def psi(x, p):
    return cmath.exp(1j * PI2 * (x % p) / p)


def compute_S_alpha(n, k, p, w, alpha):
    """
    Compute S(α) = Σ_B ψ(Σ_j α_j σ_j(B)) exactly.
    alpha = (α_1, ..., α_w).
    """
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    S = 0j
    for B in combinations(range(n), w):
        roots = [L[i] for i in B]
        es = elem_sym(roots, p)
        arg = sum(alpha[j] * es[j + 1] for j in range(w)) % p
        S += psi(arg, p)
    return S


def char_sum_stats(n, k, p, w, c_high):
    """
    Compute M via character sum and return key statistics.
    """
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    nk = n - k
    conds = n - k - w
    N = math.comb(n, w)

    # Precompute D values
    all_B = list(combinations(range(n), w))
    D_values = []
    for B in all_B:
        roots = [L[i] for i in B]
        es = elem_sym(roots, p)
        d_row = []
        for m_off in range(conds):
            val = 0
            for j in range(w + 1):
                c_idx = m_off + j
                if c_idx < nk:
                    val += pow(-1, j, p) * es[j] * c_high[c_idx]
            d_row.append(val % p)
        D_values.append(d_row)

    # Compute S(t) for all t, track statistics
    total = complex(N, 0)  # t=0 contribution
    S_mags = []
    max_S = 0
    sum_S2 = 0  # Σ|S|^2 (Parseval-like)

    for t in product(range(p), repeat=conds):
        if all(ti == 0 for ti in t):
            continue
        St = 0j
        for b_idx in range(N):
            arg = sum(t[m] * D_values[b_idx][m] for m in range(conds)) % p
            St += psi(arg, p)
        mag = abs(St)
        total += St
        S_mags.append(mag)
        max_S = max(max_S, mag)
        sum_S2 += mag * mag

    M = total.real / p ** conds

    # Parseval identity: Σ_{t≠0} |S(t)|^2 should equal p^c · N - N^2/p^c... no
    # Actually: Σ_{all t} |S(t)|^2 = p^c · |{(B1,B2): σ(B1) = σ(B2)}|
    # (by Parseval for finite abelian groups)
    # If σ is injective: Σ|S|^2 = p^c · N
    # Including t=0: N^2 + Σ_{t≠0}|S(t)|^2 = p^c · N (if σ injective)
    # So Σ_{t≠0}|S(t)|^2 = p^c · N - N^2

    parseval_rhs = p ** conds * N - N ** 2
    parseval_check = sum_S2

    avg_S2 = sum_S2 / (p ** conds - 1)
    avg_S = sum(S_mags) / len(S_mags) if S_mags else 0

    return {
        'M': M,
        'N': N,
        'p': p,
        'pc': p ** conds,
        'conds': conds,
        'max_S': max_S,
        'avg_S': avg_S,
        'avg_S2': avg_S2,
        'rms_S': math.sqrt(avg_S2),
        'parseval_lhs': parseval_check,
        'parseval_rhs': parseval_rhs,
        'max_ratio': max_S / N,
        'rms_ratio': math.sqrt(avg_S2) / N,
    }


def find_optimal_center(n, k, p, w, max_trials=5000):
    """Find center with maximum M."""
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    nk = n - k
    conds = n - k - w

    all_B = list(combinations(range(n), w))
    all_sigma = []
    for B in all_B:
        roots = [L[i] for i in B]
        all_sigma.append(elem_sym(roots, p))

    best_M = 0
    best_c = None

    for _ in range(max_trials):
        c_high = [random.randint(0, p - 1) for _ in range(nk)]

        # Count compatible B's (M_alg)
        cnt = 0
        for b_idx, es in enumerate(all_sigma):
            ok = True
            for m_off in range(conds):
                val = 0
                for j in range(w + 1):
                    c_idx = m_off + j
                    if c_idx < nk:
                        val += pow(-1, j, p) * es[j] * c_high[c_idx]
                if val % p != 0:
                    ok = False
                    break
            if ok:
                cnt += 1

        if cnt > best_M:
            best_M = cnt
            best_c = c_high[:]

    return best_M, best_c


# ========== Analysis ==========
print("=" * 70)
print("CHARACTER SUM SCALING ANALYSIS")
print("=" * 70)

# Table: for each (n, p), report max|S|/N, rms|S|/N, Parseval check
results = []

for n in [6, 8, 10]:
    k = n // 2
    w = johnson_radius(n, k)
    conds = n - k - w
    ps = primes_cong_1(n, 4)

    for p in ps:
        N = math.comb(n, w)
        pc = p ** conds

        # Skip if too expensive
        if pc > 50000 or N > 2000:
            continue

        print(f"\nn={n}, k={k}, w={w}, conds={conds}, p={p}, N={N}, p^c={pc}")

        # Find optimal center
        M_alg, c_opt = find_optimal_center(n, k, p, w, max_trials=3000)
        if c_opt is None:
            print("  No center found")
            continue

        print(f"  Optimal center: M_alg={M_alg}, c_high={c_opt}")

        # Character sum analysis
        stats = char_sum_stats(n, k, p, w, c_opt)

        print(f"  M_char = {stats['M']:.4f}")
        print(f"  max|S|/N = {stats['max_ratio']:.4f}")
        print(f"  rms|S|/N = {stats['rms_ratio']:.4f}")
        print(f"  max|S|   = {stats['max_S']:.2f}")
        print(f"  rms|S|   = {stats['rms_S']:.2f}")
        print(f"  N/p^c    = {N/pc:.4f}")
        print(f"  Parseval: {stats['parseval_lhs']:.1f} vs {stats['parseval_rhs']:.1f} "
              f"({'OK' if abs(stats['parseval_lhs'] - stats['parseval_rhs']) < 1 else 'FAIL'})")

        # Key ratio: max|S| vs sqrt(p^c * N) (the "square root cancellation" prediction)
        sqrt_bound = math.sqrt(pc * N)
        print(f"  √(p^c·N) = {sqrt_bound:.2f}, max|S|/√(p^c·N) = {stats['max_S']/sqrt_bound:.4f}")

        results.append({
            'n': n, 'k': k, 'w': w, 'conds': conds, 'p': p,
            'N': N, 'pc': pc, 'M': stats['M'],
            'max_S': stats['max_S'], 'rms_S': stats['rms_S'],
            'max_ratio': stats['max_ratio'],
            'sqrt_ratio': stats['max_S'] / sqrt_bound,
        })

# Summary table
print("\n\n" + "=" * 70)
print("SUMMARY TABLE")
print("=" * 70)
print(f"{'n':>3} {'k':>3} {'w':>3} {'c':>3} {'p':>5} {'N':>6} {'p^c':>7} {'M':>5} "
      f"{'max|S|':>8} {'max/N':>7} {'max/√NP':>8}")
print("-" * 70)
for r in results:
    print(f"{r['n']:3d} {r['k']:3d} {r['w']:3d} {r['conds']:3d} {r['p']:5d} "
          f"{r['N']:6d} {r['pc']:7d} {r['M']:5.1f} "
          f"{r['max_S']:8.2f} {r['max_ratio']:7.4f} {r['sqrt_ratio']:8.4f}")

# ========== Special analysis: σ_w-only character sum ==========
print("\n\n" + "=" * 70)
print("σ_w-ONLY CHARACTER SUM (single-variable)")
print("=" * 70)
print("Theory: |S(0,...,0,α_w)| = (N/n)|Σ_{x∈L} ψ(α_w x)| when gcd(w,n)=1")
print()

for n in [6, 8, 10, 12]:
    k = n // 2
    w = johnson_radius(n, k)
    N = math.comb(n, w)
    ps = primes_cong_1(n, 3)

    for p in ps[:2]:
        if N > 5000:
            continue
        omega = find_omega(n, p)
        L = [pow(omega, i, p) for i in range(n)]

        # Compute S(0,...,0,α_w) for all α_w ∈ F_p*
        max_S_w = 0
        for alpha_w in range(1, p):
            S = compute_S_alpha(n, k, p, w, [0] * (w - 1) + [alpha_w])
            mag = abs(S)
            max_S_w = max(max_S_w, mag)

        # Compute |Σ_{x∈L} ψ(αx)| for comparison
        max_L_sum = 0
        for alpha in range(1, p):
            Lsum = sum(psi(alpha * x, p) for x in L)
            max_L_sum = max(max_L_sum, abs(Lsum))

        predicted = N / n * max_L_sum
        gcd_wn = math.gcd(w, n)

        print(f"n={n}, k={k}, w={w}, p={p}: gcd(w,n)={gcd_wn}")
        print(f"  max|S_w|  = {max_S_w:.4f}")
        print(f"  N/n·max|L| = {predicted:.4f}  {'MATCH' if abs(max_S_w - predicted) < 0.1 else 'DIFF'}")
        print(f"  max|Σ ψ(αx)| = {max_L_sum:.4f}")
        print(f"  Gauss bound: (n-1)√p/n · n/(p-1) ≈ {(n-1)*math.sqrt(p)/(p-1):.4f}")
        print()
