"""g3_5mono_deeper_sweep.py — deeper multi-q empirical K_5 with adversarial seeding.

Beyond Note 0293 (30 samples per case), this sweep:
- 100 random samples per case at each q ∈ {97, 193, 257, 449, 1153, 2017}
- Adversarial seed at "worst" ρ patterns (ρ_i ∈ small set of structured values)
- All 21 irreducible 5-mono cases at (n, k) = (8, 2)

Output: max |B(α)| per case per q. Goal: confirm K_5 ≤ 6 EMPIRICAL UNIVERSAL
or identify a worse witness.
"""
import itertools
import random
from math import gcd
from functools import reduce as freduce


def find_root_of_unity(q, n):
    if (q - 1) % n != 0:
        return None
    g = 2
    while g < q:
        if pow(g, n, q) == 1 and all(pow(g, n // p, q) != 1 for p in [2, 3, 5] if n % p == 0):
            return g
        g += 1
    return None


def gauss_consistent(M, q):
    rows = [list(r) for r in M]
    n_rows, n_cols = len(rows), len(rows[0]) - 1
    pr = 0
    for c in range(n_cols):
        if pr >= n_rows:
            break
        p = pr
        while p < n_rows and rows[p][c] % q == 0:
            p += 1
        if p == n_rows:
            continue
        rows[pr], rows[p] = rows[p], rows[pr]
        inv = pow(rows[pr][c], -1, q)
        rows[pr] = [(x * inv) % q for x in rows[pr]]
        for r in range(n_rows):
            if r != pr and rows[r][c] % q != 0:
                f = rows[r][c]
                rows[r] = [(rows[r][i] - f * rows[pr][i]) % q for i in range(n_cols + 1)]
        pr += 1
    for r in range(pr, n_rows):
        if rows[r][-1] % q != 0:
            return False
    return True


def dist_le_J(values, L, k, q, J):
    n = len(values)
    target = n - J
    M_full = [[pow(L[i], j, q) for j in range(k)] for i in range(n)]
    for S in itertools.combinations(range(n), target):
        M_sub = [list(M_full[i]) + [values[i]] for i in S]
        if gauss_consistent(M_sub, q):
            return True
    return False


def count_bad_alpha(positions, coefs_partial, q, L, J, k):
    n = len(L)
    bad = 0
    for alpha in range(q):
        coefs = list(coefs_partial) + [alpha]
        h = [sum(coefs[j] * pow(L[i], positions[j], q) for j in range(len(positions))) % q for i in range(n)]
        if dist_le_J(h, L, k, q, J):
            bad += 1
    return bad


def adversarial_rhos(q, n_special):
    """Generate 'worst-case' candidate rho patterns: small integers, roots of unity, etc."""
    omega = find_root_of_unity(q, 8) or 2
    candidates = []
    for i in range(min(8, q-1)):
        candidates.append(pow(omega, i, q))
    for i in range(1, min(8, q)):
        candidates.append(i)
    candidates = list(set(candidates))[:n_special]
    return candidates


def main():
    n, k = 8, 2
    J = n // 2
    n_random_samples = 100
    primes = [97, 193, 257, 449, 1153, 2017]

    cases = []
    for combo in itertools.combinations(range(1, n), 5):
        if freduce(gcd, list(combo) + [n]) == 1:
            cases.append(combo)
    print(f"=== 5-mono DEEPER multi-q sweep at (n, k) = ({n}, {k}) ===")
    print(f"{len(cases)} irreducible cases × {n_random_samples} random + adversarial samples")
    print()

    overall_max = 0
    overall_witness = None

    for q in primes:
        omega = find_root_of_unity(q, n)
        if omega is None:
            print(f"  q = {q}: no root of unity, skip")
            continue
        L = [pow(omega, i, q) for i in range(n)]
        rng = random.Random(2026 + q)
        max_bad_q = 0
        max_case_q = None
        max_rho_q = None

        for case in cases:
            max_case = 0
            best_rho = None

            for _ in range(n_random_samples):
                rho_tuple = tuple(rng.randint(1, q - 1) for _ in range(4))
                bad = count_bad_alpha(list(case), list(rho_tuple), q, L, J, k)
                if bad > max_case:
                    max_case = bad
                    best_rho = rho_tuple

            adv_set = adversarial_rhos(q, 8)
            for rho_tuple in itertools.product(adv_set, repeat=4):
                if 0 in rho_tuple:
                    continue
                bad = count_bad_alpha(list(case), list(rho_tuple), q, L, J, k)
                if bad > max_case:
                    max_case = bad
                    best_rho = rho_tuple

            if max_case > max_bad_q:
                max_bad_q = max_case
                max_case_q = case
                max_rho_q = best_rho

        print(f"  q = {q:>5}: max |B(α)| = {max_bad_q} at case {max_case_q}, rho = {max_rho_q}")
        if max_bad_q > overall_max:
            overall_max = max_bad_q
            overall_witness = (q, max_case_q, max_rho_q)

    print()
    print(f"=== OVERALL ===")
    print(f"Max |B(α)| across all q, all cases: {overall_max}")
    print(f"Witness: q = {overall_witness[0]}, case = {overall_witness[1]}, rho = {overall_witness[2]}")
    print()
    print(f"Conclusion: K_5 EMPIRICAL ≤ {overall_max} (deep adversarial sweep, "
          f"{n_random_samples * len(cases) * len(primes)}+ random + {8**4 * len(cases) * len(primes)}+ adversarial trials)")


if __name__ == "__main__":
    main()
