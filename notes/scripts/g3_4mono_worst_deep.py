"""g3_4mono_worst_deep.py — DEEP ρ-sweep for the 3 worst 4-mono cases.

Cases with deg_α(Φ) = 12 from Singular GB (Note 0295):
- (1, 2, 5, 6)
- (1, 2, 6, 7)
- (1, 3, 4, 7)

Goal: large random ρ-sample (1000+ per case) at q ∈ {193, 257, 449} to
find true max |B(α)| empirically. If max << 12, Φ has spurious factors.
"""
import itertools, random
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
    cases = [(1, 2, 5, 6), (1, 2, 6, 7), (1, 3, 4, 7)]
    primes = [193, 257, 449]
    n_samples = 1000

    print(f"=== Deep ρ-sweep for 4-mono worst cases at (8, 2) ===")
    print(f"{n_samples} samples per case per q\n")

    for q in primes:
        omega = find_root_of_unity(q, n)
        if omega is None: continue
        L = [pow(omega, i, q) for i in range(n)]
        rng = random.Random(2026)
        print(f"q = {q}:")
        for case in cases:
            max_bad = 0
            argmax_rho = None
            for _ in range(n_samples):
                rho_tuple = (rng.randint(1, q - 1), rng.randint(1, q - 1), rng.randint(1, q - 1))
                bad = count_bad_alpha(list(case), list(rho_tuple), q, L, J, k)
                if bad > max_bad:
                    max_bad = bad
                    argmax_rho = rho_tuple
            print(f"  {case}: max |B(α)| = {max_bad} at ρ = {argmax_rho}")
        print()


if __name__ == "__main__":
    main()
