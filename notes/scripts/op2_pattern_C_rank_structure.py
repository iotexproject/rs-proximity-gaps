#!/usr/bin/env python3 -u
"""Pattern C rank structure: is dim X_γ always = 1 for Pattern C supports?

If yes, this is the structural reason Pattern C contributes codim
2D - T - 2 (the v6 v2 bound).

Test: enumerate Pattern C support tuples on [n=12], for each one and a few
random γ-tuples, compute dim X_γ. Check if it's always 1.
"""

import sys
import numpy as np
from itertools import combinations
from collections import Counter
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_clique_scan import rank_mod, kernel_mod
from op2_tet_consolidated import make_NEs
from op2_pattern_C_analysis import is_pattern_C
from op2_subperiod_test import find_sub_tet


def construct_x_gamma_basis(Es, gammas, L, p, c):
    """X_γ = {(ĥ_j) : Σ ĥ_j Λ_{E_j} = 0 ∧ Σ γ_j ĥ_j Λ_{E_j} = 0}."""
    m = len(Es)
    w = len(Es[0])
    n_coeffs_out = c + w  # ĥ_j Λ_{E_j} has degree at most c-1+w, so c+w coeffs
    n_vars = m * c

    def lambda_E(E):
        poly = [1]
        for j_ in E:
            new = [0] * (len(poly) + 1)
            for i, ci in enumerate(poly):
                new[i] = (new[i] - L[j_] * ci) % p
                new[i + 1] = (new[i + 1] + ci) % p
            poly = new
        return poly

    A = np.zeros((2 * n_coeffs_out, n_vars), dtype=np.int64)
    for j in range(m):
        lam = lambda_E(Es[j])
        for k in range(c):
            var_idx = j * c + k
            for i in range(len(lam)):
                deg = k + i
                if deg < n_coeffs_out:
                    A[deg, var_idx] = (A[deg, var_idx] + lam[i]) % p
                    A[n_coeffs_out + deg, var_idx] = (
                        A[n_coeffs_out + deg, var_idx] + gammas[j] * lam[i]) % p
    return kernel_mod(A, p)


def dim_x_gamma(Es, gammas, L, p, c):
    return len(construct_x_gamma_basis(Es, gammas, L, p, c))


def enumerate_and_classify_C(n, p, n_supports_max=None):
    """Find all Pattern C support tuples on [n], compute dim X_γ for each."""
    k = n // 2; c = 3
    D = n - k; w = D - c
    omega = find_omega(n, p)
    if omega is None: return None
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))
    print(f"  Total size-{w} supports on [{n}]: {len(all_supports)}")

    rng = np.random.default_rng(0)
    pattern_C_count = 0
    dim_dist = Counter()
    examples = []

    # Sample 4-tuples of supports
    for trial in range(20000):
        idx = rng.choice(len(all_supports), size=4, replace=False)
        Es = [all_supports[i] for i in idx]
        if not is_pattern_C(Es, n): continue
        if find_sub_tet(Es, n): continue  # has sub-tet → not pure Pattern C
        pattern_C_count += 1
        # Test dim X_γ at 3 random γ's
        dims_at_gammas = []
        for trial_g in range(3):
            gammas = (rng.choice(p - 1, size=4, replace=False) + 1).tolist()
            d = dim_x_gamma(Es, gammas, L, p, c)
            dims_at_gammas.append(d)
        dim_dist[tuple(dims_at_gammas)] += 1
        if len(examples) < 3 and tuple(dims_at_gammas) != (1, 1, 1):
            examples.append((Es, dims_at_gammas))
        if pattern_C_count >= 100: break
    print(f"  Pattern C configs found: {pattern_C_count}")
    print(f"  dim X_γ distribution (across 3 random γ-tuples):")
    for k_, v in dim_dist.most_common(5):
        print(f"    {k_}: {v}")
    if examples:
        print(f"  Non-uniform-dim examples: {examples[:3]}")
    return pattern_C_count, dim_dist


def test_dim_constant_across_gamma():
    """For a fixed Pattern C support, vary γ and check dim X_γ is constant."""
    n, k, c = 12, 6, 3
    D = n - k; w = D - c
    p = 1009
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    Es_C = [(3, 7, 11), (1, 7, 10), (0, 1, 4), (2, 9, 10)]
    print(f"=== Test dim X_γ stability for Pattern C Es={Es_C} ===")
    print(f"  {'γ':>30} {'dim X_γ':>10}")
    rng = np.random.default_rng(0)
    for trial in range(20):
        gammas = (rng.choice(p - 1, size=4, replace=False) + 1).tolist()
        d = dim_x_gamma(Es_C, gammas, L, p, c)
        print(f"  {str(gammas):>30} {d:>10}")


def find_pattern_C_basis_structure():
    """Inspect the basis vector of X_γ for a Pattern C support.
    Look for combinatorial structure (e.g., is some ĥ_j ≡ 0?)."""
    n, k, c = 12, 6, 3
    D = n - k; w = D - c
    p = 1009
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    Es_C = [(3, 7, 11), (1, 7, 10), (0, 1, 4), (2, 9, 10)]
    gammas = [3, 5, 7, 11]
    basis = construct_x_gamma_basis(Es_C, gammas, L, p, c)
    print(f"\n=== X_γ basis for Pattern C Es={Es_C}, γ={gammas} ===")
    for i, v in enumerate(basis):
        h = [v[j*c:(j+1)*c] for j in range(4)]
        print(f"  basis[{i}]:")
        for j in range(4):
            non_zero = any(int(x) != 0 for x in h[j])
            print(f"    ĥ_{j} (E={Es_C[j]}) = {[int(x) for x in h[j]]} ({'NONZERO' if non_zero else 'ZERO'})")


if __name__ == '__main__':
    n, k, c = 12, 6, 3
    p = 1009
    print(f"=== Pattern C rank structure at n={n} c={c} ===")
    enumerate_and_classify_C(n, p)
    print()
    test_dim_constant_across_gamma()
    print()
    find_pattern_C_basis_structure()
