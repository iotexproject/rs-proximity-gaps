#!/usr/bin/env python3
"""
1. p-independence check for M_actual
2. Extend to n=18,20
3. Character sum analysis: N(n,w,s) distribution
"""

from itertools import combinations
import random
import math

random.seed(42)


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
    p = n + 1
    while len(result) < count:
        if p % n == 1:
            is_prime = p > 1
            for d in range(2, int(p ** 0.5) + 1):
                if p % d == 0:
                    is_prime = False
                    break
            if is_prime:
                result.append(p)
        p += 1
    return result


def johnson_radius(n, k):
    return math.ceil((1 - math.sqrt(k / n)) * n)


def find_worst_M(n, k, p, w, n_search=15000):
    """Find worst-case M_actual by random search. Return M, c_high."""
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    conds = n - w - k
    nk = n - k

    # Precompute σ
    all_B = list(combinations(range(n), w))
    all_sv = []
    for B in all_B:
        roots = [L[i] for i in B]
        sigma = elem_sym(roots, p)
        all_sv.append([sigma[j] % p for j in range(1, w + 1)])

    def build_conds(c_high):
        rows = []
        for m in range(k + w, n):
            A_row = [0] * w
            c_mw_idx = m - w - k
            c_mw = c_high[c_mw_idx] if 0 <= c_mw_idx < nk else 0
            b_val = (-c_mw) % p
            for j in range(1, w + 1):
                c_idx = m - w + j - k
                c_val = c_high[c_idx] if 0 <= c_idx < nk else 0
                A_row[j - 1] = (pow(-1, j, p) * c_val) % p
            rows.append((A_row, b_val))
        return rows

    def count_compat(conds_list):
        count = 0
        for sv in all_sv:
            ok = True
            for A_row, b_val in conds_list:
                val = 0
                for j in range(w):
                    val += A_row[j] * sv[j]
                if val % p != b_val:
                    ok = False
                    break
            if ok:
                count += 1
        return count

    def get_M_actual(c_high):
        """Full M_actual computation with interpolation."""
        conds_list = build_conds(c_high)
        c_coeffs = [0] * k + list(c_high)
        c_vals = [sum(c_coeffs[j2] * pow(L[i], j2, p) for j2 in range(n)) % p
                  for i in range(n)]

        codewords = set()
        has_close = False
        for idx, (B, sv) in enumerate(zip(all_B, all_sv)):
            ok = True
            for A_row, b_val in conds_list:
                val = sum(A_row[j] * sv[j] for j in range(w)) % p
                if val != b_val:
                    ok = False
                    break
            if not ok:
                continue

            S = [i for i in range(n) if i not in B]
            m_sys = len(S)
            aug = [[pow(L[S[i]], j, p) for j in range(k)] + [c_vals[S[i]]]
                   for i in range(m_sys)]
            pivot_cols = []
            for col in range(k):
                piv = -1
                for row in range(len(pivot_cols), m_sys):
                    if aug[row][col] % p != 0:
                        piv = row
                        break
                if piv == -1:
                    continue
                r2 = len(pivot_cols)
                aug[r2], aug[piv] = aug[piv], aug[r2]
                inv_p = pow(aug[r2][col], p - 2, p)
                for row in range(m_sys):
                    if row != r2 and aug[row][col] % p != 0:
                        f2 = aug[row][col] * inv_p % p
                        for j2 in range(k + 1):
                            aug[row][j2] = (aug[row][j2] - f2 * aug[r2][j2]) % p
                pivot_cols.append(col)
            consistent = True
            for row in range(len(pivot_cols), m_sys):
                if aug[row][k] % p != 0:
                    consistent = False
                    break
            if not consistent:
                continue
            a = [0] * k
            for idx2, col in enumerate(pivot_cols):
                a[col] = aug[idx2][k] * pow(aug[idx2][col], p - 2, p) % p
            f_vals = tuple(sum(a[j] * pow(L[i], j, p) for j in range(k)) % p
                          for i in range(n))
            d_val = sum(1 for i in range(n) if c_vals[i] != f_vals[i])
            if d_val < w:
                has_close = True
            codewords.add(f_vals)

        return len(codewords), has_close

    best_actual = 0
    best_c = None
    n_trials = 0

    # Only search for centers where all codewords are at distance exactly w
    for _ in range(n_search):
        c_high = [random.randint(0, p - 1) for _ in range(nk)]
        conds_list = build_conds(c_high)
        M_alg = count_compat(conds_list)
        if M_alg <= 1 or M_alg > 30:  # skip likely overcounted
            n_trials += 1
            continue

        M_act, has_close = get_M_actual(c_high)
        if not has_close and M_act > best_actual:
            best_actual = M_act
            best_c = c_high[:]
        n_trials += 1

    return best_actual, best_c


# ===== 1. p-independence =====
print("=" * 70)
print("p-INDEPENDENCE OF M_actual")
print("=" * 70)

for n, k, w in [(6, 3, 2), (8, 4, 3), (10, 5, 3), (12, 6, 4)]:
    ps = primes_cong_1(n, 4)
    print(f"\nn={n}, k={k}, w={w}:")
    for p in ps:
        M, _ = find_worst_M(n, k, p, w, n_search=8000)
        print(f"  p={p:4d}: M_actual = {M}")


# ===== 2. N(n,w,s) distribution =====
print(f"\n{'=' * 70}")
print("N(n,w,s) = #{w-subsets of Z/nZ with sum ≡ s mod n}")
print("=" * 70)

for n in [6, 8, 10, 12, 14, 16, 18, 20]:
    k = n // 2
    w = johnson_radius(n, k)
    N = {}
    for B in combinations(range(n), w):
        s = sum(B) % n
        N[s] = N.get(s, 0) + 1
    vals = sorted(N.values())
    cnw = math.comb(n, w)
    print(f"n={n}, w={w}: C({n},{w})={cnw}, "
          f"N range [{vals[0]}, {vals[-1]}], "
          f"avg={cnw/n:.1f}, "
          f"#distinct_sums={len(N)}, "
          f"gcd(w,n)={math.gcd(w,n)}")


# ===== 3. Extend to n=18, 20 =====
print(f"\n{'=' * 70}")
print("M_actual FOR n=18, 20")
print("=" * 70)

for n in [18, 20]:
    k = n // 2
    w = johnson_radius(n, k)
    p = primes_cong_1(n, 1)[0]
    conds = n - w - k
    cnw = math.comb(n, w)
    print(f"\nn={n}, k={k}, w={w}, p={p}, conds/B={conds}, C({n},{w})={cnw}")
    print(f"Avg M_alg = {cnw / p**conds:.4f}")

    M, c = find_worst_M(n, k, p, w, n_search=10000)
    print(f"M_actual = {M}")
