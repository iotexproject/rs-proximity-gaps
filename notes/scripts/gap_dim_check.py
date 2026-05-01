"""
gap_dim_check.py — Determine dim(V(r₀-1, r₁, r₂)) in full A^w.

THE GAP: We proved V₀₁₂=∅ on bivariate flat (σ₂=...=0) when w∤n.
Need: codim(V₀₁₂) ≥ 3 in A^w, i.e., dim(V₀₁₂) ≤ w-3.

Method: brute-force count |V₀₁₂(F_p)| for several primes p.
If |V₀₁₂| ~ p^d, then dim = d. We need d ≤ w-3.

Also check: V₀₁ (2 equations), V₀₁₂ (3 equations), V_all (all w equations).
Expected dimensions: w-2, w-3, 0.
"""

import itertools
from math import gcd

def compute_ri_mod_p(sigma, n, p):
    """Compute [r₀,...,r_{w-1}] mod p via companion matrix iteration.
    sigma = [σ₁,...,σ_w] (0-indexed: sigma[j] = σ_{j+1}).
    Returns [r₀, r₁, ..., r_{w-1}] mod p.
    """
    w = len(sigma)
    # Precompute last column of companion matrix
    # x^w ≡ σ₁x^{w-1} - σ₂x^{w-2} + ... + (-1)^{w+1}σ_w
    # C[j][w-1] = coeff of x^j in (x^w mod Λ) = (-1)^{w+1-j} σ_{w-j}
    # σ_{w-j} = sigma[w-1-j]
    last_col = [0] * w
    for j in range(w):
        sign = 1 if (w + 1 - j) % 2 == 0 else -1
        last_col[j] = (sign * sigma[w - 1 - j]) % p

    # State: [c₀, c₁, ..., c_{w-1}] = coeffs of x^step mod Λ
    state = [0] * w
    state[0] = 1  # x^0 = 1

    for _ in range(n):
        top = state[w - 1]
        new_state = [(top * last_col[0]) % p]
        for j in range(1, w):
            new_state.append((state[j - 1] + top * last_col[j]) % p)
        state = new_state

    # state[j] = coefficient of x^j in x^n mod Λ
    # R(x) = r₀x^{w-1} + r₁x^{w-2} + ... + r_{w-1}
    # So r_i = state[w-1-i]
    return [state[w - 1 - i] for i in range(w)]


def count_varieties(n, w, p):
    """Count |V₀₁(F_p)|, |V₀₁₂(F_p)|, |V_all(F_p)| in full A^w."""
    count_01 = 0
    count_012 = 0
    count_all = 0
    solutions_012 = []

    for sigma in itertools.product(range(p), repeat=w):
        ri = compute_ri_mod_p(list(sigma), n, p)
        if ri[0] != 1 % p:
            continue
        # r₀ = 1
        if ri[1] != 0:
            count_01 += 0  # r₁ ≠ 0
            continue
        # r₀ = 1, r₁ = 0
        count_01 += 1
        if ri[2] != 0:
            continue
        # r₀ = 1, r₁ = 0, r₂ = 0
        count_012 += 1
        solutions_012.append(list(sigma))
        if all(ri[j] == 0 for j in range(1, w)):
            count_all += 1

    return count_01, count_012, count_all, solutions_012


def jacobian_rank(sigma, n, w, p):
    """Compute rank of Jacobian [∂r_i/∂σ_j] at point sigma, numerically.
    Uses finite differences: ∂r_i/∂σ_j ≈ (r_i(σ+e_j) - r_i(σ)) / 1 (mod p).
    """
    ri_base = compute_ri_mod_p(sigma, n, p)
    # Build Jacobian rows for r₀-1, r₁, r₂
    jac = []
    for eq_idx in range(min(3, w)):
        row = []
        for var_j in range(w):
            sigma_pert = list(sigma)
            sigma_pert[var_j] = (sigma_pert[var_j] + 1) % p
            ri_pert = compute_ri_mod_p(sigma_pert, n, p)
            if eq_idx == 0:
                deriv = (ri_pert[0] - ri_base[0]) % p
            else:
                deriv = (ri_pert[eq_idx] - ri_base[eq_idx]) % p
            row.append(deriv)
        jac.append(row)
    # Compute rank mod p (Gaussian elimination)
    return matrix_rank_mod_p(jac, p)


