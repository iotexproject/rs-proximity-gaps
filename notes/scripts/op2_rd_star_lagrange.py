#!/usr/bin/env python3 -u
"""Verify the rd-Pattern-C-star Lagrange structure (Lemma 3.1).

CLAIM: A Pattern C star (E_c central, E_a/E_b/E_d leaves with shared
vertices v_a/v_b/v_d) admits dim X_gamma >= 1 generically iff the polynomials
   Pi_{U_a}(x), Pi_{U_b}(x), Pi_{U_d}(x)
(each of degree c-1, where U_j := E_j \\ {v_j}) are LINEARLY DEPENDENT in
F_p[x]_{<c}.

In which case the basis vector of X_gamma has the form:
   h_j(x) = alpha_j * Lambda_{E_c}(x) / (x - L_{v_j})    for j leaf
   h_c(x) = -sum_{leaf j} alpha_j Pi_{U_j}(x)
where (alpha_a, alpha_b, alpha_d) span ker M, M being the 3x3 matrix whose
columns are the coefficients of Pi_{U_j}.

Derivation:
   sum_j h_j Lambda_{E_j} = Lambda_{E_c}(x) * (h_c + sum_{leaf} alpha_j Pi_{U_j}) = 0
   => h_c = -sum_{leaf} alpha_j Pi_{U_j}
   sum_j gamma_j h_j Lambda_{E_j} = Lambda_{E_c} * (gamma_c h_c + sum gamma_j alpha_j Pi_{U_j}) = 0
   => sum_{leaf} (gamma_j - gamma_c) alpha_j Pi_{U_j} = 0
For this to have nonzero (alpha_a, alpha_b, alpha_d) when (gamma_j - gamma_c)
are all nonzero, the Pi_{U_j} must be linearly dependent.

Thus the rd-Pattern-C-star condition = single polynomial equation
det(coefficients matrix of Pi_{U_a}, Pi_{U_b}, Pi_{U_d}) = 0 in F_p.
"""

import sys
import numpy as np
from itertools import combinations
from collections import Counter
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_pattern_C_rank_structure import (dim_x_gamma,
                                            construct_x_gamma_basis)
from op2_pattern_C_analysis import is_pattern_C
from op2_pattern_C_star_topology import intersection_graph, topology_signature
from op2_subperiod_test import find_sub_tet
from op2_rd_star_deep import extract_star_structure


def pi_U_coeffs(U, L, p, c):
    """Coefficients of Pi_U(x) = prod_{u in U} (x - L_u), low-to-high.
    Length c (since |U| = c - 1, deg = c - 1)."""
    poly = [1]
    for u in U:
        new = [0] * (len(poly) + 1)
        for i, ci in enumerate(poly):
            new[i] = (new[i] - L[u] * ci) % p
            new[i + 1] = (new[i + 1] + ci) % p
        poly = new
    while len(poly) < c:
        poly.append(0)
    return poly


def det_3x3_mod(M, p):
    """3x3 determinant mod p."""
    a, b, c_ = M[0]
    d, e, f = M[1]
    g, h, i = M[2]
    det = (a * e * i + b * f * g + c_ * d * h
           - c_ * e * g - b * d * i - a * f * h) % p
    return det


def rd_star_condition(Es, L, p, c):
    """Compute det(Pi_{U_j} coeffs) for the leaves. Returns 0 iff the leaves'
    Pi_{U_j} are linearly dependent (the conjectured rd-star condition)."""
    s = extract_star_structure(Es)
    if s is None: return None
    leaves = s['leaves']
    M = []
    for leaf in leaves:
        v_share = leaf['v_share']
        U = tuple(u for u in leaf['E'] if u != v_share)
        coeffs = pi_U_coeffs(U, L, p, c)
        M.append(coeffs)
    return det_3x3_mod(M, p)


