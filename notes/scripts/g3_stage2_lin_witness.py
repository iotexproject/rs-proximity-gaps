"""g3_stage2_lin_witness.py — extract the explicit linear-combination
matrix that reduces 4(h-1) Stage 2 equations modulo m^2 to a basis of m
(= 2(h-1) generators).

Output: a (2(h-1)) × (4(h-1)) matrix C over F_p such that
  sum_j C[i, j] * U_j  ≡  basis_var_i   (mod m^2)
for i = 1, ..., 2(h-1).

If the same C works for multiple h (or has a uniform pattern), we have a
universal witness.
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g3_stage2_jac_fast import stage2_linear_part, find_rho


def extract_witness(h, p, rho_val):
    eqs = stage2_linear_part(h, p, rho_val)
    nvar = 2 * (h - 1)
    # Build Jacobian J: rows = eqs, cols = vars.
    J = [list(vec[1:]) for c, k, vec in eqs]  # n_eqs x nvar
    n_eqs = len(J)

    # Stack J | I (identity of size n_eqs) to track which combinations of
    # original equations produce row-reduced form.
    # We want to find C (nvar x n_eqs) such that C @ J = I_{nvar}.
    # By solving: pick nvar rows of J that form a basis; their inverse
    # gives the witness coefficients.

    # Augment J with identity.
    aug = [J[r] + [1 if i == r else 0 for i in range(n_eqs)] for r in range(n_eqs)]

    # Row-reduce aug, focusing on first nvar columns
    rank = 0
    pivot_cols = []
    for col in range(nvar):
        pivot_row = None
        for r in range(rank, n_eqs):
            if aug[r][col] != 0:
                pivot_row = r
                break
        if pivot_row is None:
            continue
        aug[rank], aug[pivot_row] = aug[pivot_row], aug[rank]
        inv_p = pow(aug[rank][col], p-2, p)
        for j in range(len(aug[rank])):
            aug[rank][j] = (aug[rank][j] * inv_p) % p
        for r in range(n_eqs):
            if r != rank and aug[r][col] != 0:
                factor = aug[r][col]
                for j in range(len(aug[rank])):
                    aug[r][j] = (aug[r][j] - factor * aug[rank][j]) % p
        pivot_cols.append((rank, col))
        rank += 1
    if rank != nvar:
        return None
    # The first nvar rows of aug now have row-reduced form on left, and
    # right side gives the linear combination of original equations.
    C = [aug[r][nvar:] for r in range(nvar)]
    # Var ordering: a1, a2, ..., a_{h-1}, b1, ..., b_{h-1}
    var_names = [f"a{c}" for c in range(1, h)] + [f"b{c}" for c in range(1, h)]
    return C, var_names, eqs, pivot_cols


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, required=True)
    parser.add_argument("--p", type=int, default=193)
    parser.add_argument("--rho", type=int, default=None)
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()
    rho_val = args.rho or sorted(find_rho(args.p))[0]
    print(f"=== h={args.h}, p={args.p}, rho={rho_val} ===")

    res = extract_witness(args.h, args.p, rho_val)
    if res is None:
        print("FAIL: cannot extract witness")
        return
    C, var_names, eqs, pivot_cols = res
    n_eqs = len(C[0])
    nvar = len(var_names)
    print(f"  Witness matrix C: {nvar} × {n_eqs}")

    # For each var, count non-zero entries (=length of certificate)
    print(f"  Sparsity per var:")
    for i, vn in enumerate(var_names):
        nz = sum(1 for c in C[i] if c != 0)
        print(f"    {vn}: {nz} non-zero entries / {n_eqs}")

    # Eq metadata: (c, k) for each j
    eq_meta = [(c, k) for c, k, _ in eqs]
    if args.show:
        print(f"  Equation order: {eq_meta}")
        print(f"  Pivot cols: {pivot_cols}")
        for i, vn in enumerate(var_names):
            terms = []
            for j, coef in enumerate(C[i]):
                if coef != 0:
                    c_e, k_e = eq_meta[j]
                    terms.append(f"  {coef}·U_{{c={c_e},y^{k_e}}}")
            print(f"  {vn} = ")
            print("\n".join(terms))


if __name__ == "__main__":
    main()
