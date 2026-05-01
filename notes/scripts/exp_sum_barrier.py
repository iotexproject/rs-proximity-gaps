#!/usr/bin/env python3
"""
Direction C, Round 4: Establishing the √(pN) barrier and identifying what's needed.

THE BARRIER:
All approaches to bounding |S(α)| converge to O(√(pN)):
1. Gauss + e_w decomposition: |S| ≤ (1/√p)·Σ|e_w| ≤ √p·max|e_w| ~ √(pN)
2. Multiplicative Fourier: Σ_χ |g(χ)|·|e_r(χ)| ~ √p·√N·p ~ √(pN)·√p... worse
3. Parseval rms: √N, but max|S| >> rms by factor √p

WHY THIS IS INSUFFICIENT:
M_alg = N/p^c + (1/p^c)·Σ_{t≠0} S(t)
If max|S| ≤ C√(pN): M_alg ≤ N/p^c + C√(pN) → ∞ for fixed n, growing p.

But M_actual IS bounded! The cancellation in Σ S(t) is enormous.

QUESTION: Can we exploit the cancellation in the SUM rather than bounding INDIVIDUAL terms?

APPROACH: Look at the SECOND MOMENT Σ_c M_alg(c)² to bound max M_alg.
If avg M² is small, max M can't be too large.

ALTERNATIVE: Direct polynomial method — bound the number of degree-<k polynomials
with ≥ n-w zeros on L. This doesn't go through character sums at all.
"""

import math
import cmath
from itertools import combinations, product
from collections import defaultdict

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

def psi(x, p):
    return cmath.exp(1j * PI2 * (x % p) / p)

def johnson_w_mds(n, k):
    return int(n - math.sqrt(n * (k - 1)))

def primes_1modn(n, count=10):
    result = []
    pp = n + 1
    while len(result) < count:
        if pp % n == 1:
            ok = True
            for d in range(2, int(pp**0.5) + 1):
                if pp % d == 0:
                    ok = False
                    break
            if ok:
                result.append(pp)
        pp += 1
    return result


# ========== 1: Second moment method ==========
def second_moment_method(n, k, p):
    """
    Compute E[M_alg²] = (1/p^{2(n-k)}) Σ_{c_high} M_alg(c)²

    By Parseval:
    E[M²] = (1/p^{2nk}) Σ_c [Σ_{t1,t2} S(t1)·conj(S(t2))]
    This is related to the 4th moment of σ-values.

    Direct computation for small cases.
    """
    w = johnson_w_mds(n, k)
    c = n - k - w
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    N = math.comb(n, w)
    nk = n - k

    print(f"\n{'='*70}")
    print(f"SECOND MOMENT METHOD — RS[{n},{k}], p={p}, w={w}, c={c}")
    print(f"{'='*70}")

    # Precompute all σ
    all_B = list(combinations(range(n), w))
    all_sigma = []
    for B in all_B:
        roots = [L[i] for i in B]
        all_sigma.append(elem_sym(roots, p))

    # For each center: compute M_alg
    # Center space: c_high ∈ F_p^{nk}. Total: p^{nk}.
    # For small p^{nk}: enumerate. Otherwise sample.

    total_centers = p ** nk
    if total_centers > 100000:
        print(f"  p^{{n-k}} = {total_centers} too large, sampling 10000 centers")
        import random
        M_vals = []
        for _ in range(10000):
            c_high = [random.randint(0, p-1) for _ in range(nk)]
            cnt = 0
            for es in all_sigma:
                ok = True
                for m_off in range(c):
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
            M_vals.append(cnt)
        sampled = True
    else:
        M_vals = []
        for c_high in product(range(p), repeat=nk):
            cnt = 0
            for es in all_sigma:
                ok = True
                for m_off in range(c):
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
            M_vals.append(cnt)
        sampled = False

    avg_M = sum(M_vals) / len(M_vals)
    avg_M2 = sum(m**2 for m in M_vals) / len(M_vals)
    max_M = max(M_vals)
    var_M = avg_M2 - avg_M**2

    print(f"\n  Statistics ({'sampled' if sampled else 'exhaustive'}):")
    print(f"    E[M_alg] = {avg_M:.4f}")
    print(f"    E[M_alg²] = {avg_M2:.4f}")
    print(f"    Var[M_alg] = {var_M:.4f}")
    print(f"    max M_alg = {max_M}")
    print(f"    N/p^c = {N / p**c:.4f}")
    print(f"    √Var = {math.sqrt(var_M):.4f}")

    # Markov on M²: P[M ≥ t] ≤ E[M²]/t²
    # So max M ≤ √(E[M²]) · √(1/ε) for P[M≥max] ≥ ε
    print(f"\n  Markov bound: max M ≤ √E[M²] = {math.sqrt(avg_M2):.4f} (w.p. 1/total)")

    # What does E[M²] predict?
    # E[M] = N/p^c (exactly, by uniformity of char sum)
    # E[M²] = (N/p^c)² + (something)
    # The "something" = covariance term related to pair collisions.

    # For a "random code": E[M²] = E[M]² + E[M] (Poisson approximation)
    # So Var[M] ≈ E[M] = N/p^c.
    poisson_var = N / p**c
    print(f"\n  Poisson prediction: Var ≈ E[M] = {poisson_var:.4f}")
    print(f"  Actual Var = {var_M:.4f}")
    print(f"  Ratio Var/E[M] = {var_M/avg_M:.4f}" if avg_M > 0 else "")

    # Distribution of M_alg
    M_dist = defaultdict(int)
    for m in M_vals:
        M_dist[m] += 1
    print(f"\n  M_alg distribution:")
    for m in sorted(M_dist):
        cnt = M_dist[m]
        frac = cnt / len(M_vals)
        bar = '#' * min(int(frac * 50), 50)
        print(f"    M={m:3d}: {cnt:6d} ({frac:.4f}) {bar}")


