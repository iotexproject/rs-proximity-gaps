#!/usr/bin/env python3 -u
"""Test whether the tetrahedron lemma counterexample lifts to Q.

At n=12 c=3 p=61, the tetrahedron supports {(1,4,5), (1,4,8), (4,5,8), (1,5,8)}
on V={1,4,5,8} disprove the Open-Set Rank Lemma. Question: does this configuration
also disprove the lemma over Q (so the lemma is FALSE in characteristic 0)?

If YES: lemma fails universally → conjecture v5 is wrong.
If NO  : lemma holds at generic prime → conjecture v5 vindicated, prove via lift.

Method:
  1. Build supports E_i and Λ_{E_i}(z) symbolically.
  2. Pick GENERIC L_j (rational distinct values) and γ_i (rational distinct values).
  3. Compute rank A over Q exactly.
  4. If rank = min(mc, 2D), the lemma's rank-deficiency hypothesis is empty over Q
     for this generic point, hence fails on at most a Zariski-closed proper subset.
"""

import sys
from itertools import combinations
from fractions import Fraction

def elp_Q(E, L):
    """Λ_E(z) = ∏_{j∈E}(z - L_j) as list of Q coefficients [c_0, c_1, ..., c_w]."""
    poly = [Fraction(1)]
    for j in E:
        new = [Fraction(0)] * (len(poly) + 1)
        for i, ci in enumerate(poly):
            new[i] -= L[j] * ci
            new[i + 1] += ci
        poly = new
    return poly

def make_NE_Q(E, L, D, c):
    """Build N_E ∈ Q^{c × D} where row r is shifted ELP coefficients."""
    lam = elp_Q(E, L)
    w = len(E)
    assert w == D - c
    N = [[Fraction(0)] * D for _ in range(c)]
    for r in range(c):
        for j in range(D):
            t = j - r
            if 0 <= t <= w:
                N[r][j] = lam[t]
    return N

def rank_Q(M):
    """Exact rank over Q via Gaussian elimination on Fraction matrix."""
    M = [row[:] for row in M]
    rows = len(M)
    cols = len(M[0]) if rows else 0
    rank = 0
    r = 0
    for c in range(cols):
        pv = None
        for i in range(r, rows):
            if M[i][c] != 0:
                pv = i; break
        if pv is None:
            continue
        M[r], M[pv] = M[pv], M[r]
        inv = Fraction(1) / M[r][c]
        M[r] = [x * inv for x in M[r]]
        for i in range(rows):
            if i != r and M[i][c] != 0:
                fac = M[i][c]
                M[i] = [a - fac * b for a, b in zip(M[i], M[r])]
        r += 1
        rank += 1
    return rank

def build_A_Q(E_list, gammas, L, D, c):
    """A ∈ Q^{m·c × 2D} with row blocks [N_{E_i} | γ_i N_{E_i}]."""
    m = len(E_list)
    A = [[Fraction(0)] * (2 * D) for _ in range(m * c)]
    for i, E in enumerate(E_list):
        N = make_NE_Q(E, L, D, c)
        g = gammas[i]
        for r in range(c):
            for j in range(D):
                A[i*c + r][j]     = N[r][j]
                A[i*c + r][D + j] = g * N[r][j]
    return A

def kernel_Q(M, expected_dim=None):
    """Return basis of right null space (as list of column vectors of Fractions)."""
    M = [row[:] for row in M]
    rows = len(M); cols = len(M[0]) if rows else 0
    pivot_col = [-1] * rows
    r = 0
    for c in range(cols):
        if r >= rows: break
        pv = None
        for i in range(r, rows):
            if M[i][c] != 0:
                pv = i; break
        if pv is None: continue
        M[r], M[pv] = M[pv], M[r]
        inv = Fraction(1) / M[r][c]
        M[r] = [x * inv for x in M[r]]
        for i in range(rows):
            if i != r and M[i][c] != 0:
                fac = M[i][c]
                M[i] = [a - fac * b for a, b in zip(M[i], M[r])]
        pivot_col[r] = c
        r += 1
    pivots = set(pivot_col[:r])
    free_cols = [c for c in range(cols) if c not in pivots]
    basis = []
    for fc in free_cols:
        v = [Fraction(0)] * cols
        v[fc] = Fraction(1)
        for i in range(r):
            pc = pivot_col[i]
            if pc >= 0:
                v[pc] = -M[i][fc]
        basis.append(v)
    return basis

