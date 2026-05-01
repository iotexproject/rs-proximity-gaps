#!/usr/bin/env python3
"""
Pairwise Rank v4: Find the null vector (feasible line direction).

For each worst-case M-configuration:
1. Compute all condition vectors
2. Find the 1D null space (the line direction v)
3. Characterize v: is it related to ω or L in some nice way?
4. Check: how many OTHER error sets also have conditions vanishing on v?
"""

from itertools import combinations
from math import comb
from collections import defaultdict


def find_primitive_root(p):
    factors = set()
    temp = p - 1
    d = 2
    while d * d <= temp:
        while temp % d == 0:
            factors.add(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.add(temp)
    for g in range(2, p):
        if all(pow(g, (p - 1) // q, p) != 1 for q in factors):
            return g


def find_omega(n, p):
    g = find_primitive_root(p)
    return pow(g, (p - 1) // n, p)


def rank_mod_p(mat, p):
    if not mat or not mat[0]:
        return 0
    m = len(mat)
    nn = len(mat[0])
    M = [row[:] for row in mat]
    for i in range(m):
        for j in range(nn):
            M[i][j] %= p
    rank = 0
    for col in range(nn):
        pivot = -1
        for row in range(rank, m):
            if M[row][col] % p != 0:
                pivot = row
                break
        if pivot == -1:
            continue
        M[rank], M[pivot] = M[pivot], M[rank]
        inv_pivot = pow(M[rank][col], p - 2, p)
        for row in range(m):
            if row != rank and M[row][col] % p != 0:
                factor = M[row][col] * inv_pivot % p
                for j in range(nn):
                    M[row][j] = (M[row][j] - factor * M[rank][j]) % p
        rank += 1
    return rank


def kernel_mod_p(mat, p):
    """Right kernel of mat over F_p."""
    if not mat:
        return []
    m = len(mat)
    n = len(mat[0])
    M_mat = [row[:] for row in mat]
    for i in range(m):
        for j in range(n):
            M_mat[i][j] %= p
    pivot_cols = []
    rank = 0
    for col in range(n):
        pivot = -1
        for row in range(rank, m):
            if M_mat[row][col] % p != 0:
                pivot = row
                break
        if pivot == -1:
            continue
        M_mat[rank], M_mat[pivot] = M_mat[pivot], M_mat[rank]
        inv_pivot = pow(M_mat[rank][col], p - 2, p)
        for j in range(n):
            M_mat[rank][j] = M_mat[rank][j] * inv_pivot % p
        for row in range(m):
            if row != rank and M_mat[row][col] % p != 0:
                factor = M_mat[row][col]
                for j in range(n):
                    M_mat[row][j] = (M_mat[row][j] - factor * M_mat[rank][j]) % p
        pivot_cols.append(col)
        rank += 1
    free_cols = [c for c in range(n) if c not in pivot_cols]
    kernel = []
    for fc in free_cols:
        vec = [0] * n
        vec[fc] = 1
        for i, pc in enumerate(pivot_cols):
            vec[pc] = (-M_mat[i][fc]) % p
        kernel.append(vec)
    return kernel


def left_kernel_mod_p(mat, p):
    m = len(mat)
    n = len(mat[0])
    matT = [[mat[i][j] for i in range(m)] for j in range(n)]
    return kernel_mod_p(matT, p)


def get_conditions(S_indices, L, k, p, n):
    n_w = len(S_indices)
    if n_w <= k:
        return []
    V_S = [[pow(L[S_indices[j]], l, p) for l in range(k)] for j in range(n_w)]
    lk = left_kernel_mod_p(V_S, p)
    conditions = []
    for u in lk:
        v = [0] * n
        for j, idx in enumerate(S_indices):
            v[idx] = u[j] % p
        conditions.append(v)
    return conditions


def analyze_null_vector(n, k, p, w_target, error_sets):
    """
    Given the worst-case M error sets, find the null vector of the condition matrix.
    """
    w = w_target
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    conds_per = n - w - k
    M = len(error_sets)

    # Compute all conditions
    all_conds = []
    for B in error_sets:
        S = [i for i in range(n) if i not in B]
        conds = get_conditions(S, L, k, p, n)
        all_conds.extend(conds)

    # Find null space
    # The conditions are vectors in F_p^n, but they lie in RS_k^⊥ (dim n-k).
    # The null space of the condition matrix (as vectors in F_p^n) has
    # dimension n - rank(conditions). But we want the null space WITHIN RS_k^⊥,
    # which has dimension (n-k) - rank(conditions).

    # Since conditions ⊥ RS_k, the null space includes RS_k (dim k).
    # The null space modulo RS_k has dimension (n-k) - rank = 1 (our conjecture).

    # So: compute null space of conditions, then mod out RS_k.

    # Actually, let's work in syndrome space directly.
    # Map conditions to syndrome coordinates.

    # Parity check H[r][i] = L[i]^(k+r)
    H = [[pow(L[i], k + r, p) for i in range(n)] for r in range(n - k)]

    # Each condition vector v ∈ F_p^n is in RS_k^⊥ = rowspace(H).
    # So v = H^T w for some w ∈ F_p^{n-k}.
    # The syndrome-space condition is w^T s = 0.
    # We need to find w from v.

    # v = H^T w means: v_i = sum_r H[r][i] * w_r for all i.
    # We can solve for w using any (n-k) of the n equations.
    # Use the first (n-k) rows of the system v_i = sum_r H[r][i] w_r.

    # Matrix A: A[i][r] = H[r][i] = L[i]^(k+r).  Size n x (n-k).
    # v = A * w.
    # Solve using first (n-k) rows (they're independent since H has full rank).

    A = [[pow(L[i], k + r, p) for r in range(n - k)] for i in range(n)]
    A_sub = A[:n-k]  # (n-k) x (n-k), should be invertible

    # Invert A_sub mod p
    def mat_inv_mod_p(mat, p):
        nn = len(mat)
        aug = [mat[i][:] + [1 if j == i else 0 for j in range(nn)] for i in range(nn)]
        for col in range(nn):
            pivot = -1
            for row in range(col, nn):
                if aug[row][col] % p != 0:
                    pivot = row
                    break
            assert pivot != -1, f"Matrix not invertible at col {col}"
            aug[col], aug[pivot] = aug[pivot], aug[col]
            inv_pivot = pow(aug[col][col], p - 2, p)
            for j in range(2 * nn):
                aug[col][j] = aug[col][j] * inv_pivot % p
            for row in range(nn):
                if row != col and aug[row][col] % p != 0:
                    factor = aug[row][col]
                    for j in range(2 * nn):
                        aug[row][j] = (aug[row][j] - factor * aug[col][j]) % p
        return [[aug[i][j + nn] for j in range(nn)] for i in range(nn)]

    A_inv = mat_inv_mod_p(A_sub, p)

    # Convert each condition to syndrome space
    syn_conds = []
    for v in all_conds:
        # w_syn = A_inv * v[:n-k]
        v_sub = v[:n - k]
        w_syn = [sum(A_inv[r][i] * v_sub[i] for i in range(n - k)) % p for r in range(n - k)]
        syn_conds.append(w_syn)

    # Now find null space of the syndrome conditions
    r = rank_mod_p(syn_conds, p)
    print(f"  Syndrome condition rank: {r} / {n-k}")

    null_vecs = kernel_mod_p(syn_conds, p)
    print(f"  Null space dimension: {len(null_vecs)}")

    if len(null_vecs) == 1:
        v = null_vecs[0]
        print(f"  Null vector (syndrome direction): {v}")

        # Lift to F_p^n: find the coset representative
        # c = A * v (but this gives the n-k coordinates)
        # Actually, the syndrome s = v (up to scaling). The coset representative
        # has c_i = sum_r H[r][i]^{-1} ... hmm, this is more complex.

        # The null vector v represents a SYNDROME DIRECTION.
        # Any syndrome s = t*v (for t ∈ F_p*) achieves the M list codewords.

        # Let me check: for s = v, does M actually equal our M?
        # The list at syndrome s consists of error vectors e with He = s and wt(e) ≤ w.

        # For each error set B (positions where error is nonzero):
        # He = s has a unique solution e (with support B) iff H_B is invertible.
        # Since H is MDS: H_B (restriction to columns in B) is (n-k) x w.
        # For w ≤ n-k: H_B has rank w (all column subsets of MDS parity check are full rank).
        # So the system H_B * e_B = s has solutions: s must be in col(H_B).
        # s ∈ col(H_B) iff rank([H_B | s]) = rank(H_B) = w (when w < n-k).
        # I.e., s must be in the w-dimensional column span of H_B.

        # For our null vector v: check how many error position sets B have v ∈ col(H_B).
        H_cols = [[H[r][i] % p for r in range(n - k)] for i in range(n)]

        count_v = 0
        matching_B = []
        for B in combinations(range(n), w):
            # Check if v ∈ span(H_cols[b] for b in B)
            cols = [H_cols[b] for b in B]
            # Augment with v and check rank
            mat = cols + [v]
            r_aug = rank_mod_p([[mat[j][i] for i in range(n - k)] for j in range(len(mat))], p)
            r_base = rank_mod_p([[cols[j][i] for i in range(n - k)] for j in range(len(cols))], p)
            if r_aug == r_base:  # v is in span
                count_v += 1
                matching_B.append(B)

        print(f"  Error sets B with v ∈ col(H_B): {count_v}")
        print(f"  (Expected: M = {M})")

        if count_v != M:
            print(f"  WARNING: count_v = {count_v} ≠ M = {M}")
            print(f"  Additional error sets:")
            for B in matching_B:
                if B not in [tuple(sorted(es)) for es in error_sets]:
                    print(f"    B = {B}")

        # Now: analyze the structure of v
        print(f"\n  Analysis of null vector v = {v}:")

        # Check if v = (ω^0, ω^1, ..., ω^{n-1})^T for some exponent
        # i.e., v_r = ω^{r*a} for some a
        for a in range(n):
            test = [pow(omega, (k + r) * a, p) for r in range(n - k)]
            # Normalize: check if v is proportional to test
            if v[0] != 0 and test[0] != 0:
                ratio = v[0] * pow(test[0], p - 2, p) % p
                match = all((v[r] - ratio * test[r]) % p == 0 for r in range(n - k))
                if match:
                    print(f"  v is proportional to H*e_{{a={a}}}: ratio = {ratio}")
                    print(f"  This means s = {ratio} * H_col[{a}] = syndrome of error at position {a}")

        # Check if v is syndrome of a weight-1 error
        for i in range(n):
            for val in range(1, p):
                test_s = [val * H[r][i] % p for r in range(n - k)]
                if test_s == v:
                    print(f"  v = syndrome of error e[{i}] = {val}")

        # Check DFT structure: is v_r = ω^{r*a} * const?
        print(f"\n  v as function of r:")
        for r in range(n - k):
            # v[r] = syndrome component r, which corresponds to degree k+r
            print(f"    v[{r}] = {v[r]} (degree k+r = {k+r})")

        # Check if v is a codeword evaluation
        # v_r = g(ω^r) for some polynomial g?
        # Actually v is in syndrome space, not evaluation space.
        # The syndrome s_r = sum_i c_i * ω^{i(k+r)}.
        # So s_r = sum_i c_i * (ω^i)^{k+r} = f_c evaluated at degree k+r powers.
        # This is NOT the same as g(ω^r) for generic g.

        # Let me check: what is v as a function of ω^r?
        # Can we write v_r = f(ω^r) for some polynomial f?
        # v_r = sum_i c_i * L[i]^{k+r} = sum_i c_i * ω^{i(k+r)}
        # = sum_i c_i * (ω^{ik}) * ω^{ir}
        # = sum_i (c_i * ω^{ik}) * ω^{ir}
        # = DFT of the sequence (c_i * ω^{ik})_i evaluated at position r.

        # So v is the DFT of a "twisted" version of c. Interesting.

        # For the null vector: check all (n-k)-tuples for polynomial structure
        # v_r = a_0 + a_1 * ω^r + ... + a_{n-k-2} * ω^{r*(n-k-2)}?

        # Check: is v in the RS_{n-k-1} code on the "syndrome" evaluation domain
        # {ω^0, ω^1, ..., ω^{n-k-1}}? (Different from the original domain!)

        # Actually the syndrome domain is {1, ω, ω^2, ..., ω^{n-1}} evaluated
        # at exponents k, k+1, ..., n-1. So the syndrome evaluation points are
        # ω^k, ω^{k+1}, ..., ω^{n-1} applied to position indices.
        # But the syndrome components are indexed by the degree of the exponent.

        # Let me just check: can v be expressed as evaluations of a low-degree poly?
        # v_r for r = 0, ..., n-k-1. The evaluation point for component r is ω^r (or some derived value).

        # Check polynomial interpolation through (r, v_r) over F_p:
        # NOT the right thing. The relationship is multiplicative, not additive.

        # Let me check multiplicative structure: v_r = c * ω^{ar} for constants c, a.
        for a in range(n):
            ratios = []
            base = v[0]
            if base == 0:
                continue
            ok = True
            for r in range(n - k):
                expected = base * pow(omega, a * r, p) % p
                if expected != v[r]:
                    ok = False
                    break
            if ok:
                print(f"  v_r = {base} * ω^({a}*r)  [geometric sequence with ratio ω^{a}]")

    return null_vecs


# === n=6 ===
print("="*70)
print("n=6, k=3, p=7, w=2")
error_sets_6 = [(0, 1), (2, 5), (3, 4)]
analyze_null_vector(6, 3, 7, 2, error_sets_6)

# === n=8 ===
print("\n" + "="*70)
print("n=8, k=4, p=17, w=3")
error_sets_8 = [(0, 1, 2), (0, 4, 7), (0, 5, 6), (1, 3, 7), (1, 4, 6), (2, 3, 6), (2, 4, 5)]
analyze_null_vector(8, 4, 17, 3, error_sets_8)

# === n=10 ===
print("\n" + "="*70)
print("n=10, k=5, p=11, w=3")
error_sets_10 = [(0, 1, 2), (3, 4, 8), (6, 7, 9)]
analyze_null_vector(10, 5, 11, 3, error_sets_10)

# === n=12 ===
print("\n" + "="*70)
print("n=12, k=6, p=13, w=4")
error_sets_12 = [(0, 1, 2, 4), (0, 6, 8, 10), (1, 5, 10, 11), (2, 3, 5, 8), (2, 7, 9, 10), (3, 4, 6, 7)]
analyze_null_vector(12, 6, 13, 4, error_sets_12)