# ========== 2: Polynomial method — agreement polynomial approach ==========
def polynomial_method(n, k, p):
    """
    Direct bound on M_actual via the agreement polynomial.

    For f ∈ RS_k at distance d from center c:
    f - c = e (error poly), wt(e) = d ≤ w, deg(e) ≤ n-1.

    The agreement set A = {i : f(ω^i) = c(ω^i)} has |A| ≥ n-w.
    The agreement polynomial Λ_A(x) = Π_{i∈A}(x-ω^i) divides x^n - 1 in F_p[x].

    f - c = (error on B) = e, which can be written as e(x) = h(x) · (x^n - 1) / Λ_A(x)
    for some polynomial h of appropriate degree.

    Actually: any degree-<n polynomial with zeros at A is determined by its values on B.
    So f = c + Lagrange interpolation of error values at B positions.

    For TWO codewords f_1, f_2 at distance ≤ w from c:
    f_1 - f_2 has degree < k and ≥ n - 2w zeros (at positions where both agree with c).

    So f_1 - f_2 ∈ RS_k has ≥ n - 2w zeros ⟹ d(f_1, f_2) ≤ 2w.
    And since RS_k has min distance n-k+1: either f_1 = f_2 or d(f_1,f_2) ≥ n-k+1.

    So: n-k+1 ≤ d(f_1,f_2) ≤ 2w.
    This requires: 2w ≥ n-k+1 ⟺ w ≥ (n-k+1)/2.

    At Johnson radius w ≈ (1-√ρ)n and n-k+1 = n(1-ρ)+1:
    2w ≈ 2(1-√ρ)n vs n-k+1 ≈ (1-ρ)n+1.
    2(1-√ρ) vs (1-ρ) = (1-√ρ)(1+√ρ).
    So 2w/(n-k+1) ≈ 2/(1+√ρ). For ρ=1/2: 2/(1+0.707) = 1.17. So 2w > n-k+1 ✓.

    This means: differences f_1-f_2 have between n-k+1 and 2w zeros.
    The number of zeros constrains the factorization of f_1-f_2.
    """
    w = johnson_w_mds(n, k)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    N = math.comb(n, w)

    print(f"\n{'='*70}")
    print(f"POLYNOMIAL METHOD — RS[{n},{k}], p={p}, w={w}")
    print(f"{'='*70}")

    d_min = n - k + 1
    d_max = 2 * w

    print(f"  d_min(RS) = {d_min}")
    print(f"  2w = {d_max}")
    print(f"  Pairwise distance range: [{d_min}, {d_max}]")
    print(f"  Zero range for f_i - f_j: [{n - d_max}, {n - d_min}]")

    # Number of divisors of x^n-1 with degree in [n-2w, n-k]:
    # These are products of cyclotomic factors.
    # x^n - 1 = Π_{d|n} Φ_d(x) over F_p.

    # Actually, the zeros of f_1-f_2 on L correspond to a SUBSET of L of size ≥ n-2w.
    # The locator polynomial Λ(x) = Π_{i∈Z}(x-ω^i) must divide x^n-1.
    # This is automatic since ω^i are n-th roots of unity.

    # So any subset of L gives a valid zero set. The constraint is:
    # f_1 - f_2 has degree < k and exactly |Z| zeros ⟹ n-2w ≤ |Z| ≤ n - d_min = k-1.

    # For M codewords in the list: we have C(M,2) pairwise differences,
    # each with ≥ n-2w zeros. These zeros overlap in structured ways.

    # SUNFLOWER / DESIGN argument:
    # If all pairwise agreement sets have overlap ≥ t:
    # then the list has a "common core" of size ≥ t.
    # At Johnson radius: t ≈ n - 2w ≈ (2√ρ - 1)n (positive for ρ > 1/4).

    t_min = n - d_max  # minimum agreement between any two codewords in list
    print(f"  Minimum pairwise agreement: {t_min}")
    print(f"  (Interpretation: any two close codewords agree on ≥ {t_min} positions)")

    # How many degree-<k polynomials can have ≥ t zeros in common?
    # If f_1, f_2 share t zeros: (f_1-f_2) has ≥ t zeros among n points.
    # Since deg(f_1-f_2) < k: # zeros ≤ k-1. But ≥ t = n-2w.
    # So k-1 ≥ n-2w ⟹ w ≥ (n-k+1)/2 (already verified).

    # The key: for M codewords {f_i}, consider the PAIRWISE DIFFERENCE GRAPH:
    # Vertices = codewords, edge between f_i, f_j labeled by their agreement set.
    # Each agreement set has size ∈ [n-2w, k-1].

    # The AGREEMENT SETS are subsets of [n] of size ∈ [n-2w, k-1].
    # For each pair (i,j): A_{ij} = {m : f_i(ω^m) = f_j(ω^m)}.

    # Compute for a specific case
    if N > 5000:
        print(f"  N={N} too large, skipping direct computation")
        return

    # Find codewords close to optimal center
    import random
    best_M = 0
    best_cws = None

    for _ in range(2000):
        c_high = [random.randint(0, p-1) for _ in range(n-k)]
        c_coeffs = [0] * k + list(c_high)
        c_vals = [sum(c_coeffs[j] * pow(L[i], j, p) for j in range(n)) % p for i in range(n)]

        codewords = []
        for B in combinations(range(n), w):
            roots = [L[i] for i in B]
            es = elem_sym(roots, p)
            c = n - k - w
            ok = True
            for m_off in range(c):
                val = 0
                for j in range(w + 1):
                    c_idx = m_off + j
                    if c_idx < n-k:
                        val += pow(-1, j, p) * es[j] * c_high[c_idx]
                if val % p != 0:
                    ok = False
                    break
            if not ok:
                continue

            # Interpolate codeword
            S = [i for i in range(n) if i not in B]
            if len(S) < k:
                continue
            # Use agreement positions to determine f
            mat = [[pow(L[S[i]], j, p) for j in range(k)] for i in range(k)]
            rhs = [c_vals[S[i]] for i in range(k)]

            # Solve via Gaussian elimination
            aug = [row + [r] for row, r in zip(mat, rhs)]
            ok2 = True
            for col in range(k):
                piv = -1
                for row in range(col, k):
                    if aug[row][col] % p != 0:
                        piv = row
                        break
                if piv == -1:
                    ok2 = False
                    break
                aug[col], aug[piv] = aug[piv], aug[col]
                inv_p = pow(aug[col][col], p-2, p)
                for row in range(k):
                    if row != col and aug[row][col] % p != 0:
                        f2 = aug[row][col] * inv_p % p
                        for j2 in range(k + 1):
                            aug[row][j2] = (aug[row][j2] - f2 * aug[col][j2]) % p
            if not ok2:
                continue

            a = tuple(aug[col][k] * pow(aug[col][col], p-2, p) % p for col in range(k))
            f_vals = tuple(sum(a[j] * pow(L[i], j, p) for j in range(k)) % p for i in range(n))
            codewords.append(f_vals)

        unique_cws = list(set(codewords))
        if len(unique_cws) > best_M:
            best_M = len(unique_cws)
            best_cws = unique_cws[:]

    if best_cws is None or best_M < 2:
        print(f"  Only found M={best_M}, need ≥ 2 for pairwise analysis")
        return

    print(f"\n  Found M = {best_M} codewords")

    # Pairwise analysis
    print(f"\n  Pairwise agreement structure:")
    for i in range(min(best_M, 6)):
        for j in range(i+1, min(best_M, 6)):
            agree = sum(1 for m in range(n) if best_cws[i][m] == best_cws[j][m])
            print(f"    d(f_{i}, f_{j}) = {n - agree}, agree = {agree}")


