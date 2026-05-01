"""fit_G_alpha.py — try to fit a degree-≤R polynomial G(α) vanishing on V_δ.

For each of the 6 known Lemma-A falsifiers (rank-2 above-J f), and a few additional
rank-2 above-J cases for diversity, we:
  1. Brute-force enumerate V_δ ⊂ F_q^R (R=2, q=97).
  2. Extract the actual α-set.
  3. Build the linear system over F_q: monomials [α₁^i α₂^j : 0 ≤ i+j ≤ 2].
     Each (α₁, α₂) ∈ V_δ gives one equation. Solve for null space.
  4. Report:
       - |V_δ|
       - dim of degree-≤2 vanishing subspace (if ≥1, found a G)
       - dim of degree-≤1 vanishing subspace (linear forms vanishing on V_δ)
       - if degree-2 G exists, attempt to factor as L₁·L₂ (two lines through origin)
       - report which linear factors appear.

If for ALL above-J f (rank 2), V_δ is contained in zero set of a degree-2 polynomial:
  Direction A bound |V_δ| ≤ R q^(R-1) = 2q follows by Schwartz-Zippel.
"""
from __future__ import annotations
import sys, os, random
from itertools import product, combinations
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, parity_check, gauss_rank, matvec, modinv
from mds_decoder import is_above_johnson_sampling
from probe_step5_n32_studio import (
    P, N0, K0, R, N_R, W_J,
    evaluate_dft, fold_at_alpha, compute_corner_syndromes, min_wt_via_MDS,
)


CANDIDATES = [
    ((12, 18, 22), (59, 73, 36)),
    ((14, 18, 31), (90, 90, 88)),
    ((9, 19, 27),  (16, 86, 49)),
    ((13, 22, 30), (23, 17, 17)),
    ((9, 10, 22, 25, 26), (30, 38, 58, 50, 69)),
    ((14, 18, 28, 30), (91, 88, 70, 22)),
]

# Monomial ordering for degree-≤2 polynomials in (α₁, α₂):
#   index 0: 1
#   index 1: α₁
#   index 2: α₂
#   index 3: α₁²
#   index 4: α₁ α₂
#   index 5: α₂²
MONOMIALS = [(0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2)]
MON_NAMES = ["1", "α₁", "α₂", "α₁²", "α₁α₂", "α₂²"]


def eval_monomials(a1, a2, p):
    return [
        1,
        a1 % p,
        a2 % p,
        (a1 * a1) % p,
        (a1 * a2) % p,
        (a2 * a2) % p,
    ]


def gauss_kernel(M, n_cols, p):
    """Compute kernel of matrix M (rows=eqns, cols=unknowns) over F_p.
    Returns list of basis vectors."""
    A = [list(r) for r in M]
    n_rows = len(A)
    pivot_col_of_row = [-1] * n_rows
    pivot_row_of_col = [-1] * n_cols
    cur_row = 0
    for col in range(n_cols):
        if cur_row >= n_rows:
            break
        pr = None
        for r in range(cur_row, n_rows):
            if A[r][col] % p != 0:
                pr = r
                break
        if pr is None:
            continue
        A[cur_row], A[pr] = A[pr], A[cur_row]
        inv = modinv(A[cur_row][col], p)
        A[cur_row] = [(x * inv) % p for x in A[cur_row]]
        for rr in range(n_rows):
            if rr != cur_row and A[rr][col] % p != 0:
                ff = A[rr][col]
                A[rr] = [(A[rr][c] - ff * A[cur_row][c]) % p for c in range(n_cols)]
        pivot_col_of_row[cur_row] = col
        pivot_row_of_col[col] = cur_row
        cur_row += 1
    free_cols = [c for c in range(n_cols) if pivot_row_of_col[c] == -1]
    basis = []
    for fc in free_cols:
        v = [0] * n_cols
        v[fc] = 1
        for c in range(n_cols):
            if pivot_row_of_col[c] != -1:
                v[c] = (-A[pivot_row_of_col[c]][fc]) % p
        basis.append(v)
    return basis


