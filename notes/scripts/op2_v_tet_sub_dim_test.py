#!/usr/bin/env python3 -u
"""Direct test: what is dim V_tet_sub at c=4 w'=3 sub-tet for fixed (E_1, ..., E_4)?

Two tests:

(A) Linear-span upper bound: V_tet_sub ⊂ Σ_γ ker A(γ). Sample many γ's,
    accumulate the linear span of all observed kernels. Final dim is an
    upper bound for dim V_tet_sub (and likely equality for irreducible families).

(B) Constructive lower bound: parameterize (s_1, s_2) = (Λ_V h_1, Λ_V h_2)
    with h_1, h_2 ∈ F_p[x]_{<D-w'-1}. By the Lagrange-diagonal forced-zero
    argument (s_2 vanishes on L_V because m ≥ 3 distinct supports share v_l),
    every (s_1, s_2) in V_tet_sub has this form. We then check the additional
    constraint h_1(L_{u_i}) + γ_i h_2(L_{u_i}) = 0 with γ_i ∈ F_p^* distinct.

If (A) gives dim 8 and (B) gives dim 8, the conjecture in Note 0113 is wrong.
If (A) gives dim 5, my claim is wrong somewhere.
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_clique_scan import rank_mod, kernel_mod
from op2_tet_consolidated import make_NEs, solve_for_witness


def linear_span_of_kers(NEs, p, D, c, n_gammas=200, seed=0):
    """Sample γ-tuples, accumulate all ker A(γ) into a single matrix; return dim."""
    rng = np.random.default_rng(seed)
    m = len(NEs)
    accumulated = []
    for trial in range(n_gammas):
        gammas = (rng.choice(p - 1, size=m, replace=False) + 1).tolist()
        A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
        for v in ker:
            accumulated.append(v)
    if not accumulated:
        return 0
    M = np.array(accumulated, dtype=np.int64) % p
    return rank_mod(M, p)


def build_sub_tet_c4(n, p, V, U, w):
    """Build E_i = (V \\ {v_i}) ∪ {u_i} for i=1..4."""
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    Es = []
    for i, v_i in enumerate(V):
        E_i = tuple(sorted([v for v in V if v != v_i] + [U[i]]))
        Es.append(E_i)
    return Es, L


def lagrange_param_check(Es, V, U, L, p, D, c):
    """Test (B): (s_1, s_2) parametrized by h_1, h_2 ∈ F_p[x]_{<D-(w'+1)}.
    Λ_V is degree w'+1, so h_l of degree < D - (w'+1).
    For each (h_1, h_2), check (s_1, s_2) = (Λ_V h_1, Λ_V h_2) satisfies:
    s_1 + γ_i s_2 ∈ ker N_{E_i} for some γ_i ∈ F_p^* (distinct).

    Then count: how many of the p^{2(D-w'-1)} parameterized points are in V_tet_sub?
    """
    w_plus_1 = len(V)  # w'+1
    h_deg_max = D - w_plus_1  # h ∈ F_p[x]_{<h_deg_max}, so deg < h_deg_max
    # Build Λ_V coefficient vector: Λ_V(x) = ∏(x - L_v) for v ∈ V
    Lambda_V = [1]  # constant poly
    for v in V:
        Lambda_V = poly_mul(Lambda_V, [(-L[v]) % p, 1], p)
    # deg Λ_V = |V| = w_plus_1
    print(f"  Λ_V degree = {len(Lambda_V) - 1}, h degree < {h_deg_max}")

    # For each i, compute h_2(L_{u_i}) coefficients via "row vector at x = L_{u_i}".
    # h_2(L_{u_i}) = sum_k h_2[k] * L_{u_i}^k.
    NEs = make_NEs(Es, L, p, D, c, w=D - c)

    # Sample h_1, h_2 and check membership.
    rng = np.random.default_rng(7)
    n_trials = 5000
    n_in_v_tet_sub = 0
    n_with_distinct_gammas = 0
    h_dim = h_deg_max
    if h_dim <= 0:
        print(f"  h_dim = {h_dim} (≤0), parameterization empty.")
        return
    for trial in range(n_trials):
        h1 = rng.integers(0, p, h_dim)
        h2 = rng.integers(0, p, h_dim)
        # Compute s_l = Λ_V * h_l (deg < D)
        s1 = poly_mul(h1.tolist(), Lambda_V, p)
        s2 = poly_mul(h2.tolist(), Lambda_V, p)
        # Pad to length D
        s1 = s1 + [0] * (D - len(s1))
        s2 = s2 + [0] * (D - len(s2))
        s1 = np.array(s1[:D], dtype=np.int64)
        s2 = np.array(s2[:D], dtype=np.int64)
        # For each E_i, derive γ_i if exists
        gammas = []
        ok = True
        for i, N in enumerate(NEs):
            aE = (N @ s2) % p
            bE = (N @ s1) % p
            nz = next((j for j in range(c) if aE[j] != 0), None)
            if nz is None:
                if any(bE):
                    ok = False; break
                # Both zero: γ_i can be anything; pick a placeholder
                gammas.append(None); continue
            g = (-int(bE[nz]) * pow(int(aE[nz]), p - 2, p)) % p
            # Check proportionality
            prop = all(
                (int(aE[j_]) * int(bE[k_]) - int(aE[k_]) * int(bE[j_])) % p == 0
                for j_ in range(c) for k_ in range(c)
            )
            if not prop or g == 0:
                ok = False; break
            gammas.append(g)
        if not ok: continue
        n_in_v_tet_sub += 1
        # Check distinct gammas (for None entries, can fill in)
        non_none = [g for g in gammas if g is not None]
        if len(set(non_none)) == len(non_none):
            # Check no None forced collision
            # If any None, can pick a fresh γ from F_p^* \ {non_none}, exists if |non_none| < p-1
            if all(g is not None for g in gammas) or len(non_none) < p - 1:
                n_with_distinct_gammas += 1
    print(f"  Test (B): of {n_trials} random (h_1, h_2): "
          f"{n_in_v_tet_sub} ∈ V_tet_sub (any γ), "
          f"{n_with_distinct_gammas} with distinct γ ∈ F_p^*")
    print(f"  → fraction in V_tet_sub: {n_in_v_tet_sub / n_trials:.4f}")
    if n_with_distinct_gammas > 0:
        # Implies parameterization image has dim ≥ 2*h_dim, density 1
        print(f"  → param image (s_1,s_2) ⊂ V_tet_sub of dim ≥ {2 * h_dim}")


def poly_mul(a, b, p):
    """Multiply two polynomials (lists of coefs) mod p."""
    out = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[i + j] = (out[i + j] + int(ai) * int(bj)) % p
    return out


def main():
    n = 16; c = 4
    primes = [17, 97, 193, 257, 449]
    for p in primes:
        if (p - 1) % n != 0:
            print(f"\np={p}: skipping (n={n} doesn't divide p-1)")
            continue
        D = n - n // 2  # k = n//2
        w = D - c
        # Sub-tet at w' = w - 1 = 3: V has 4 vertices, 4 supports, each E_i has 1 extra
        V = [0, 1, 2, 3]      # V ⊂ [n] of size 4
        U = [4, 5, 6, 7]      # one extra per support
        Es, L = build_sub_tet_c4(n, p, V, U, w)
        print(f"\n=== p={p}, n={n}, c={c}, D={D}, w={w} ===")
        print(f"V = {V}, U = {U}")
        print(f"E_i = (V \\ {{v_i}}) ∪ {{u_i}}: {Es}")

        NEs = make_NEs(Es, L, p, D, c, w)

        # Test (A): linear span of all ker A(γ)
        print("\n  Test (A): linear span of ⋃_γ ker A(γ)")
        for n_g in [50, 200, 1000]:
            d = linear_span_of_kers(NEs, p, D, c, n_gammas=n_g, seed=42)
            print(f"    {n_g} γ samples: dim Σ ker A = {d}")
            if d == 2 * D: break  # full

        # Test (B): parameterization (Λ_V h_1, Λ_V h_2)
        print("\n  Test (B): (s_1, s_2) = (Λ_V h_1, Λ_V h_2) parameterization")
        lagrange_param_check(Es, V, U, L, p, D, c)


if __name__ == '__main__':
    main()