# ========== 3: The REAL barrier test ==========
def barrier_test(n, k):
    """
    For each valid p: compute max|S(t)| over all t and centers.
    Verify: max|S| = Θ(√(pN)) and NOT o(√(pN)).

    If max|S| = Ω(√(pN)): character sum approach CANNOT give M = O(1).
    If max|S| = o(√(pN)): there's hope.
    """
    w = johnson_w_mds(n, k)
    c = n - k - w
    N = math.comb(n, w)
    ps = primes_1modn(n, 8)

    print(f"\n{'='*70}")
    print(f"BARRIER TEST — RS[{n},{k}], w={w}, c={c}, N={N}")
    print(f"{'='*70}")

    print(f"\n  {'p':>5} {'max|S|':>10} {'√(pN)':>10} {'ratio':>8} {'N/p^c':>8} {'M_alg_bound':>12}")
    print(f"  {'-'*65}")

    for p in ps:
        if p**c > 500000 or N > 5000:
            continue

        omega = find_omega(n, p)
        L = [pow(omega, i, p) for i in range(n)]

        all_B = list(combinations(range(n), w))
        all_sigma = []
        for B in all_B:
            roots = [L[i] for i in B]
            all_sigma.append(elem_sym(roots, p)[1:])

        # Compute max|S(α)| over ALL α
        max_S = 0
        if p**w <= 100000:
            for alpha in product(range(p), repeat=w):
                if all(a == 0 for a in alpha):
                    continue
                S = sum(psi(sum(alpha[j] * sig[j] for j in range(w)) % p, p)
                        for sig in all_sigma)
                mag = abs(S)
                if mag > max_S:
                    max_S = mag
        else:
            import random
            for _ in range(30000):
                alpha = tuple(random.randint(0, p-1) for _ in range(w))
                if all(a == 0 for a in alpha):
                    continue
                S = sum(psi(sum(alpha[j] * sig[j] for j in range(w)) % p, p)
                        for sig in all_sigma)
                mag = abs(S)
                if mag > max_S:
                    max_S = mag

        sqrtpN = math.sqrt(p * N)
        ratio = max_S / sqrtpN
        pc = p**c
        m_bound = N/pc + max_S  # trivial M_alg bound from max|S|

        print(f"  {p:5d} {max_S:10.4f} {sqrtpN:10.4f} {ratio:8.5f} {N/pc:8.3f} {m_bound:12.2f}")