def matrix_rank_mod_p(mat, p):
    """Rank of matrix over F_p."""
    m = [list(row) for row in mat]
    rows, cols = len(m), len(m[0]) if m else 0
    rank = 0
    for col in range(cols):
        # Find pivot
        pivot = None
        for row in range(rank, rows):
            if m[row][col] % p != 0:
                pivot = row
                break
        if pivot is None:
            continue
        m[rank], m[pivot] = m[pivot], m[rank]
        inv = pow(m[rank][col], p - 2, p)
        for c in range(cols):
            m[rank][c] = (m[rank][c] * inv) % p
        for row in range(rows):
            if row != rank and m[row][col] != 0:
                factor = m[row][col]
                for c in range(cols):
                    m[row][c] = (m[row][c] - factor * m[rank][c]) % p
        rank += 1
    return rank


def main():
    print("=" * 70)
    print("GAP DIMENSION CHECK: dim(V(r₀-1, r₁, r₂)) in full A^w")
    print("=" * 70)

    # Test configurations: (n, w) with w ∤ n
    configs = [
        # w=3
        (7, 3), (8, 3), (10, 3), (11, 3), (13, 3),
        # w=4
        (7, 4), (9, 4), (10, 4), (11, 4), (13, 4),
        # w=5
        (7, 5), (8, 5), (11, 5),
    ]

    # Primes to test (need several to estimate dimension)
    primes_by_w = {
        3: [11, 13, 17, 19, 23, 29, 31, 37],
        4: [7, 11, 13, 17, 19, 23],
        5: [7, 11, 13],
    }

    for n, w in configs:
        if n <= w:
            continue
        divides = "w|n" if n % w == 0 else "w∤n"
        print(f"\n{'='*60}")
        print(f"n={n}, w={w}  ({divides})  expected dim(V₀₁₂)={w-3}")
        print(f"{'='*60}")

        primes = primes_by_w.get(w, [7, 11, 13])
        results = []

        for p in primes:
            if p <= n:
                # Need p > n for proper RS code behavior
                continue
            cnt_01, cnt_012, cnt_all, sols = count_varieties(n, w, p)
            results.append((p, cnt_01, cnt_012, cnt_all))
            print(f"  p={p:3d}: |V₀₁|={cnt_01:6d}  |V₀₁₂|={cnt_012:5d}  |V_all|={cnt_all:4d}", end="")

            # Check Jacobian at solution points
            if sols:
                ranks = []
                for s in sols[:5]:  # check first 5
                    r = jacobian_rank(s, n, w, p)
                    ranks.append(r)
                print(f"  Jac ranks: {ranks}", end="")
            print()

        # Estimate dimensions by log-log regression
        if len(results) >= 2:
            import math
            print(f"\n  Dimension estimates (log|V|/log p):")
            for label, idx in [("V₀₁", 1), ("V₀₁₂", 2), ("V_all", 3)]:
                pairs = [(r[0], r[idx]) for r in results if r[idx] > 0]
                if len(pairs) >= 2:
                    # Use last two points for slope
                    p1, c1 = pairs[-2]
                    p2, c2 = pairs[-1]
                    if c1 > 0 and c2 > 0:
                        slope = (math.log(c2) - math.log(c1)) / (math.log(p2) - math.log(p1))
                        print(f"    {label}: slope ≈ {slope:.2f}  (expect {w-1-idx} for regular seq)")
                    else:
                        print(f"    {label}: count dropped to 0")
                elif pairs:
                    print(f"    {label}: only one nonzero point ({pairs[0]})")
                else:
                    print(f"    {label}: all zero!")


    # Detailed analysis for w=3
    print(f"\n{'='*60}")
    print("DETAILED w=3 ANALYSIS: V₀₁₂ should be 0-dimensional (finite)")
    print(f"{'='*60}")

    for n in [7, 8, 10, 11, 13]:
        w = 3
        if n <= w:
            continue
        print(f"\n  n={n}, w=3:")
        for p in [11, 13, 17, 19, 23, 29, 31, 37, 41, 43]:
            if p <= n:
                continue
            cnt_01, cnt_012, cnt_all, sols = count_varieties(n, w, p)
            print(f"    p={p:3d}: |V₀₁₂|={cnt_012:4d}  solutions={sols[:3]}{'...' if len(sols)>3 else ''}")


    # Detailed analysis for w=4
    print(f"\n{'='*60}")
    print("DETAILED w=4 ANALYSIS: V₀₁₂ should be 1-dimensional (~p)")
    print(f"{'='*60}")

    for n in [7, 9, 10, 11]:
        w = 4
        if n <= w:
            continue
        print(f"\n  n={n}, w=4:")
        for p in [11, 13, 17, 19, 23]:
            if p <= n:
                continue
            cnt_01, cnt_012, cnt_all, sols = count_varieties(n, w, p)
            print(f"    p={p:3d}: |V₀₁₂|={cnt_012:5d}  |V₀₁₂|/p={cnt_012/p:.2f}")


    print(f"\n{'='*60}")
    print("KEY QUESTION: Is dim(V₀₁₂) ≤ w-3 for all (n,w) with w∤n?")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
