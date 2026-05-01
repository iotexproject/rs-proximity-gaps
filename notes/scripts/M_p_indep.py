#!/usr/bin/env python3
"""
p-independence for conds/B ≥ 2.
Strategy: for each (n,k,w), find worst-case center for SMALL p,
then check if the SAME combinatorial structure (which B's are compatible)
gives the same M for larger p.

Key idea: M should depend on (n,k,w) and the INDEX SET structure,
not on the specific prime p.
"""

from itertools import combinations
import math


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


def find_M_with_center(n, k, p, w, c_high):
    """For a given center (specified as c_high coefficients),
    compute M_actual."""
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    c_coeffs = [0] * k + list(c_high)
    c_vals = [sum(c_coeffs[j] * pow(L[i], j, p) for j in range(n)) % p
              for i in range(n)]

    all_B = list(combinations(range(n), w))
    all_sv = []
    for B in all_B:
        roots = [L[i] for i in B]
        sigma = elem_sym(roots, p)
        all_sv.append([sigma[j] % p for j in range(1, w + 1)])

    # Build conditions
    nk = n - k
    conds_list = []
    for m in range(k + w, n):
        A_row = [0] * w
        c_mw_idx = m - w - k
        c_mw = c_high[c_mw_idx] if 0 <= c_mw_idx < nk else 0
        b_val = (-c_mw) % p
        for j in range(1, w + 1):
            c_idx = m - w + j - k
            c_val = c_high[c_idx] if 0 <= c_idx < nk else 0
            A_row[j - 1] = (pow(-1, j, p) * c_val) % p
        conds_list.append((A_row, b_val))

    # Find compatible B's
    compat = []
    for idx, sv in enumerate(all_sv):
        ok = True
        for A_row, b_val in conds_list:
            val = sum(A_row[j] * sv[j] for j in range(w)) % p
            if val != b_val:
                ok = False
                break
        if ok:
            compat.append(idx)

    M_alg = len(compat)

    # Compute M_actual
    codewords = set()
    dists = {}
    compat_B_list = []
    for idx in compat:
        B = all_B[idx]
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
        codewords.add(f_vals)
        dists[d_val] = dists.get(d_val, 0) + 1
        compat_B_list.append(B)

    return len(codewords), M_alg, dists, compat_B_list


def exhaustive_search(n, k, p, w, max_trials=50000):
    """Exhaustive search for worst-case M_actual over all c_high in F_p^{n-k}."""
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    nk = n - k

    all_B = list(combinations(range(n), w))
    all_sv = []
    for B in all_B:
        roots = [L[i] for i in B]
        sigma = elem_sym(roots, p)
        all_sv.append([sigma[j] % p for j in range(1, w + 1)])

    def count_M_actual(c_high):
        conds_list = []
        for m in range(k + w, n):
            A_row = [0] * w
            c_mw_idx = m - w - k
            c_mw = c_high[c_mw_idx] if 0 <= c_mw_idx < nk else 0
            b_val = (-c_mw) % p
            for j in range(1, w + 1):
                c_idx = m - w + j - k
                c_val = c_high[c_idx] if 0 <= c_idx < nk else 0
                A_row[j - 1] = (pow(-1, j, p) * c_val) % p
            conds_list.append((A_row, b_val))

        compat = []
        for idx, sv in enumerate(all_sv):
            ok = True
            for A_row, b_val in conds_list:
                val = sum(A_row[j] * sv[j] for j in range(w)) % p
                if val != b_val:
                    ok = False
                    break
            if ok:
                compat.append(idx)

        if len(compat) <= 1:
            return len(compat), len(compat), False

        c_coeffs = [0] * k + list(c_high)
        c_vals = [sum(c_coeffs[j2] * pow(L[i], j2, p) for j2 in range(n)) % p
                  for i in range(n)]

        codewords = set()
        has_close = False
        for idx in compat:
            B = all_B[idx]
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

        return len(codewords), len(compat), has_close

    best = 0
    best_c = None
    total = p ** nk
    trials = min(total, max_trials)
    import random
    random.seed(42)

    if total <= max_trials:
        # Exhaustive
        for idx in range(total):
            c_high = []
            temp = idx
            for _ in range(nk):
                c_high.append(temp % p)
                temp //= p
            M_act, M_alg, has_close = count_M_actual(c_high)
            if not has_close and M_act > best:
                best = M_act
                best_c = c_high[:]
    else:
        # Random
        for _ in range(trials):
            c_high = [random.randint(0, p - 1) for _ in range(nk)]
            M_act, M_alg, has_close = count_M_actual(c_high)
            if not has_close and M_act > best:
                best = M_act
                best_c = c_high[:]

    return best, best_c, total <= max_trials


# ===== EXHAUSTIVE for small cases =====
print("=" * 70)
print("EXHAUSTIVE M_actual SEARCH (small p)")
print("=" * 70)

for n, k, w in [(10, 5, 3), (12, 6, 4)]:
    ps = primes_cong_1(n, 3)
    print(f"\nn={n}, k={k}, w={w}, conds/B={n-w-k}:")
    for p in ps:
        M, c, is_exact = exhaustive_search(n, k, p, w, max_trials=p ** (n - k))
        tag = "(EXHAUSTIVE)" if is_exact else "(RANDOM)"
        print(f"  p={p:4d}: M_actual = {M}  c_high={c}  {tag}")
        if c and M > 0:
            # Verify with other primes using same c_high
            for p2 in ps:
                if p2 != p:
                    M2, _, d2, Bs2 = find_M_with_center(n, k, p2, w, c)
                    print(f"    → same c at p={p2}: M_actual={M2}, dists={d2}")

# ===== For n=6, 8: already verified above =====
print(f"\n{'='*70}")
print("SUMMARY: WORST-CASE M_actual vs p")
print("="*70)

for n, k, w in [(6, 3, 2), (8, 4, 3), (10, 5, 3)]:
    ps = primes_cong_1(n, 5)
    print(f"\nn={n}, k={k}, w={w}, conds/B={n-w-k}:")
    for p in ps:
        M, c, is_exact = exhaustive_search(n, k, p, w, max_trials=200000)
        tag = "EX" if is_exact else "RN"
        print(f"  p={p:4d}: M={M} [{tag}]")
