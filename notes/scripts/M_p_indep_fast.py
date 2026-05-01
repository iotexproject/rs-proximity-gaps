#!/usr/bin/env python3
"""
Fast p-independence check. Strategy:
1. For small p: exhaustive search (p^{n-k} ≤ 200K)
2. For larger p: random search (50K trials)
3. Cross-check: take best center from small-p, test at larger p
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


def search_M(n, k, p, w, max_trials=50000):
    """Search for worst-case M_actual. Returns (M, c_high, is_exhaustive)."""
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    conds = n - w - k
    nk = n - k

    all_B = list(combinations(range(n), w))
    # Precompute σ as flat arrays for speed
    n_B = len(all_B)
    all_sv = []
    for B in all_B:
        roots = [L[i] for i in B]
        sigma = elem_sym(roots, p)
        all_sv.append(tuple(sigma[j] % p for j in range(1, w + 1)))

    def get_compat_count(c_high):
        """Fast: just count compatible B's."""
        count = 0
        for sv in all_sv:
            ok = True
            for m_off in range(conds):
                m = k + w + m_off
                val = 0
                for j in range(w + 1):
                    c_idx = m - w + j - k
                    c_val = c_high[c_idx] if 0 <= c_idx < nk else 0
                    if c_val == 0:
                        continue
                    if j == 0:
                        val += c_val
                    else:
                        sign = 1 if j % 2 == 0 else p - 1
                        val += sign * c_val * sv[j - 1]
                if val % p != 0:
                    ok = False
                    break
            if ok:
                count += 1
        return count

    def get_M_actual(c_high):
        """Full M_actual with interpolation."""
        c_coeffs = [0] * k + list(c_high)
        c_vals = [sum(c_coeffs[j2] * pow(L[i], j2, p) for j2 in range(n)) % p
                  for i in range(n)]

        compat_indices = []
        for idx, sv in enumerate(all_sv):
            ok = True
            for m_off in range(conds):
                m = k + w + m_off
                val = 0
                for j in range(w + 1):
                    c_idx = m - w + j - k
                    c_val = c_high[c_idx] if 0 <= c_idx < nk else 0
                    if c_val == 0:
                        continue
                    if j == 0:
                        val += c_val
                    else:
                        sign = 1 if j % 2 == 0 else p - 1
                        val += sign * c_val * sv[j - 1]
                if val % p != 0:
                    ok = False
                    break
            if ok:
                compat_indices.append(idx)

        if len(compat_indices) <= 1:
            return len(compat_indices), False

        codewords = set()
        has_close = False
        for idx in compat_indices:
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

        return len(codewords), has_close

    total = p ** nk
    is_exhaustive = total <= max_trials
    trials = min(total, max_trials)

    best_M = 0
    best_c = None

    if is_exhaustive:
        for idx in range(total):
            c_high = []
            temp = idx
            for _ in range(nk):
                c_high.append(temp % p)
                temp //= p
            cnt = get_compat_count(c_high)
            if cnt <= 1 or cnt > 50:
                continue
            M_act, has_close = get_M_actual(c_high)
            if not has_close and M_act > best_M:
                best_M = M_act
                best_c = c_high[:]
    else:
        for _ in range(trials):
            c_high = [random.randint(0, p - 1) for _ in range(nk)]
            cnt = get_compat_count(c_high)
            if cnt <= 1 or cnt > 50:
                continue
            M_act, has_close = get_M_actual(c_high)
            if not has_close and M_act > best_M:
                best_M = M_act
                best_c = c_high[:]

    return best_M, best_c, is_exhaustive


# ===== p-independence for rate 1/2 at Johnson =====
print("=" * 70)
print("p-INDEPENDENCE OF M_actual (rate 1/2 at Johnson)")
print("=" * 70)

for n in [6, 8, 10, 12]:
    k = n // 2
    w = johnson_radius(n, k)
    conds = n - w - k
    ps = primes_cong_1(n, 4)

    print(f"\nn={n}, k={k}, w={w}, conds/B={conds}")
    results = []
    for p in ps:
        M, c, is_ex = search_M(n, k, p, w, max_trials=200000)
        tag = "EX" if is_ex else f"RND({200000})"
        results.append((p, M, c, is_ex))
        print(f"  p={p:4d}: M_actual={M:2d}  {tag}  c={c}")

    # Cross-check: best center from smallest p, test at other primes
    best_p, best_M, best_c, _ = max(results, key=lambda x: x[1])
    if best_c and best_M > 0:
        print(f"\n  Cross-check: center from p={best_p} (M={best_M}):")
        for p2, _, _, _ in results:
            if p2 == best_p:
                continue
            # Evaluate same center at different prime
            omega2 = find_omega(n, p2)
            L2 = [pow(omega2, i, p2) for i in range(n)]
            c_high2 = [v % p2 for v in best_c]
            c_coeffs2 = [0] * k + c_high2
            c_vals2 = [sum(c_coeffs2[j] * pow(L2[i], j, p2) for j in range(n)) % p2
                       for i in range(n)]
            # Count M_actual
            codewords = set()
            for B in combinations(range(n), w):
                S = [i for i in range(n) if i not in B]
                roots = [L2[i] for i in B]
                sigma = elem_sym(roots, p2)
                sv = tuple(sigma[j] % p2 for j in range(1, w + 1))
                ok = True
                for m_off in range(conds):
                    m = k + w + m_off
                    val = 0
                    for j in range(w + 1):
                        c_idx = m - w + j - k
                        c_val = c_high2[c_idx] if 0 <= c_idx < n - k else 0
                        if c_val == 0:
                            continue
                        if j == 0:
                            val += c_val
                        else:
                            sign = 1 if j % 2 == 0 else p2 - 1
                            val += sign * c_val * sv[j - 1]
                    if val % p2 != 0:
                        ok = False
                        break
                if not ok:
                    continue
                # Interpolate
                m_sys = len(S)
                aug = [[pow(L2[S[i]], j, p2) for j in range(k)] + [c_vals2[S[i]]]
                       for i in range(m_sys)]
                pivot_cols = []
                for col in range(k):
                    piv = -1
                    for row in range(len(pivot_cols), m_sys):
                        if aug[row][col] % p2 != 0:
                            piv = row
                            break
                    if piv == -1:
                        continue
                    r2 = len(pivot_cols)
                    aug[r2], aug[piv] = aug[piv], aug[r2]
                    inv_p = pow(aug[r2][col], p2 - 2, p2)
                    for row in range(m_sys):
                        if row != r2 and aug[row][col] % p2 != 0:
                            f2 = aug[row][col] * inv_p % p2
                            for j2 in range(k + 1):
                                aug[row][j2] = (aug[row][j2] - f2 * aug[r2][j2]) % p2
                    pivot_cols.append(col)
                consistent = True
                for row in range(len(pivot_cols), m_sys):
                    if aug[row][k] % p2 != 0:
                        consistent = False
                        break
                if not consistent:
                    continue
                a = [0] * k
                for idx2, col in enumerate(pivot_cols):
                    a[col] = aug[idx2][k] * pow(aug[idx2][col], p2 - 2, p2) % p2
                f_vals = tuple(sum(a[j] * pow(L2[i], j, p2) for j in range(k)) % p2
                              for i in range(n))
                d_val = sum(1 for i in range(n) if c_vals2[i] != f_vals[i])
                if d_val >= w:
                    codewords.add(f_vals)
            print(f"    p={p2}: M_actual={len(codewords)}")
