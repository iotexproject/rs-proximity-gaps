"""g3_stage2_linearize.py — examine Stage 2 system Jacobian at origin
and degree distribution.

If most equations are linear in (α, β) with full-rank Jacobian, then origin
is locally isolated and GB closes near origin trivially.
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g3_stage2_fast import build_stage2, find_rho


def degree_profile(eqs, nvar):
    """Return list of (c, k, total_degree, num_terms, is_linear)."""
    profile = []
    for c, k, poly in eqs:
        if not poly:
            profile.append((c, k, -1, 0, True))
            continue
        max_deg = max(sum(monom) for monom in poly)
        n_terms = len(poly)
        # Linear in unknowns iff every monomial has degree ≤ 1 in vars
        is_linear = max_deg <= 1
        profile.append((c, k, max_deg, n_terms, is_linear))
    return profile


def jacobian_rank(eqs, nvar, p):
    """Compute Jacobian of equations at origin, rank over F_p."""
    # ∂U/∂x_i at origin = coefficient of x_i in U (constants drop, all degree-≥2 drop)
    # Build matrix: rows = equations, cols = vars
    n_eqs = len(eqs)
    M = [[0]*nvar for _ in range(n_eqs)]
    constants = []
    for r, (c, k, poly) in enumerate(eqs):
        const_term = 0
        for monom, coef in poly.items():
            total_deg = sum(monom)
            if total_deg == 0:
                const_term = coef
            elif total_deg == 1:
                # Find which var
                for i, ex in enumerate(monom):
                    if ex == 1:
                        M[r][i] = coef
                        break
        constants.append(const_term)
    # Row-reduce M mod p
    rank = 0
    pivot_col = 0
    for r in range(n_eqs):
        # Find pivot
        pivot_row = None
        for rr in range(rank, n_eqs):
            if M[rr][pivot_col] != 0:
                pivot_row = rr
                break
        while pivot_row is None and pivot_col + 1 < nvar:
            pivot_col += 1
            for rr in range(rank, n_eqs):
                if M[rr][pivot_col] != 0:
                    pivot_row = rr
                    break
        if pivot_row is None:
            break
        if pivot_row != rank:
            M[rank], M[pivot_row] = M[pivot_row], M[rank]
        # Normalize and eliminate
        inv_p = pow(M[rank][pivot_col], p-2, p)
        for j in range(nvar):
            M[rank][j] = (M[rank][j] * inv_p) % p
        for rr in range(n_eqs):
            if rr != rank and M[rr][pivot_col] != 0:
                factor = M[rr][pivot_col]
                for j in range(nvar):
                    M[rr][j] = (M[rr][j] - factor * M[rank][j]) % p
        rank += 1
        pivot_col += 1
        if pivot_col >= nvar:
            break
    return rank, constants


def degree_min_max(eqs, nvar):
    """Return per-equation (min_deg, max_deg) — checks if equations are
    homogeneous (min == max)."""
    out = []
    for c, k, poly in eqs:
        if not poly:
            out.append((c, k, -1, -1, True))
            continue
        degs = [sum(monom) for monom in poly]
        out.append((c, k, min(degs), max(degs), min(degs) == max(degs)))
    return out


def linear_part_matrix(eqs, nvar, p):
    """Return the Jacobian matrix at origin, full (no row reduction)."""
    n_eqs = len(eqs)
    M = [[0]*nvar for _ in range(n_eqs)]
    for r, (c, k, poly) in enumerate(eqs):
        for monom, coef in poly.items():
            if sum(monom) == 1:
                for i, ex in enumerate(monom):
                    if ex == 1:
                        M[r][i] = coef
                        break
    return M


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, required=True)
    parser.add_argument("--p", type=int, default=193)
    parser.add_argument("--rho", type=int, default=None)
    parser.add_argument("--show-jac", action="store_true")
    args = parser.parse_args()
    rho_val = args.rho or sorted(find_rho(args.p))[0]
    print(f"=== h={args.h}, p={args.p}, rho={rho_val} ===")

    eqs, nvar = build_stage2(args.h, args.p, rho_val)
    profile = degree_profile(eqs, nvar)

    print(f"\n  {len(eqs)} eqs, {nvar} unknowns")
    deg_counts = {}
    for c, k, deg, nt, lin in profile:
        deg_counts[deg] = deg_counts.get(deg, 0) + 1
    print(f"  Degree distribution: {sorted(deg_counts.items())}")

    rank, consts = jacobian_rank(eqs, nvar, args.p)
    n_const = sum(1 for c in consts if c != 0)
    print(f"  Constants (non-zero): {n_const} / {len(eqs)}")
    print(f"  Jacobian rank at origin: {rank} / {nvar}")
    if rank == nvar and n_const == 0:
        print(f"  → Origin is LOCALLY ISOLATED (full Jacobian rank, no constants)")
    elif n_const != 0:
        print(f"  → Origin is NOT a solution (constants don't vanish)")

    # Per-equation min/max degree
    mm = degree_min_max(eqs, nvar)
    n_homog = sum(1 for c, k, mn, mx, eq in mm if eq and mn > 0)
    n_with_linear = sum(1 for c, k, mn, mx, eq in mm if mn == 1)
    print(f"  Eqs that are pure-homogeneous (degree d > 0 only): {n_homog} / {len(eqs)}")
    print(f"  Eqs with non-trivial linear part: {n_with_linear} / {len(eqs)}")
    # Show distribution of (min, max) per eq
    profile = {}
    for c, k, mn, mx, _ in mm:
        profile[(mn, mx)] = profile.get((mn, mx), 0) + 1
    print(f"  (min_deg, max_deg) profile: {sorted(profile.items())}")

    if args.show_jac:
        M = linear_part_matrix(eqs, nvar, args.p)
        print(f"\n  Jacobian matrix at origin ({len(M)} × {nvar}):")
        for r, row in enumerate(M):
            c, k, _ = eqs[r]
            print(f"    eq c={c} y^{k}: {row}")


if __name__ == "__main__":
    main()
