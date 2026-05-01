"""Empirical verification of Lemma 1 (⇐) in paper3 §7.6 at D < 2w+1.

Issue #398 claims: at D < 2w+1, "Q ∈ Ann_w(x) monic deg w L-rooted" does
NOT imply x ∈ ⋃_{|E|=w} V_E because Hankel-w only encodes D-w shift
relations.

This script tests the claim. For random x ∈ F_p^D at (n, c, p, D, w) =
(10, 3, 41, 7, 4) (so D=7 < 2w+1=9 — exactly the deployment regime):

  1. Compute Ann_4(x) = ker(H_4(x)).
  2. Search for Q ∈ Ann_4(x) monic deg 4 with all roots in L.
  3. If exists: brute-force check if x ∈ ⋃_{|E|=4} V_E.
  4. If exists Q but x ∉ ⋃ V_E → COUNTEREXAMPLE TO LEMMA 1 (⇐).

If no counterexamples found across N trials, Lemma 1 (⇐) holds
empirically and the proof in paper3.tex needs to be made rigorous (not
restricted as #398 suggests).
"""

import os
import random
import sys
from itertools import combinations, product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from op2_curve_measure_prefactor import (
    small_field_subgroup, vandermonde, precompute_E_kernels, in_V_E,
)

random.seed(42)


def hankel_w(x, w):
    """H_w(x): rows 0..D-w-1, cols 0..w. H[j][i] = x[j+i].

    Ann_w(x) = ker(H_w) = {q ∈ F_p^{w+1} : H_w · q = 0}.
    """
    D = len(x)
    return [[x[j + i] for i in range(w + 1)] for j in range(D - w)]


def matrix_kernel(M, p):
    """Right kernel of M over F_p, as a list of basis vectors."""
    if not M or not M[0]:
        return []
    rows = len(M)
    cols = len(M[0])
    A = [list(row) for row in M]

    pivot_col_for_row = [-1] * rows
    pivot_cols = set()
    r = 0
    for c in range(cols):
        # Find pivot
        piv = None
        for i in range(r, rows):
            if A[i][c] % p != 0:
                piv = i
                break
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        # Normalize
        inv = pow(A[r][c], p - 2, p)
        A[r] = [(v * inv) % p for v in A[r]]
        # Eliminate
        for i in range(rows):
            if i != r and A[i][c] % p != 0:
                factor = A[i][c]
                A[i] = [(A[i][j] - factor * A[r][j]) % p for j in range(cols)]
        pivot_col_for_row[r] = c
        pivot_cols.add(c)
        r += 1
        if r == rows:
            break

    # Free columns give basis vectors
    free_cols = [c for c in range(cols) if c not in pivot_cols]
    basis = []
    for fc in free_cols:
        v = [0] * cols
        v[fc] = 1
        # Back-substitute pivots
        for i, pc in enumerate(pivot_col_for_row):
            if pc == -1:
                break
            # v[pc] = -A[i][fc]
            v[pc] = (-A[i][fc]) % p
        basis.append(v)
    return basis


def poly_div_check(num, den, p):
    """Check num | X^n - 1, where num is the polynomial we want to check
    is L-rooted (L = order-n multiplicative subgroup). Returns True iff
    X^n - 1 ≡ 0 (mod num)."""
    # Compute X^n mod num via repeated squaring
    n = len(den) - 1  # X^n - 1 has X^n leading term; den = [-1, 0, ..., 0, 1]
    if not num or len(num) <= 1:
        return False  # constant doesn't really divide here
    deg = len(num) - 1
    # Compute X^n mod num
    result = [1]  # 1 = X^0
    base = [0, 1]  # X
    e = n
    while e > 0:
        if e & 1:
            result = poly_mul_mod(result, base, num, p)
        e >>= 1
        if e > 0:
            base = poly_mul_mod(base, base, num, p)
    # Check result == 1
    while result and result[-1] == 0:
        result.pop()
    return result == [1]


def poly_mul_mod(a, b, mod, p):
    """(a * b) mod (mod) over F_p."""
    # mod = list of coeffs, leading nonzero
    out = [0] * (len(a) + len(b) - 1) if a and b else []
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[i + j] = (out[i + j] + ai * bj) % p
    # Reduce mod
    md = len(mod) - 1
    lead_inv = pow(mod[md], p - 2, p)
    while len(out) > md:
        c = out[-1]
        if c != 0:
            for k in range(md + 1):
                out[len(out) - 1 - md + k] = (out[len(out) - 1 - md + k] - c * lead_inv * mod[k]) % p
        out.pop()
    return out


