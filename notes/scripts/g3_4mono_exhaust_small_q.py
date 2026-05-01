"""g3_4mono_exhaust_small_q.py — exhaustive ρ-sweep at small q for case (1, 2, 5, 6).

q = 41 gives 8 | q-1 with q^3 = 68921 small enough to exhaustive enumerate
ρ_1, ρ_2, ρ_3 ∈ F_q*. For each, count |B(α)|. Find true max.

If empirical max reaches deg_α(Φ) = 12: Φ is tight.
If empirical max stays at ≤ 8: Φ has spurious factors (gap to factor).
"""
import itertools
from math import gcd


def find_root_of_unity(q, n):
    if (q - 1) % n != 0: return None
    g = 2
    while True:
        if pow(g, n, q) == 1 and all(pow(g, n // p, q) != 1 for p in [2, 3, 5] if n % p == 0):
            return g
        g += 1
        if g >= q: return None


def gauss_consistent(M, q):
    rows = [list(r) for r in M]
    n_rows, n_cols = len(rows), len(rows[0]) - 1
    pr = 0
    for c in range(n_cols):
        if pr >= n_rows: break
        p = pr
        while p < n_rows and rows[p][c] % q == 0: p += 1
        if p == n_rows: continue
        rows[pr], rows[p] = rows[p], rows[pr]
        inv = pow(rows[pr][c], -1, q)
        rows[pr] = [(x * inv) % q for x in rows[pr]]
        for r in range(n_rows):
            if r != pr and rows[r][c] % q != 0:
                f = rows[r][c]
                rows[r] = [(rows[r][i] - f * rows[pr][i]) % q for i in range(n_cols + 1)]
        pr += 1
    for r in range(pr, n_rows):
        if rows[r][-1] % q != 0: return False
    return True


def dist_le_J(values, L, k, q, J):
    n = len(values); target = n - J
    M_full = [[pow(L[i], j, q) for j in range(k)] for i in range(n)]
    for S in itertools.combinations(range(n), target):
        M_sub = [list(M_full[i]) + [values[i]] for i in S]
        if gauss_consistent(M_sub, q): return True
    return False


def count_bad_alpha(positions, coefs_partial, q, L, J, k):
    n = len(L)
    bad = 0
    for alpha in range(q):
        coefs = list(coefs_partial) + [alpha]
        h = [sum(coefs[j] * pow(L[i], positions[j], q) for j in range(len(positions))) % q for i in range(n)]
        if dist_le_J(h, L, k, q, J): bad += 1
    return bad


def main():
    n, k = 8, 2
    J = n // 2
    case = (1, 2, 5, 6)  # worst case from Note 0295 (deg_α = 12)

    # q = 41: 8 | 40, q^3 = 68921
    for q in [41, 73, 89]:
        omega = find_root_of_unity(q, n)
        if omega is None: continue
        L = [pow(omega, i, q) for i in range(n)]
        max_bad = 0
        argmax = None
        total = 0
        print(f"q = {q}, exhaustive ρ ∈ F_{q}^*³ for case {case}")
        for r1 in range(1, q):
            for r2 in range(1, q):
                for r3 in range(1, q):
                    bad = count_bad_alpha(list(case), [r1, r2, r3], q, L, J, k)
                    total += 1
                    if bad > max_bad:
                        max_bad = bad
                        argmax = (r1, r2, r3)
                        print(f"  new max: |B(α)| = {bad} at ρ = {argmax}", flush=True)
        print(f"  TOTAL: {total} ρ-tuples, max |B(α)| = {max_bad}")
        print()


if __name__ == "__main__":
    main()
