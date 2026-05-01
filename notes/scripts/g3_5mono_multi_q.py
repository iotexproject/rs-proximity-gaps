"""g3_5mono_multi_q.py — 5-monomial pencil multi-q empirical K_5.

Pencil: ρ_1 z^a + ρ_2 z^b + ρ_3 z^c + ρ_4 z^d + α z^e on L_8 with k=2.
All 5 distinct positions in {1, ..., 7}: C(7, 5) = 21 cases.

For each q ∈ {97, 193, 257, 449, 1153}, 30 random (ρ_1, ρ_2, ρ_3, ρ_4) per case.
"""
import itertools, random
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
    n_samples = 30
    primes = [97, 193, 257, 449, 1153]

    cases = []
    for combo in itertools.combinations(range(1, n), 5):
        if freduce(gcd, list(combo) + [n]) == 1:
            cases.append(combo)
    print(f"=== 5-mono multi-q sweep at (n, k) = ({n}, {k}) ===")
    print(f"{len(cases)} irreducible cases, {n_samples} samples each")
    print()

    for q in primes:
        omega = find_root_of_unity(q, n)
        if omega is None: continue
        L = [pow(omega, i, q) for i in range(n)]
        rng = random.Random(2026)
        max_bad_global = 0
        max_case_global = None
        for case in cases:
            max_case = 0
            for _ in range(n_samples):
                rho_tuple = tuple(rng.randint(1, q - 1) for _ in range(4))
                bad = count_bad_alpha(list(case), list(rho_tuple), q, L, J, k)
                if bad > max_case: max_case = bad
            if max_case > max_bad_global:
                max_bad_global = max_case
                max_case_global = case
        print(f"  q = {q:>5}: max |B(α)| = {max_bad_global} at {max_case_global}")

    print()
    print("K_5 trend across q.")


if __name__ == "__main__":
    main()
