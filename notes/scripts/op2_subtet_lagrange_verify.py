#!/usr/bin/env python3 -u
"""Verify Lemma 2.1 (Sub-tet Lagrange diagonality, Note 0109) numerically.

Setup: V ⊂ [n] with |V|=w'+1, w' < w. m' = w'+1 supports E_i ⊂ [n] of size
w with V \ {v_i} ⊂ E_i. For (ĥ_j) ∈ X_γ_sub (the m'-fold twisted syzygy
module), evaluation at L_{v_i} forces ĥ_i(L_{v_i}) = 0 ∀ i.

Test: pick V with |V| = 3 (w'=2), sub-tet supports of size w=3 over [n=12],
construct X_γ_sub explicitly. Verify ĥ_i(L_{v_i}) = 0 for all i.

Then compute dim X_γ_sub and the codim of V_tet_sub(V) in (s_1, s_2)-space.
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_clique_scan import rank_mod, kernel_mod
from op2_tet_consolidated import make_NEs


def lambda_E(E, L, p):
    """Λ_E(z) = ∏_{j ∈ E}(z - L_j) coefficients, low-to-high."""
    poly = [1]
    for j in E:
        new = [0] * (len(poly) + 1)
        for i, ci in enumerate(poly):
            new[i] = (new[i] - L[j] * ci) % p
            new[i + 1] = (new[i + 1] + ci) % p
        poly = new
    return poly


def construct_x_gamma_basis(Es, gammas, L, p, c):
    """Construct X_γ for the m supports E_j of size w with γ_j.

    X_γ = {(ĥ_j) ∈ (F_p[x]_{<c})^m : Σ ĥ_j Λ_{E_j} = 0 ∧ Σ γ_j ĥ_j Λ_{E_j} = 0}.

    Each ĥ_j has c coefficients. Total dim of (ĥ_j) space = mc.
    Each constraint Σ ĥ_j Λ_{E_j} ≡ 0 in F_p[x]_{<w+c}: gives w+c equations.
    Two constraints (with γ): total 2(w+c) equations.

    Return basis of X_γ as list of (m × c) coefficient arrays.
    """
    m = len(Es)
    w = len(Es[0])
    deg_lambda = w  # each Λ_E has degree w
    out_deg = c + deg_lambda - 1  # max degree of ĥ_j Λ_{E_j}
    # ĥ_j Λ_{E_j} has degree at most c-1 + w. So result has w + c coefficients.
    n_coeffs_out = c + deg_lambda  # degrees 0, 1, ..., c+w-1
    # Variable space: m × c, ordered as (j, k) with k = 0, ..., c-1
    n_vars = m * c
    # Constraint matrix: 2 * n_coeffs_out × n_vars
    A = np.zeros((2 * n_coeffs_out, n_vars), dtype=np.int64)
    lambdas = [lambda_E(E, L, p) for E in Es]
    for j in range(m):
        lam = lambdas[j]  # length w+1
        for k in range(c):
            # ĥ_j has coeff h_{j,k} at degree k
            # Contributes h_{j,k} · lam[i] to degree (k+i) of result
            var_idx = j * c + k
            for i in range(len(lam)):
                deg = k + i
                if deg < n_coeffs_out:
                    A[deg, var_idx] = (A[deg, var_idx] + lam[i]) % p
                    A[n_coeffs_out + deg, var_idx] = (A[n_coeffs_out + deg, var_idx] + gammas[j] * lam[i]) % p
    # Find ker A
    return kernel_mod(A, p), n_vars


def evaluate_h_at_L(h_coeffs, L_v, p, c):
    """h(L_v) given c coefficients of h."""
    result = 0
    L_pow = 1
    for k in range(c):
        result = (result + h_coeffs[k] * L_pow) % p
        L_pow = (L_pow * L_v) % p
    return result


def verify_sub_tet_lagrange(V, Es, gammas, L, p, c):
    """Verify ĥ_i(L_{v_i}) = 0 for all (ĥ_j) ∈ X_γ_sub and all i = 1, ..., w'+1.

    V is the sub-tet vertex set; Es should be ordered such that E_i ⊃ V \ {V[i]}.
    """
    m = len(Es)
    ker, n_vars = construct_x_gamma_basis(Es, gammas, L, p, c)
    if not ker:
        return True, 0, "X_γ = {0}"
    msgs = []
    for v_basis in ker:
        # v_basis is m*c-dim vector; reshape to m × c
        h = [v_basis[i*c:(i+1)*c] for i in range(m)]
        for i, v_i in enumerate(V):
            val = evaluate_h_at_L(h[i], L[v_i], p, c)
            if val != 0:
                msgs.append(f"  basis vec {ker.index(v_basis)}: ĥ_{i}(L_{v_i}) = {val} ≠ 0")
    if msgs:
        return False, len(ker), "\n".join(msgs)
    return True, len(ker), f"all ĥ_i(L_{{v_i}}) = 0 verified ({len(ker)} basis vectors)"


def test_sub_tet():
    """Run sub-tet Lagrange test at n=12 c=3 w'=2."""
    n, k, c = 12, 6, 3
    D = n - k; w = D - c
    p = 1009
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"=== Sub-tet Lagrange diagonality verification at n={n} c={c} ===")
    # Pattern A example from sub-tet test:
    # Es=[(7,8,9), (3,4,9), (2,10,11), (3,7,8)]
    # Sub-tet V=(3,7,9), mapping={3:0, 7:1, 9:3}
    # So sub-tet supports are (E_0, E_1, E_3) covering V\{3}={7,9}, V\{7}={3,9}, V\{9}={3,7}.
    print("\nPattern A example: V=(3,7,9), sub-tet supports E_0,E_1,E_3 (skip E_2):")
    V = (3, 7, 9)
    Es_sub = [(7, 8, 9), (3, 4, 9), (3, 7, 8)]
    # Order matters: Es_sub[i] ⊃ V \ {V[i]}, so:
    # V[0]=3: Es_sub[0] ⊃ {7,9} ✓ (E_0=(7,8,9))
    # V[1]=7: Es_sub[1] ⊃ {3,9} ✓ (E_1=(3,4,9))
    # V[2]=9: Es_sub[2] ⊃ {3,7} ✓ (E_3=(3,7,8))
    gammas_sub = [3, 5, 7]
    ok, ker_dim, msg = verify_sub_tet_lagrange(V, Es_sub, gammas_sub, L, p, c)
    print(f"  ker dim X_γ_sub = {ker_dim}")
    print(f"  Lemma 2.1 holds: {ok}")
    print(f"  {msg}")

    # Compare: full tet at n=12 c=3 w=3
    print("\nFull tet at V=(0,1,2,3) for comparison:")
    V_full = (0, 1, 2, 3)
    Es_full = [tuple(sorted(set(V_full) - {v})) for v in V_full]
    gammas_full = [2, 3, 5, 7]
    ok, ker_dim, msg = verify_sub_tet_lagrange(V_full, Es_full, gammas_full, L, p, c)
    print(f"  ker dim X_γ = {ker_dim}, formula (w-1)(c-1) = {(w-1)*(c-1)}")
    print(f"  Theorem 1 (Note 0099) holds: {ok}")
    print(f"  {msg}")

    # Sub-tet with another w'=2 example
    print("\nAnother sub-tet w'=2: V=(0,1,2), supports of size 3:")
    V2 = (0, 1, 2)
    # Need 3 supports E_i of size 3 with V \ {V[i]} ⊂ E_i, plus extra vertex.
    # E_0 ⊃ {1, 2}: pick (1, 2, 5)
    # E_1 ⊃ {0, 2}: pick (0, 2, 6)
    # E_2 ⊃ {0, 1}: pick (0, 1, 7)
    Es_sub2 = [(1, 2, 5), (0, 2, 6), (0, 1, 7)]
    gammas_sub2 = [11, 13, 17]
    ok, ker_dim, msg = verify_sub_tet_lagrange(V2, Es_sub2, gammas_sub2, L, p, c)
    print(f"  ker dim X_γ_sub = {ker_dim}")
    print(f"  Lemma 2.1 holds: {ok}")
    print(f"  {msg}")

    # Vary γ's: dim X_γ_sub stable?
    print("\nVary γ's for V=(0,1,2), Es_sub2 — track ker dim:")
    for trial_gammas in [[3, 5, 7], [11, 13, 17], [2, 4, 6], [100, 200, 300]]:
        ok, ker_dim, _ = verify_sub_tet_lagrange(V2, Es_sub2, trial_gammas, L, p, c)
        print(f"  γ={trial_gammas}: ker dim X_γ_sub = {ker_dim}, ok = {ok}")


if __name__ == '__main__':
    test_sub_tet()