# ========== 4: What the ACTUAL M_alg looks like vs the bound ==========
def actual_vs_bound(n, k):
    """Direct comparison: max M_alg(c) vs the character sum bound."""
    w = johnson_w_mds(n, k)
    c = n - k - w
    N = math.comb(n, w)
    ps = primes_1modn(n, 6)

    print(f"\n{'='*70}")
    print(f"ACTUAL M vs BOUND — RS[{n},{k}], w={w}, c={c}")
    print(f"{'='*70}")

    print(f"\n  {'p':>5} {'N/p^c':>8} {'max M_alg':>10} {'max|S|':>10} {'M_bound':>10} {'gap':>8}")

    for p in ps:
        pc = p**c
        if pc > 200000 or N > 3000:
            continue

        omega = find_omega(n, p)
        L = [pow(omega, i, p) for i in range(n)]
        nk = n - k

        all_B = list(combinations(range(n), w))
        all_sigma = []
        for B in all_B:
            roots = [L[i] for i in B]
            all_sigma.append(elem_sym(roots, p))

        # Find max M_alg over random centers
        import random
        max_M_alg = 0
        for _ in range(5000):
            c_high = [random.randint(0, p-1) for _ in range(nk)]
            cnt = 0
            for es in all_sigma:
                ok = True
                for m_off in range(c):
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
            max_M_alg = max(max_M_alg, cnt)

        # max|S(α)| (just sample)
        max_S = 0
        for _ in range(min(20000, p**w)):
            alpha = tuple(random.randint(0, p-1) for _ in range(w))
            if all(a == 0 for a in alpha):
                continue
            S = sum(psi(sum(alpha[j] * sig[j] for j in range(w)) % p, p)
                    for sig in all_sigma)
            mag = abs(S)
            if mag > max_S:
                max_S = mag

        m_bound = N/pc + max_S
        gap = m_bound / max(max_M_alg, 1)

        print(f"  {p:5d} {N/pc:8.3f} {max_M_alg:10d} {max_S:10.2f} {m_bound:10.2f} {gap:8.1f}x")


# ========== MAIN ==========
if __name__ == '__main__':
    print("DIRECTION C, ROUND 4: BARRIER ANALYSIS")
    print("=" * 70)

    # Barrier test: does max|S| = Θ(√(pN))?
    for n, k in [(6, 3), (8, 4), (10, 5)]:
        barrier_test(n, k)

    # Actual M vs bound
    for n, k in [(6, 3), (8, 4), (10, 5), (12, 6)]:
        actual_vs_bound(n, k)

    # Second moment method
    for n, k, p in [(6, 3, 7), (8, 4, 17), (10, 5, 11), (10, 5, 31)]:
        second_moment_method(n, k, p)

    # Polynomial method
    for n, k, p in [(8, 4, 17), (10, 5, 11), (12, 6, 13)]:
        polynomial_method(n, k, p)

    print("\n\nDONE.")
