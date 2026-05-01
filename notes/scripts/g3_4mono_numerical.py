"""g3_4mono_numerical.py — numerical |B(α)| max for 4-mono pencils at (8, 2).

For each (a, b, c, d) at (8, 2), random sample (ρ1, ρ2, ρ3) ∈ F_q^3 and
count |{α : pencil bad on L_8}| per ρ-tuple. Output max per case.

Goal: empirical universal K_4 bound for 4-mono pencils. Expected K_4 ≤ 9
(matching K_3) or smaller (since 4-mono has more constraints).
"""
import itertools
import random
from math import gcd
from functools import reduce as freduce


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


def count_bad_alpha(n, k, positions, coefs_partial, q, omega):
    L = [pow(omega, i, q) for i in range(n)]
    J = n // 2
    bad = 0
    for alpha in range(q):
        coefs = list(coefs_partial) + [alpha]
        h = [sum(coefs[j] * pow(L[i], positions[j], q) for j in range(len(positions))) % q for i in range(n)]
        if dist_le_J(h, L, k, q, J): bad += 1
    return bad


def sweep_q(n, k, q, n_samples, log_each_case=False):
    omega = find_root_of_unity(q, n)
    if omega is None:
        return None, None
    rng = random.Random(2026)
    cases = []
    for a in range(1, n - 3):
        for b in range(a + 1, n - 2):
            for c in range(b + 1, n - 1):
                for d in range(c + 1, n):
                    g = freduce(gcd, [a, b, c, d, n])
                    if g != 1: continue
                    cases.append((a, b, c, d))
    max_bad_global = 0
    max_case_global = None
    for case in cases:
        max_bad_case = 0
        for _ in range(n_samples):
            rho_tuple = (rng.randint(1, q - 1), rng.randint(1, q - 1), rng.randint(1, q - 1))
            bad = count_bad_alpha(n, k, list(case), list(rho_tuple), q, omega)
            if bad > max_bad_case:
                max_bad_case = bad
        if log_each_case:
            print(f"  {case}: max |B(α)| = {max_bad_case}", flush=True)
        if max_bad_case > max_bad_global:
            max_bad_global = max_bad_case
            max_case_global = case
    return max_bad_global, max_case_global


def main():
    n, k = 8, 2
    q = 97
    omega = find_root_of_unity(q, n)
    rng = random.Random(2026)
    n_samples = 30  # random ρ-tuples per case

    print(f"=== 4-mono pencils at (n, k) = ({n}, {k}), q = {q} ===")
    print(f"Sampling {n_samples} (ρ1, ρ2, ρ3) per case")
    print(f"Pencil: ρ1·z^a + ρ2·z^b + ρ3·z^c + α·z^d on L_{n}")
    print()

    cases = []
    for a in range(1, n - 3):
        for b in range(a + 1, n - 2):
            for c in range(b + 1, n - 1):
                for d in range(c + 1, n):
                    g = freduce(gcd, [a, b, c, d, n])
                    if g != 1: continue
                    cases.append((a, b, c, d))

    max_bad_global = 0
    max_case_global = None
    for case in cases:
        max_bad_case = 0
        for _ in range(n_samples):
            rho_tuple = (rng.randint(1, q - 1), rng.randint(1, q - 1), rng.randint(1, q - 1))
            bad = count_bad_alpha(n, k, list(case), list(rho_tuple), q, omega)
            if bad > max_bad_case:
                max_bad_case = bad
        marker = ""
        if max_bad_case > max_bad_global:
            max_bad_global = max_bad_case
            max_case_global = case
            marker = "  <<< MAX so far"
        print(f"  {case}: max |B(α)| = {max_bad_case}{marker}", flush=True)

    print(f"\n=== SUMMARY ===")
    print(f"Max |B(α)| over all 4-mono cases at (8, 2): {max_bad_global}")
    print(f"Achieved at: {case if max_case_global is None else max_case_global}")
    print(f"Empirical K_4 ≤ {max_bad_global} (universal at deployment via Substitution Principle).")


if __name__ == "__main__":
    main()
