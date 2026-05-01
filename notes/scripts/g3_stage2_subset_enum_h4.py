"""g3_stage2_subset_enum_h4.py — meet-in-the-middle enumeration for h=4.

Approach: split μ_{32} into two halves of 16 elements each. Enumerate
8-subsets in each half. For each pair (A, B) with |A| = 8 in half1 and
|B| = 8 in half2, S = A ∪ B has size 16.

For each subset of size 8 in each half, precompute (e_1, ..., e_8) (4h
elementary symmetric polynomials).

Then use the multiplication formula:
  E_S(t) = E_A(t) · E_B(t)
to compute e_k(S) from e_k(A), e_k(B).

Then check the 10 constraints on e_k(S).

Cost: 2 * C(16, 8) = 2 * 12870 = 25740 enumerations per half. For each
pair (A, B), O(16²) = 256 operations to combine. Total ≈ 25740² * 256 ≈
1.7e11 — too much.

Better: for each A, compute e_k(A) and store. Then for each B, compute
e_k(B), and check if any A ∈ stored gives valid combined S.

For the constraint e_k(S) = target_k, we have:
  e_k(S) = sum_{i=0}^{k} e_i(A) * e_{k-i}(B)

This is a CONVOLUTION. So e_•(S) = e_•(A) ★ e_•(B) (Cauchy product, as
generating polynomials).

Check: for each fixed B, the constraint becomes a LINEAR system in (e_0(A), ...,
e_8(A)), namely:
  sum_i e_i(A) * e_{k-i}(B) = target_k
for each k with target. So given B, solve for the e_•(A) values that would
work. Look up matching A in the stored A-list.

This is O(C(16,8) * 16²) = O(C(16,8)) per B, times C(16,8) for B = O(C(16,8)²) ≈ 1.6e8.
Manageable in a few minutes.
"""
import argparse
import sys
import os
import itertools
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g3_stage2_fast import find_rho