def fit_vanishing(V_set, max_deg, p):
    """Fit polynomials of total degree ≤ max_deg vanishing on V_set ⊂ F_p^2.

    Returns list of basis polynomials in MONOMIAL coefficient form (length 6 for deg≤2,
    length 3 for deg≤1).
    """
    if max_deg == 1:
        # Use only first 3 monomials
        rows = []
        for a1, a2 in V_set:
            evs = eval_monomials(a1, a2, p)
            rows.append(evs[:3])
        return gauss_kernel(rows, 3, p)
    elif max_deg == 2:
        rows = []
        for a1, a2 in V_set:
            evs = eval_monomials(a1, a2, p)
            rows.append(evs)
        return gauss_kernel(rows, 6, p)
    else:
        raise ValueError(max_deg)


def poly_to_str(coefs, names=MON_NAMES):
    parts = []
    for c, n in zip(coefs, names):
        if c % P != 0:
            cc = c % P
            cc = cc - P if cc > P // 2 else cc
            if cc == 1:
                parts.append(n)
            elif cc == -1:
                parts.append(f"-{n}")
            else:
                parts.append(f"{cc}·{n}")
    if not parts:
        return "0"
    return " + ".join(parts).replace("+ -", "- ")


def factor_homogeneous_quadratic(coefs, p):
    """Try to factor a homogeneous quadratic A α₁² + B α₁α₂ + C α₂² over F_p.

    coefs in MONOMIAL form (length 6). If 1, α₁, α₂ coefficients all 0, the form is
    homogeneous. Returns (None, None) if not factorable, else ((u1, v1), (u2, v2)) for
    L_i(α) = u_i α₁ + v_i α₂.
    """
    if any(coefs[i] % p != 0 for i in [0, 1, 2]):
        return None  # not homogeneous
    A, B, C = coefs[3] % p, coefs[4] % p, coefs[5] % p
    if A == 0 and C == 0:
        # B α₁ α₂  → factors are α₁ and α₂
        return ((1, 0), (0, 1))
    if A == 0:
        # B α₁ α₂ + C α₂² = α₂ (B α₁ + C α₂)
        return ((0, 1), (B, C))
    # treat as quadratic in α₁: A x² + B x α₂ + C α₂² = 0. Discriminant = B² - 4 A C
    disc = (B * B - 4 * A * C) % p
    # find sqrt of disc
    if disc == 0:
        # repeated root
        u = (-B * modinv(2 * A, p)) % p
        return ((1, -u), (1, -u))
    # try Tonelli-Shanks (or for small p just bruteforce)
    sq = None
    for r in range(p):
        if (r * r) % p == disc:
            sq = r
            break
    if sq is None:
        return None  # not factorable over F_p (irreducible conic)
    inv2A = modinv(2 * A, p)
    u1 = ((-B + sq) * inv2A) % p
    u2 = ((-B - sq) * inv2A) % p
    # roots of α₁/α₂ = u_i, so factor: (α₁ - u_i α₂)
    return ((1, (-u1) % p), (1, (-u2) % p))


def compute_V_delta(f, chain, R_local, p, H_R, n_R, w_R):
    V = []
    for alphas in product(range(p), repeat=R_local):
        g = fold_at_alpha(f, chain, list(alphas), p)
        syn = matvec(H_R, g, p)
        if all(x == 0 for x in syn):
            V.append(alphas)
            continue
        w_min, _T, _e = min_wt_via_MDS(syn, H_R, n_R, p, max_w=w_R)
        if w_min is not None:
            V.append(alphas)
    return V


