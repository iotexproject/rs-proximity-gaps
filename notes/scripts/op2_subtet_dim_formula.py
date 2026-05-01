#!/usr/bin/env python3 -u
"""Derive a general formula for dim X_gamma_sub in the sub-tet setting.

Analysis from algebraic reduction (Note 0099 port):

For V = {v_1, ..., v_{w'+1}}, E_i of size w with V \\ {v_i} \\subset E_i and
v_i \\notin E_i, set U_i := E_i \\setminus (V \\ {v_i}), |U_i| = w - w'.
After forced zero h_i(L_{v_i}) = 0 we write h_i = (x - L_{v_i}) q_i with
deg q_i < c - 1. Then:

   sum_j h_j Lambda_{E_j} = Lambda_V(x) * sum_j q_j(x) Pi_{U_j}(x)

X_gamma_sub corresponds to the kernel of the map
   T : (q_j) -> (sum q_j Pi_{U_j}, sum gamma_j q_j Pi_{U_j})
acting on (F_p[x]_{<c-1})^{w'+1} -> (F_p[x]_{<c+w-w'})^2.

Variable space dim: (w'+1)(c-1).
Codomain dim: 2(c + w - w').

Generic rank: min((w'+1)(c-1), 2(c+w-w')).

Conjecture A: dim X_gamma_sub = max(0, (w'+1)(c-1) - 2(c+w-w'))
            = max(0, (w'-1)(c-1) - 2(w-w'))

Setting w'=w gives (w-1)(c-1) ✓ (matches Note 0099).

When extras U_i have collisions (Pi_{U_i} = Pi_{U_j} for i ≠ j or other
algebraic dependence), dim X_gamma_sub may exceed Conjecture A.
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_subtet_lagrange_verify import (lambda_E, construct_x_gamma_basis,
                                          evaluate_h_at_L)


def conjecture_A(w_prime, w, c):
    """Generic dim X_gamma_sub formula.

    Output coefficients: q_j Pi_{U_j} has deg <= (c-2) + (w - w') = c+w-w'-2,
    so c+w-w'-1 coefficients. Two such constraints (T1, T2): codomain dim
    2(c+w-w'-1).
    """
    return max(0, (w_prime + 1) * (c - 1) - 2 * (c + w - w_prime - 1))


def make_sub_tet_supports(V, n, w, rng, force_distinct_extras=True,
                           coincide_extras=None):
    """Pick extras for each i so E_i = (V \\ {v_i}) ∪ U_i, v_i ∉ E_i.

    coincide_extras: if not None, dict {i: u} forcing U_i to be a singleton {u}.
    """
    w_prime = len(V) - 1
    extras_size = w - w_prime
    available = [v for v in range(n) if v not in V]
    Es = []
    used_extras = []
    for i in range(len(V)):
        v_i = V[i]
        # Pool excludes V[i] (must not include it), and we want U_i ⊂ [n] \ V
        pool = list(available)
        if coincide_extras is not None and i in coincide_extras:
            U_i = coincide_extras[i]
        else:
            if force_distinct_extras:
                pool_distinct = [v for v in pool
                                 if not any(v in u for u in used_extras)]
                pool = pool_distinct if len(pool_distinct) >= extras_size else pool
            U_i = tuple(rng.choice(pool, size=extras_size, replace=False).tolist())
        used_extras.append(set(U_i))
        E_i = tuple(sorted(set(V) - {v_i} | set(U_i)))
        Es.append(E_i)
    return Es


def measure_dim(V, Es, gammas, L, p, c):
    ker, _ = construct_x_gamma_basis(Es, gammas, L, p, c)
    return len(ker)


def test_conjecture_A():
    """Test conjecture A across (n, c, w'): with distinct extras, dim X = max(0, ...)?"""
    print("=== Conjecture A test: distinct extras ===")
    print(f"{'n':>4}{'c':>4}{'w':>4}{'wp':>4}{'pred':>6}  empirical (10 trials)")
    rng = np.random.default_rng(0)
    for (n, c) in [(12, 3), (16, 3), (16, 4), (20, 4), (20, 5)]:
        k = n // 2; w = n - k - c
        p_candidates = [97, 193, 257, 449, 577, 1009, 1153]
        p = next((q for q in p_candidates if (q - 1) % n == 0), None)
        if p is None: continue
        omega = find_omega(n, p)
        L = [pow(omega, i, p) for i in range(n)]
        for w_prime in range(2, min(w + 1, n - 1)):
            pred = conjecture_A(w_prime, w, c)
            empirical = []
            for trial in range(10):
                V_pool = list(range(n))
                V = tuple(sorted(rng.choice(V_pool, size=w_prime + 1,
                                             replace=False).tolist()))
                Es = make_sub_tet_supports(V, n, w, rng,
                                            force_distinct_extras=True)
                # check valid sub-tet (V[i] ∉ E_i, V \ {V[i]} ⊂ E_i)
                if any(V[i] in Es[i] for i in range(len(V))):
                    continue
                gammas = (rng.choice(p - 1, size=w_prime + 1,
                                       replace=False) + 1).tolist()
                d = measure_dim(V, Es, gammas, L, p, c)
                empirical.append(d)
            if empirical:
                from collections import Counter
                ctr = Counter(empirical)
                most_common = ctr.most_common(1)[0]
                print(f"{n:>4}{c:>4}{w:>4}{w_prime:>4}{pred:>6}  "
                      f"counts={dict(ctr)}, mode={most_common[0]} "
                      f"({'matches' if most_common[0] == pred else 'MISMATCH'})")


def test_extras_collision_effect():
    """When U_i = U_j for some i, j: does dim X_gamma_sub increase?"""
    print("\n=== Extras collision effect (n=16 c=3 w=5 w'=3) ===")
    n, c, w_prime = 16, 3, 3
    k = n // 2; w = n - k - c
    p = 257
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    rng = np.random.default_rng(42)

    # All distinct
    V = (0, 1, 2, 3)
    print(f"\nV = {V}, all extras distinct:")
    Es = make_sub_tet_supports(V, n, w, rng, force_distinct_extras=True)
    if not any(V[i] in Es[i] for i in range(len(V))):
        gammas = [3, 5, 7, 11]
        d = measure_dim(V, Es, gammas, L, p, c)
        print(f"  Es={Es}, gammas={gammas}, dim X_sub = {d}, "
              f"pred (Conj A) = {conjecture_A(w_prime, w, c)}")

    print("\nForce U_0 = U_1 (collision pair):")
    # extras_size = w - w' = 5 - 3 = 2
    coincide_extras = {0: (4, 5), 1: (4, 5)}
    Es = make_sub_tet_supports(V, n, w, rng, force_distinct_extras=False,
                                coincide_extras=coincide_extras)
    # Add distinct extras for i=2, i=3
    # Need U_2, U_3 of size 2 from [n]\V = {4,..,15} not equal to {4,5}
    Es = list(Es)
    Es[2] = tuple(sorted(set(V) - {V[2]} | {6, 7}))
    Es[3] = tuple(sorted(set(V) - {V[3]} | {8, 9}))
    if not any(V[i] in Es[i] for i in range(len(V))):
        gammas = [3, 5, 7, 11]
        d = measure_dim(V, Es, gammas, L, p, c)
        print(f"  Es={Es}, gammas={gammas}, dim X_sub = {d}")

    print("\nForce U_0 = U_1 = U_2 (3-way collision):")
    Es = list(Es)
    Es[0] = tuple(sorted(set(V) - {V[0]} | {4, 5}))
    Es[1] = tuple(sorted(set(V) - {V[1]} | {4, 5}))
    Es[2] = tuple(sorted(set(V) - {V[2]} | {4, 5}))
    Es[3] = tuple(sorted(set(V) - {V[3]} | {6, 7}))
    if not any(V[i] in Es[i] for i in range(len(V))):
        gammas = [3, 5, 7, 11]
        d = measure_dim(V, Es, gammas, L, p, c)
        print(f"  Es={Es}, gammas={gammas}, dim X_sub = {d}")

    print("\nAll U_i equal (full collision):")
    Es = [tuple(sorted(set(V) - {V[i]} | {4, 5})) for i in range(len(V))]
    if not any(V[i] in Es[i] for i in range(len(V))):
        gammas = [3, 5, 7, 11]
        d = measure_dim(V, Es, gammas, L, p, c)
        print(f"  Es={Es}, gammas={gammas}, dim X_sub = {d}")


if __name__ == '__main__':
    test_conjecture_A()
    test_extras_collision_effect()