def get_mu_n(p, n):
    if (p - 1) % n != 0:
        return None
    from sympy.ntheory import factorint
    pf = list(factorint(p - 1).keys())
    g = None
    for cand in range(2, p):
        if all(pow(cand, (p-1) // f, p) != 1 for f in pf):
            g = cand
            break
    omega = pow(g, (p-1) // n, p)
    return [pow(omega, i, p) for i in range(n)]


def elem_sym_full(roots, p, max_k=None):
    """Compute e_0, e_1, ..., e_n of roots."""
    n = len(roots)
    if max_k is None:
        max_k = n
    poly = [0] * (max_k + 1)
    poly[0] = 1
    for r in roots:
        new_poly = poly[:]
        for j in range(min(max_k - 1, len(poly) - 1), -1, -1):
            if poly[j] != 0:
                new_poly[j + 1] = (new_poly[j + 1] + poly[j] * r) % p
        poly = new_poly
    return poly


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, default=193)
    args = parser.parse_args()
    p = args.p
    h = 4
    rhos = find_rho(p)
    rho = sorted(rhos)[0]
    inv2 = pow(2, p-2, p)
    inv4 = pow(4, p-2, p)
    print(f"p={p}, rho={rho}")

    # Targets
    target = {
        4: rho,
        8: 0,
        9: 0,
        10: 0,
        11: 0,
        12: (-pow(rho, 3, p) * inv2) % p,
        13: 0,
        14: 0,
        15: 0,
        16: (-pow(rho, 4, p) * inv4) % p,
    }
    print(f"Targets: {sorted(target.items())}")

    mu32 = get_mu_n(p, 32)
    if mu32 is None:
        print("FAIL: 32 ∤ p-1")
        return
    print(f"|μ_32| = {len(mu32)}")

    # Split μ_32 into 2 halves
    H1 = mu32[:16]
    H2 = mu32[16:]
    print(f"H1 size {len(H1)}, H2 size {len(H2)}")

    # Enumerate 8-subsets of each half, store (key=tuple of e_•, value=subset)
    print("Building H1 8-subsets...")
    t0 = time.time()
    A_dict = {}  # key=tuple(e_0..e_8), value=list of subsets
    for A in itertools.combinations(range(16), 8):
        roots = [H1[i] for i in A]
        e = tuple(elem_sym_full(roots, p, max_k=8))
        A_dict.setdefault(e, []).append(A)
    print(f"  {len(A_dict)} distinct e-tuples for H1; time {time.time()-t0:.1f}s")

    # Enumerate 8-subsets of H2; for each B, check if A exists matching constraints
    print("Scanning H2 8-subsets...")
    t0 = time.time()
    valid = []
    for ix, B in enumerate(itertools.combinations(range(16), 8)):
        if ix % 1000 == 0 and ix > 0:
            print(f"  ...{ix}/12870 ({time.time()-t0:.1f}s); valid so far: {len(valid)}")
        rootsB = [H2[i] for i in B]
        eB = elem_sym_full(rootsB, p, max_k=8)

        # For each k, target_k = sum_i e_i(A) * e_{k-i}(B)
        # We need to find e_i(A) tuple satisfying these.
        # 10 constraints on 9 variables (e_0..e_8); need enough constraints.
        # Build linear system in e_•(A):
        #   for each k in target: sum_{i: 0 <= k-i <= 8 and 0 <= i <= 8} e_i(A) * eB[k-i] = target[k]
        # 10 linear equations in (e_0(A), ..., e_8(A)).

        # Solve via Gaussian elimination.
        n_vars = 9
        rows = []
        for k, t_k in sorted(target.items()):
            row = [0] * n_vars
            for i in range(n_vars):
                kpi = k - i
                if 0 <= kpi <= 8:
                    row[i] = eB[kpi]
            rows.append((row, t_k))

        # Gaussian elim mod p
        sol = list(range(n_vars))  # placeholder
        # Augmented matrix
        M = [list(r) + [t] for r, t in rows]
        n_rows = len(M)
        # Forward elimination
        rank = 0
        col = 0
        while rank < n_rows and col < n_vars:
            piv = None
            for r in range(rank, n_rows):
                if M[r][col] != 0:
                    piv = r
                    break
            if piv is None:
                col += 1
                continue
            M[rank], M[piv] = M[piv], M[rank]
            inv_pv = pow(M[rank][col], p-2, p)
            for j in range(n_vars + 1):
                M[rank][j] = (M[rank][j] * inv_pv) % p
            for r in range(n_rows):
                if r != rank and M[r][col] != 0:
                    factor = M[r][col]
                    for j in range(n_vars + 1):
                        M[r][j] = (M[r][j] - factor * M[rank][j]) % p
            rank += 1
            col += 1
        # Check consistency: rows after rank should be all zero (lhs and rhs)
        consistent = True
        for r in range(rank, n_rows):
            if any(M[r][:n_vars]) or M[r][n_vars] != 0:
                consistent = False
                break
        if not consistent:
            continue
        # Express e_• in terms of free variables; check if any A in A_dict matches.
        # Free variables: cols not pivoted.
        # If all 9 vars pivoted (full rank), there's a unique e tuple — look up.
        if rank == n_vars:
            # Unique solution; tuple from rhs of M[i] for i=0..n_vars-1
            sol_tuple = tuple(M[i][n_vars] for i in range(n_vars))
            if sol_tuple in A_dict:
                for A in A_dict[sol_tuple]:
                    S = sorted([H1[i] for i in A] + rootsB)
                    valid.append((A, B, S))
        else:
            # Underdetermined; would need to enumerate possible e_• values.
            # For now, skip (unlikely)
            pass

    print(f"\nDone. Valid (A, B, S): {len(valid)}")
    for i, (A, B, S) in enumerate(valid[:5]):
        print(f"  S_{i}: {S}")


if __name__ == "__main__":
    main()
