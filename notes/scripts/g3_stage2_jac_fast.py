"""g3_stage2_jac_fast.py — fast Jacobian-rank check at origin.

Key idea: each E[d] is at most degree 1 in (α, β). So R[d] mod m^2 (where
m = (α, β)) can be computed in O(h^2) time using a (constant, linear-vec)
representation. Avoids full R[d] expansion.

Each polynomial P in F_p[α, β]/m^2 = (P[0]: constant, P[1..nvar]: lin coefs).
Multiplication: (a0, a_lin) * (b0, b_lin) = (a0*b0, a0*b_lin + a_lin*b0).

This makes h=32 linearization possible in seconds.
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g3_stage2_fast import find_rho


def make_const(c, nvar, p):
    return [c % p] + [0]*nvar


def make_var(idx, nvar, p):
    v = [0] * (nvar + 1)
    v[idx + 1] = 1
    return v


def add(a, b, p):
    return [(a[i] + b[i]) % p for i in range(len(a))]


def neg(a, p):
    return [(p - x) % p for x in a]


def scale(a, k, p):
    k %= p
    return [(x * k) % p for x in a]


def mul(a, b, p):
    nvar = len(a) - 1
    out = [0] * (nvar + 1)
    out[0] = (a[0] * b[0]) % p
    for i in range(1, nvar + 1):
        out[i] = (a[0] * b[i] + a[i] * b[0]) % p
    return out


def stage2_linear_part(h, p, rho_val):
    """Return (rows, n_const_nonzero, eqs_meta).
    rows: list of length-(2(h-1)) row vectors over F_p (the Jacobian rows).
    n_const_nonzero: count of equations with non-zero constant term.
    eqs_meta: list of (c, k) for each row.
    """
    inv2 = pow(2, p-2, p)
    inv4 = pow(4, p-2, p)
    eps_val = (pow(rho_val, 4, p) * inv4) % p
    Eh_val = (-pow(rho_val, 3, p) * inv2) % p
    E0_val = (-eps_val) % p

    nvar = 2 * (h - 1)

    # E[d] as length-(nvar+1) vector
    E = [make_const(0, nvar, p) for _ in range(4*h + 1)]
    E[0] = make_const(E0_val, nvar, p)
    E[h] = make_const(Eh_val, nvar, p)
    E[3*h] = make_const(rho_val, nvar, p)
    E[4*h] = make_const(1, nvar, p)
    for c in range(1, h):
        E[2*h + c] = make_var(c-1, nvar, p)        # alpha_c
        E[3*h + c] = make_var((h-1) + (c-1), nvar, p)  # beta_c

    # R[4h] = 1; R[idx] = -E[idx] - sum_{ell} E[4h-ell]*R[4h-d+ell]  (mod m^2)
    R = [None] * (4*h + 1)
    R[4*h] = make_const(1, nvar, p)
    for d in range(1, 4*h + 1):
        idx = 4*h - d
        rhs = neg(E[idx], p)
        for ell in range(1, d):
            term = mul(E[4*h - ell], R[4*h - d + ell], p)
            rhs = add(rhs, neg(term, p), p)
        R[idx] = rhs

    # Build U_c[k] = sum P^(a)(y)*R^(b)(y) ... mod m^2
    # P^(a)[j] = E[a + j*h], R^(b)[j] = R[a + j*h]
    eqs = []  # (c, k, vec)
    for c in range(1, h):
        # 9 y-coefficients: Sc[k] for k in 0..8, Tc[k] for k in 0..8
        Sc = [make_const(0, nvar, p) for _ in range(9)]
        Tc = [make_const(0, nvar, p) for _ in range(9)]
        for a in range(h):
            b = c - a
            if 0 <= b < h:
                for j1 in range(5):
                    for j2 in range(5):
                        d1 = a + j1*h
                        d2 = b + j2*h
                        if d1 > 4*h or d2 > 4*h:
                            continue
                        prod = mul(E[d1], R[d2], p)
                        Sc[j1+j2] = add(Sc[j1+j2], prod, p)
            b = c + h - a
            if 0 <= b < h:
                for j1 in range(5):
                    for j2 in range(5):
                        d1 = a + j1*h
                        d2 = b + j2*h
                        if d1 > 4*h or d2 > 4*h:
                            continue
                        prod = mul(E[d1], R[d2], p)
                        Tc[j1+j2] = add(Tc[j1+j2], prod, p)
        for k in range(10):
            uk = make_const(0, nvar, p)
            if k <= 8:
                uk = add(uk, Sc[k], p)
            if k-1 >= 0 and k-1 <= 8:
                uk = add(uk, Tc[k-1], p)
            # uk[0] is constant; uk[1:] is linear part
            if any(x != 0 for x in uk):
                eqs.append((c, k, uk))
    return eqs


def matrix_rank(rows, p, ncols):
    """Compute rank of integer matrix mod p."""
    M = [list(r) for r in rows]
    nrows = len(M)
    rank = 0
    pivot_col = 0
    while rank < nrows and pivot_col < ncols:
        pivot_row = None
        for r in range(rank, nrows):
            if M[r][pivot_col] != 0:
                pivot_row = r
                break
        if pivot_row is None:
            pivot_col += 1
            continue
        if pivot_row != rank:
            M[rank], M[pivot_row] = M[pivot_row], M[rank]
        inv_p = pow(M[rank][pivot_col], p-2, p)
        for j in range(ncols):
            M[rank][j] = (M[rank][j] * inv_p) % p
        for r in range(nrows):
            if r != rank and M[r][pivot_col] != 0:
                factor = M[r][pivot_col]
                for j in range(ncols):
                    M[r][j] = (M[r][j] - factor * M[rank][j]) % p
        rank += 1
        pivot_col += 1
    return rank


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, required=True)
    parser.add_argument("--p", type=int, default=193)
    parser.add_argument("--rho", type=int, default=None)
    args = parser.parse_args()

    p = args.p
    rho_val = args.rho or sorted(find_rho(p))[0]
    nvar = 2 * (args.h - 1)
    print(f"=== h={args.h}, p={p}, rho={rho_val}, nvar={nvar} ===")

    import time
    t0 = time.time()
    eqs = stage2_linear_part(args.h, p, rho_val)
    t1 = time.time()
    print(f"  build (mod m^2): {t1-t0:.2f}s; {len(eqs)} non-trivial eqs")

    # Constants
    n_const = sum(1 for c, k, vec in eqs if vec[0] != 0)
    print(f"  Constants (non-zero): {n_const} / {len(eqs)}")

    # Jacobian = linear part = vec[1:]
    rows = [vec[1:] for c, k, vec in eqs]
    rank = matrix_rank(rows, p, nvar)
    print(f"  Jacobian rank at origin: {rank} / {nvar}")
    if rank == nvar and n_const == 0:
        print(f"  → ORIGIN LOCALLY ISOLATED")


if __name__ == "__main__":
    main()