def analyze(positions, coefs, chain, p, H_R, R_local, n_R, w_R, label):
    fhat = [0] * N0
    for pos, c in zip(positions, coefs):
        fhat[pos] = c
    f = evaluate_dft(fhat, chain[0][0], p)

    V = compute_V_delta(f, chain, R_local, p, H_R, n_R, w_R)
    print(f"\n=== {label}: positions={positions}, coefs={coefs} ===")
    print(f"  |V_δ| = {len(V)}")

    # Linear (deg ≤ 1) vanishing forms
    lin_basis = fit_vanishing(V, 1, p)
    print(f"  dim(linear vanishing forms) = {len(lin_basis)}")
    for v in lin_basis:
        # extend to length 6 for printing
        full = v + [0, 0, 0]
        print(f"    L = {poly_to_str(full)}")

    # Quadratic (deg ≤ 2) vanishing forms
    quad_basis = fit_vanishing(V, 2, p)
    print(f"  dim(deg-≤2 vanishing forms) = {len(quad_basis)}")
    for v in quad_basis:
        s = poly_to_str(v)
        # Try to factor if it's homogeneous quadratic
        fac = factor_homogeneous_quadratic(v, p)
        fac_str = ""
        if fac is not None:
            (a, b), (c, d) = fac
            L1 = f"({a}α₁ + {b}α₂)" if (a or b) else "1"
            L2 = f"({c}α₁ + {d}α₂)" if (c or d) else "1"
            fac_str = f"  ←  {L1} · {L2}"
        print(f"    G = {s}{fac_str}")

    # Diagnostic: for nontrivial V, see if the bound 2q is exhaustive
    if quad_basis:
        # Pick any nontrivial G and check Z(G) ⊇ V (sanity) and report |Z(G)|
        G = quad_basis[0]
        zeros = []
        for a1 in range(p):
            for a2 in range(p):
                if sum(c * m for c, m in zip(G, eval_monomials(a1, a2, p))) % p == 0:
                    zeros.append((a1, a2))
        contained = all(v in set(zeros) for v in V)
        print(f"  using G_basis[0]: |Z(G)| = {len(zeros)}, V ⊆ Z(G): {contained}")
    return V, lin_basis, quad_basis


def main():
    chain = setup_chain(P, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, P)
    w_R = 3

    print(f"# fit_G_alpha — fit deg-≤2 polynomial G(α) vanishing on V_δ")
    print(f"# Setup: p={P}, n_0={N0}, k_0={K0}, R={R}, n_R={N_R}, w_R={w_R}")
    print(f"# Schwartz-Zippel target: deg-2 G nonzero ⇒ |V_δ| ≤ 2q = {2*P}")

    # 6 known falsifiers
    for i, (positions, coefs) in enumerate(CANDIDATES):
        analyze(positions, coefs, chain, P, H_R, R, N_R, w_R, f"falsifier #{i+1}")

    # A few additional rank-2 above-J spec for diversity. Pick from the random scan
    # spec generator; only keep those with rank=2 above-J.
    print("\n\n# === Additional rank-2 above-J cases for sanity ===")
    rng = random.Random(12345)
    n_extra_done = 0
    n_tried = 0
    while n_extra_done < 4 and n_tried < 50:
        n_tried += 1
        sparsity = rng.choice([2, 3])
        positions = tuple(sorted(rng.sample(range(K0, N0), sparsity)))
        coefs = tuple(rng.randrange(1, P) for _ in range(sparsity))

        # Quick filter: above-J + rank 2
        fhat = [0] * N0
        for pos, c in zip(positions, coefs):
            fhat[pos] = c
        f = evaluate_dft(fhat, chain[0][0], P)
        above, _, _ = is_above_johnson_sampling(
            f, chain[0][0], K0, P, W_J, n_samples=20000, batch=4096, seed=1234,
            return_evidence=True,
        )
        if not above:
            continue
        corner_syns = compute_corner_syndromes(f, chain, R, P, H_R)
        nz = [s for s in corner_syns.values() if any(x != 0 for x in s)]
        rk = gauss_rank([list(s) for s in nz], P) if nz else 0
        if rk != 2:
            continue
        analyze(positions, coefs, chain, P, H_R, R, N_R, w_R, f"extra #{n_extra_done+1}")
        n_extra_done += 1


if __name__ == '__main__':
    main()