def vec_in_rowspan(A, target):
    """Check if `target` ∈ row-span(A) via rank(A) vs rank(A | target)."""
    Aug = [row + [t] for row, t in zip([r[:] for r in A], [Fraction(0)] * len(A))]
    # Actually easier: stack target as a row, see if rank changes
    rA = rank_Q(A)
    A2 = [r[:] for r in A] + [target[:]]
    rA2 = rank_Q(A2)
    return rA2 == rA

def test_config(name, n, k, c, V_or_Es, L=None, gammas=None):
    D = n - k; w = D - c
    print(f"\n=== {name} ===")
    print(f"  n={n} k={k} D={D} c={c} w={w}")
    if isinstance(V_or_Es, tuple) and len(V_or_Es) == w + 1:
        # Tetrahedron: all w-subsets of V
        E_list = list(combinations(V_or_Es, w))
    else:
        E_list = list(V_or_Es)
    m = len(E_list)
    print(f"  m={m}, supports={E_list}")
    bound = (2 * D - 1) // c
    print(f"  bound = ⌊(2D-1)/c⌋ = {bound}, m > bound? {m > bound}")

    if L is None:
        # Generic L_j = small distinct rationals
        L = [Fraction(j + 1) for j in range(n)]
    if gammas is None:
        # Generic γ_i = small distinct rationals (avoiding 0 and L conflicts)
        gammas = [Fraction(100 + i) for i in range(m)]

    A = build_A_Q(E_list, gammas, L, D, c)
    rA = rank_Q(A)
    full = min(m * c, 2 * D)
    print(f"  rank A over Q = {rA}, min(mc, 2D) = {full}, deficient? {rA < full}")

    if rA < full:
        # Compute X_γ dim and check open conditions
        ker = kernel_Q(A)
        print(f"  ker A dim over Q = {len(ker)}")
        # Open condition: ⟨n_0(E_i), s_2⟩ = 0 for some i, all (s_1, s_2) ∈ ker
        any_open = False
        for i, E in enumerate(E_list):
            N = make_NE_Q(E, L, D, c)
            n0 = N[0]  # first row
            # Check if for ALL kernel vectors v, sum_j n0[j] * v[D+j] == 0
            zero_for_all = all(
                sum(n0[j] * v[D + j] for j in range(D)) == 0
                for v in ker
            )
            print(f"    i={i} E={E}: ⟨n_0, s_2⟩ ≡ 0 on ker? {zero_for_all}")
            if zero_for_all:
                any_open = True
        if not any_open:
            print(f"  ⚠️ LEMMA DISPROVED OVER Q at this configuration")
            return False
        else:
            print(f"  Lemma's open-condition branch hit → lemma OK over Q here")
            return True
    else:
        print(f"  Full rank → lemma trivially holds (X_γ = 0)")
        return True

if __name__ == '__main__':
    # Test 1: tetrahedron at n=12 c=3 (which fails at p=61)
    test_config(
        "Tetrahedron n=12 c=3 over Q (V={1,4,5,8})",
        n=12, k=6, c=3, V_or_Es=(1, 4, 5, 8),
    )

    # Test 2: tetrahedron with different V
    test_config(
        "Tetrahedron n=12 c=3 over Q (V={0,1,2,3})",
        n=12, k=6, c=3, V_or_Es=(0, 1, 2, 3),
    )

    # Test 3: tetrahedron at n=16 c=3 (m=C(4,5)=4 size-5 subsets of 6-set? No.)
    # Actually general "(w+1)-clique": all w-subsets of (w+1)-set = w+1 supports
    # n=16 k=8 c=3 → w=5, V is a 6-set, m = C(6,5) = 6
    test_config(
        "(w+1)-clique n=16 c=3 over Q (V={0,1,2,3,4,5})",
        n=16, k=8, c=3, V_or_Es=(0, 1, 2, 3, 4, 5),
    )

    # Test 4: same config but with γ_i hitting some special algebraic values
    # Try γ = -1, ..., -m to see if special γ creates rank deficiency
    print("\n=== Special γ values ===")
    Es = list(combinations((1, 4, 5, 8), 3))
    L = [Fraction(j + 1) for j in range(12)]
    test_config(
        "Tetrahedron n=12 c=3 over Q with γ = roots of unity (rational approx)",
        n=12, k=6, c=3, V_or_Es=Es, L=L,
        gammas=[Fraction(1), Fraction(2), Fraction(3), Fraction(5)],
    )

    # Test 5: triangle at c=2 (known to FAIL even over Q presumably)
    print("\n=== c=2 triangle test (sanity check) ===")
    test_config(
        "Triangle n=8 c=2 over Q (E_i = pairs forming K_3 on {3,5,6} + disjoint (0,1))",
        n=8, k=4, c=2, V_or_Es=[(3, 6), (5, 6), (0, 1), (3, 5)],
    )