def verify_correspondence(n, p, n_trials=300000):
    """Run many Pattern C stars; check rd_star_condition vs dim X_gamma."""
    k = n // 2; c = 3
    D = n - k; w = D - c
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))
    rng = np.random.default_rng(7)

    # Quadrants:
    #   det != 0, dim = 0  (generic)
    #   det != 0, dim >= 1 (FALSIFIES the claim)
    #   det == 0, dim = 0  (FALSIFIES)
    #   det == 0, dim >= 1 (rd-star)
    quadrants = Counter()
    examples = {q: [] for q in range(4)}
    n_star = 0
    for trial in range(n_trials):
        idx = rng.choice(len(all_supports), size=4, replace=False)
        Es = [all_supports[i] for i in idx]
        if not is_pattern_C(Es, n): continue
        if find_sub_tet(Es, n): continue
        edges = intersection_graph(Es)
        if topology_signature(edges, 4) != 'star': continue
        n_star += 1
        det = rd_star_condition(Es, L, p, c)
        if det is None: continue
        # Sample a few gammas to detect rd
        rd = True
        for tg in range(2):
            gammas = (rng.choice(p - 1, size=4, replace=False) + 1).tolist()
            d = dim_x_gamma(Es, gammas, L, p, c)
            if d == 0: rd = False; break
        q = (1 if det == 0 else 0) * 2 + (1 if rd else 0)
        quadrants[q] += 1
        if len(examples[q]) < 3:
            examples[q].append((Es, det, rd))
        if n_star >= 1500: break

    print(f"  Stars sampled: {n_star}")
    print(f"  Quadrant counts (det==0?, rd?):")
    for q in [0, 1, 2, 3]:
        det_zero = (q >> 1) == 1
        rd = (q & 1) == 1
        label = f"det={'0' if det_zero else '!=0'}, rd={'YES' if rd else 'NO'}"
        print(f"    {label}: {quadrants[q]}")
    return quadrants, examples


def basis_vector_matches_predicted_form(rd_star, L, p, c=3):
    """Verify the basis vector of X_gamma matches the predicted form."""
    s = extract_star_structure(rd_star)
    if s is None: return False, "not a star"
    rng = np.random.default_rng(0)
    gammas = (rng.choice(p - 1, size=4, replace=False) + 1).tolist()
    basis = construct_x_gamma_basis(rd_star, gammas, L, p, c)
    if not basis: return False, "X_gamma trivial"
    v = basis[0]
    h = [v[j*c:(j+1)*c] for j in range(4)]
    cidx = s['central_idx']
    leaves = s['leaves']

    # For each leaf, predict h_j as alpha_j * Lambda_{E_c}/(x - L_{v_j})
    E_c = s['E_c']
    L_E_c = [L[v] for v in E_c]
    predicted_match = []
    for leaf in leaves:
        j = leaf['idx']
        v_share = leaf['v_share']
        # Lambda_{E_c}/(x - L_{v_share}) has roots at the OTHER two L_{v_l}
        other_v = [vv for vv in E_c if vv != v_share]
        lag_poly = pi_U_coeffs(other_v, L, p, c)
        # h[j] should be alpha * lag_poly. Compare.
        # Find first nonzero coeff in lag_poly; ratio.
        idx_nz = next((i for i, x in enumerate(lag_poly) if x != 0), None)
        if idx_nz is None: continue
        alpha = (int(h[j][idx_nz]) * pow(int(lag_poly[idx_nz]), p-2, p)) % p
        match = all((int(h[j][k]) - alpha * lag_poly[k]) % p == 0
                    for k in range(c))
        predicted_match.append((j, alpha, match))
    return predicted_match


if __name__ == '__main__':
    n = 12; p = 1009
    print(f"=== rd-Pattern-C-star Lagrange-form verification at n={n} p={p} ===\n")
    print(f"Test: rd-star <=> det(Pi_{{U_a}}, Pi_{{U_b}}, Pi_{{U_d}}) coefficients = 0\n")
    quadrants, examples = verify_correspondence(n, p, n_trials=300000)

    print(f"\n=== Verifying basis vector form for det==0 examples ===")
    for ex_data in examples[3]:  # det==0 AND rd
        Es, det, rd = ex_data
        result = basis_vector_matches_predicted_form(Es, [pow(find_omega(n, p), i, p) for i in range(n)], p)
        print(f"  Es={Es}, det=0, rd=YES")
        if isinstance(result, list):
            for j, alpha, match in result:
                print(f"    leaf j={j}: alpha={alpha}, predicted match: {match}")
        else:
            print(f"    {result}")
