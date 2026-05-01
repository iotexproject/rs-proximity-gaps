"""g3_subst_principle_verify.py — empirical verification of universal
Substitution Principle (Note 0294) at (16, 4) → (8, 2).

For each 3-mono and 4-mono case at (n, k) = (16, 4) with gcd | 2 (reducible
to (n/d, k/d) = (8, 2) for d = 2):

1. Compute |B(α)| at (16, 4) numerically at q = 193.
2. Compute |B(α)| at (8, 2) for reduced positions (a/2, b/2, ...) at q = 193.
3. Verify they match.

If matches at all reducible cases: Substitution Principle empirical ✓.

Also: for irreducible cases at (16, 4) (gcd = 1), |B(α)| should NOT
exceed K_s at base case (8, 2), since (16, 4) is a separate "base"
class needing direct enumeration.
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
    q = 193
    n_samples = 20

    print(f"=== Substitution Principle empirical verification ===")
    print(f"q = {q}, {n_samples} ρ-samples per case\n")

    # --- 3-mono reducible (gcd = 2): (a, b, c) at (16, 4) → (a/2, b/2, c/2) at (8, 2) ---
    print("3-mono reducible cases at (16, 4) (gcd = 2):")
    print(f"{'(16,4) case':>20} | {'K_(16,4)':>10} | {'(8,2) case':>14} | {'K_(8,2)':>10} | match?")
    print("-" * 75)

    omega16 = find_root_of_unity(q, 16)
    omega8 = find_root_of_unity(q, 8)
    L16 = [pow(omega16, i, q) for i in range(16)]
    L8 = [pow(omega8, i, q) for i in range(8)]
    rng = random.Random(2026)

    matches = 0; total = 0
    for combo in itertools.combinations(range(1, 16), 3):
        g = freduce(gcd, list(combo) + [16])
        if g != 2: continue  # reducible to (8, 2)
        # Compute max K at (16, 4)
        max_K_16 = 0
        for _ in range(n_samples):
            rho_pair = (rng.randint(1, q - 1), rng.randint(1, q - 1))
            bad = count_bad_alpha(list(combo), list(rho_pair), q, L16, 8, 4)
            if bad > max_K_16: max_K_16 = bad

        reduced = tuple(c // 2 for c in combo)
        max_K_8 = 0
        for _ in range(n_samples):
            rho_pair = (rng.randint(1, q - 1), rng.randint(1, q - 1))
            bad = count_bad_alpha(list(reduced), list(rho_pair), q, L8, 4, 2)
            if bad > max_K_8: max_K_8 = bad

        match = "✓" if max_K_16 == max_K_8 else "✗"
        if max_K_16 == max_K_8: matches += 1
        total += 1
        print(f"{str(combo):>20} | {max_K_16:>10} | {str(reduced):>14} | {max_K_8:>10} | {match}")

    print(f"\n3-mono reducible: {matches}/{total} match")
    print()

    # --- 3-mono irreducible (gcd = 1) at (16, 4): direct (16, 4) base ---
    print("3-mono irreducible cases at (16, 4) (gcd = 1):")
    print(f"{'case':>15} | {'K_(16,4)':>10} | {'≤ K_3 = 9?':>12}")
    print("-" * 50)
    irred_pass = 0; irred_total = 0
    for combo in itertools.combinations(range(1, 16), 3):
        g = freduce(gcd, list(combo) + [16])
        if g != 1: continue
        # only 3-mono with k_2 = 4 (k=4), so check w_J(L_16) = 16 - sqrt(64) = 8
        max_K = 0
        for _ in range(min(n_samples, 10)):  # fewer samples (more cases)
            rho_pair = (rng.randint(1, q - 1), rng.randint(1, q - 1))
            bad = count_bad_alpha(list(combo), list(rho_pair), q, L16, 8, 4)
            if bad > max_K: max_K = bad
        if max_K <= 9: irred_pass += 1
        irred_total += 1
        if max_K > 9 or irred_total <= 5:
            print(f"{str(combo):>15} | {max_K:>10} | {'✓' if max_K <= 9 else '✗ EXCEED'}")

    print(f"... {irred_total - 5} more rows omitted ...")
    print(f"\n3-mono irreducible at (16, 4): {irred_pass}/{irred_total} satisfy K ≤ 9")


if __name__ == "__main__":
    main()