def find_L_rooted_monic_deg_w(ann_basis, w, L, p):
    """Search for Q = sum c_i * basis[i] with c_i ∈ F_p such that:
       - Q has degree exactly w (leading coeff nonzero)
       - Q is monic (after normalization: leading coeff = 1)
       - All w roots lie in L

    Returns (Q_list, ξ_list, E_list) for one such Q, or None if none.

    For deployment scale we'd need a smarter search; for (n=10, w=4),
    Ann_w has dim ≥ w+1-(D-w) = 2 generically. Search by brute force.
    """
    if not ann_basis:
        return None
    dim = len(ann_basis)
    # Enumerate F_p^dim coefficient vectors
    n_L = len(L)
    L_set = set(L)
    for coeffs in product(range(p), repeat=dim):
        # Build Q = sum coeffs[i] * basis[i]
        Q = [0] * (w + 1)
        for i, c in enumerate(coeffs):
            for j in range(w + 1):
                Q[j] = (Q[j] + c * ann_basis[i][j]) % p
        # Strip trailing zeros
        while Q and Q[-1] == 0:
            Q.pop()
        if not Q or len(Q) != w + 1:
            continue
        # Monic check: leading coeff
        lead = Q[-1]
        inv_lead = pow(lead, p - 2, p)
        Q_monic = [(c * inv_lead) % p for c in Q]
        # Check L-rooted: factor over L (equivalently Q | X^n - 1)
        roots_in_L = []
        for v_idx, v in enumerate(L):
            # Evaluate Q at v
            val = 0
            for k, qk in enumerate(Q_monic):
                val = (val + qk * pow(v, k, p)) % p
            if val == 0:
                roots_in_L.append(v_idx)
        if len(roots_in_L) == w:
            # Check distinct (forced by L being a multiplicative subgroup —
            # X^n - 1 has distinct roots over F_p, so any Q | X^n - 1 has
            # distinct roots).
            return Q_monic, roots_in_L
    return None


def is_in_union_V_E(x, w, L, p):
    """Brute-force check x ∈ ⋃_{|E|=w} V_E by enumerating all (n choose w)
    subsets E and testing if x is in the column span of the Vandermonde
    matrix [ev_v : v ∈ E]^T (DxW)."""
    n = len(L)
    D = len(x)
    for E in combinations(range(n), w):
        # Build DxW Vandermonde for E
        M = [[pow(L[v], j, p) for v in E] for j in range(D)]
        # Augment with x and check rank
        aug = [row[:] + [x[j]] for j, row in enumerate(M)]
        # Reduce both M and aug to compare ranks
        if rank_eq(M, aug, p):
            return True
    return False


def matrix_rank(M, p):
    """Rank of M over F_p via row reduction."""
    if not M or not M[0]:
        return 0
    A = [list(row) for row in M]
    rows = len(A)
    cols = len(A[0])
    r = 0
    for c in range(cols):
        if r >= rows:
            break
        piv = None
        for i in range(r, rows):
            if A[i][c] % p != 0:
                piv = i
                break
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        inv = pow(A[r][c], p - 2, p)
        A[r] = [(v * inv) % p for v in A[r]]
        for i in range(r + 1, rows):
            if A[i][c] % p != 0:
                factor = A[i][c]
                A[i] = [(A[i][j] - factor * A[r][j]) % p for j in range(cols)]
        r += 1
    return r


def rank_eq(M, aug, p):
    """rank(M) == rank(aug)?"""
    return matrix_rank(M, p) == matrix_rank(aug, p)


# --- Main verification ---

def main():
    n = 10
    c = 3
    p = 41
    D = 7  # n - k where k = 3
    w = 4  # D - c
    assert D < 2 * w + 1, f"Need short-data regime; got D={D}, 2w+1={2*w+1}"
    print(f"Test cell: n={n}, c={c}, p={p}, D={D}, w={w}, 2w+1={2*w+1}")
    print(f"Short-data regime: D={D} < 2w+1={2*w+1} ✓")
    print()

    L = small_field_subgroup(p, n)
    print(f"L = {L}")
    print()

    n_trials = 1000
    n_q_exists = 0
    n_x_in_union = 0
    n_q_implies_union = 0
    counterexamples = []

    for trial in range(n_trials):
        x = [random.randrange(p) for _ in range(D)]
        H = hankel_w(x, w)
        ann = matrix_kernel(H, p)
        if not ann:
            continue
        # Find Q ∈ Ann_w(x) monic deg w L-rooted
        result = find_L_rooted_monic_deg_w(ann, w, L, p)
        x_in_union = is_in_union_V_E(x, w, L, p)
        if x_in_union:
            n_x_in_union += 1
        if result is not None:
            n_q_exists += 1
            if x_in_union:
                n_q_implies_union += 1
            else:
                counterexamples.append((trial, x, result))
                print(f"COUNTEREXAMPLE at trial {trial}: x={x}, Q={result[0]}, "
                      f"E={result[1]}")

    print(f"Trials: {n_trials}")
    print(f"  cases x ∈ ⋃ V_E (brute force): {n_x_in_union}")
    print(f"  cases Q ∈ Ann_w(x) monic deg w L-rooted exists: {n_q_exists}")
    print(f"  cases Q exists ⟹ x ∈ ⋃ V_E: {n_q_implies_union}")
    print(f"  COUNTEREXAMPLES to (⇐): {len(counterexamples)}")
    print()
    if not counterexamples:
        print("✓ Lemma 1 (⇐) holds empirically at D < 2w+1.")
        print("  Issue #398's concern is empirically refuted.")
        print("  Fix: rigorize the (⇐) proof in paper3 §7.6 (recurrence-extension")
        print("  argument), don't restrict the lemma.")
    else:
        print("✗ Lemma 1 (⇐) FAILS — Issue #398 confirmed.")
        print("  Need to restrict lemma per Issue #398 Option 1.")


if __name__ == "__main__":
    main()
