#!/usr/bin/env python3
"""
Pairwise Rank v5: Direct approach — work entirely in F_p^n.

The condition from error set B (agreement set S, |S|=n-w):
  u^T c = 0 for each u in left_ker(V_S), embedded into F_p^n.

The combined conditions from M error sets form a matrix C (M*conds_per x n).
Its null space has dimension n - rank(C).
Since conditions ⊥ RS_k (dim k): null space ⊃ RS_k.
The "effective" null space (mod RS_k) has dimension n - rank(C) - k = (n-k) - rank(C).

If this is 1: the feasible directions form a 1D space mod RS_k.

To find the feasible DIRECTION: take any vector in null(C) that is NOT in RS_k.
Then: check how many error sets have conditions also vanishing on this direction.
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


def get_conditions_embedded(S_indices, L, k, p, n):
    """Get condition vectors in F_p^n from agreement set S."""
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


def dot_mod_p(a, b, p):
    return sum(x * y for x, y in zip(a, b)) % p


def analyze(n, k, p, w, error_sets):
    """Analyze the rank structure of M worst-case error sets."""
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    conds_per = n - w - k
    M = len(error_sets)

    print(f"\n{'='*70}")
    print(f"n={n}, k={k}, p={p}, w={w}, M={M}, conds/B={conds_per}")

    # Generator matrix G: G[j][i] = L[i]^j for j=0,...,k-1
    # RS_k = rowspace(G)
    G = [[pow(L[i], j, p) for i in range(n)] for j in range(k)]
    gen_rank = rank_mod_p(G, p)
    assert gen_rank == k, f"Generator rank {gen_rank} ≠ k={k}"

    # Get all condition vectors (in F_p^n) for the M error sets
    all_conds = []
    conds_by_set = []
    for B in error_sets:
        S = [i for i in range(n) if i not in B]
        conds = get_conditions_embedded(S, L, k, p, n)
        assert len(conds) == conds_per
        conds_by_set.append(conds)
        all_conds.extend(conds)

    # Verify: each condition ⊥ RS_k
    for ci, c in enumerate(all_conds):
        for gi, g in enumerate(G):
            d = dot_mod_p(c, g, p)
            assert d == 0, f"Condition {ci} · G[{gi}] = {d} ≠ 0"

    # Rank of all conditions
    r = rank_mod_p(all_conds, p)
    print(f"  Condition rank: {r}")
    print(f"  Null space dim: {n - r} = {k} (RS_k) + {n - r - k} (extra)")
    print(f"  Free dim (mod RS_k): {n - r - k}")

    # Null space of conditions
    null_vecs = kernel_mod_p(all_conds, p)
    print(f"  Full null space dim: {len(null_vecs)}")

    # Find a null vector NOT in RS_k
    # Test each null vector: is it in RS_k?
    non_RS_null = []
    for v in null_vecs:
        # Check if v ∈ RS_k: augment G with v and check rank
        aug = G + [v]
        r_aug = rank_mod_p(aug, p)
        if r_aug > k:  # v not in RS_k
            non_RS_null.append(v)

    print(f"  Non-RS null vectors: {len(non_RS_null)}")

    if non_RS_null:
        v = non_RS_null[0]
        print(f"  Representative null vector: {v}")

        # VERIFY: v · c = 0 for all conditions
        for ci, c in enumerate(all_conds):
            d = dot_mod_p(v, c, p)
            assert d == 0, f"v · cond[{ci}] = {d} ≠ 0"
        print(f"  ✓ v is orthogonal to all {len(all_conds)} conditions")

        # Now: for ALL C(n,w) error sets, check if v satisfies their conditions
        count = 0
        matching = []
        for B in combinations(range(n), w):
            S = [i for i in range(n) if i not in B]
            conds = get_conditions_embedded(S, L, k, p, n)
            all_zero = True
            for c in conds:
                if dot_mod_p(v, c, p) != 0:
                    all_zero = False
                    break
            if all_zero:
                count += 1
                matching.append(B)

        print(f"\n  Error sets B with v ⊥ all conditions: {count}")
        print(f"  (Our M error sets: {M})")
        if count != M:
            print(f"  NOTE: v satisfies MORE error sets than our specific M!")

        # Print matching error sets
        our_set = set(tuple(sorted(B)) for B in error_sets)
        in_ours = [B for B in matching if B in our_set]
        not_in_ours = [B for B in matching if B not in our_set]
        print(f"  In our M: {len(in_ours)}, Additional: {len(not_in_ours)}")
        for B in not_in_ours[:10]:
            print(f"    Additional: B = {B}")

        # The KEY QUESTION: what makes v special?
        # v is in null(conditions) and v ∉ RS_k.
        # So v represents a "non-codeword" direction.
        # The number of error sets compatible with v is the LIST SIZE at center v.

        # Check: is v a polynomial evaluation of degree exactly k?
        # v = (f(L[0]), ..., f(L[n-1])) for f of degree k (not <k).
        # The syndrome of v is s = Hv ≠ 0.
        # v|_S agrees with a degree-<k polynomial iff the conditions vanish.

        # Check polynomial structure of v:
        # Interpolate v through all n points — what is the degree?
        # For n points over F_p: unique polynomial of degree < n.

        # Use Lagrange interpolation:
        # f(x) = sum_i v[i] * prod_{j≠i} (x - L[j]) / (L[i] - L[j])

        # Instead of computing the full polynomial, just check: is v of degree k?
        # v is degree < k iff v ∈ RS_k (we know v ∉ RS_k).
        # v is degree < k+1 iff v ∈ RS_{k+1}.
        G_ext = [[pow(L[i], j, p) for i in range(n)] for j in range(k + 1)]
        aug2 = G_ext + [v]
        r_ext = rank_mod_p(G_ext, p)
        r_aug2 = rank_mod_p(aug2, p)
        if r_aug2 == r_ext:
            print(f"\n  v ∈ RS_{{k+1}} (degree ≤ {k})")
            # Find the coefficients: v = sum_{j=0}^{k} a_j * G_ext[j]
            # Solve G_ext * a = v (overdetermined, but v is in the span)
            pass
        else:
            # Check higher degrees
            for deg in range(k + 2, n):
                G_deg = [[pow(L[i], j, p) for i in range(n)] for j in range(deg)]
                aug3 = G_deg + [v]
                if rank_mod_p(aug3, p) == rank_mod_p(G_deg, p):
                    print(f"\n  v ∈ RS_{{{deg}}} (degree ≤ {deg-1})")
                    break

        # Analyze v as evaluations: v_i for each L[i] = ω^i
        print(f"\n  v values: v = [", end="")
        for i in range(n):
            print(f"v(ω^{i})={v[i]}", end=", " if i < n-1 else "]\n")

        # Check: is v(ω^i) = ω^{ai+b} (geometric)?
        if v[0] != 0:
            for a in range(n):
                ratio = v[0] * pow(pow(omega, 0, p), p - 2, p) % p  # v[0] / ω^0 = v[0]
                test = [v[0] * pow(omega, a * i, p) % p for i in range(n)]
                if test == v:
                    print(f"  v(ω^i) = {v[0]} * ω^({a}*i): GEOMETRIC SEQUENCE!")

        # Check: is v a monomial evaluation x^d for some d?
        for d in range(n):
            test = [pow(L[i], d, p) for i in range(n)]
            # Check proportionality
            if v[0] == 0 and test[0] == 0:
                # Need to check nonzero entry
                for i in range(n):
                    if v[i] != 0 and test[i] != 0:
                        ratio = v[i] * pow(test[i], p-2, p) % p
                        if all((v[j] - ratio * test[j]) % p == 0 for j in range(n)):
                            print(f"  v ∝ (ω^{{i*{d}}})_i = evaluation of x^{d}, ratio={ratio}")
                        break
            elif v[0] != 0 and test[0] != 0:
                ratio = v[0] * pow(test[0], p-2, p) % p
                if all((v[j] - ratio * test[j]) % p == 0 for j in range(n)):
                    print(f"  v ∝ (ω^{{i*{d}}})_i = evaluation of x^{d}, ratio={ratio}")

    # Cumulative rank
    print(f"\n  Cumulative rank:")
    cumulative = list(G)  # start with RS_k basis
    for i in range(M):
        cumulative.extend(conds_by_set[i])
        r = rank_mod_p(cumulative, p)
        print(f"    After G + B_0..B_{i}: rank = {r} / {n}")


# === Data from v3 ===
print("n=6, k=3, p=7, w=2")
analyze(6, 3, 7, 2, [(0, 1), (2, 5), (3, 4)])

print("\nn=8, k=4, p=17, w=3")
analyze(8, 4, 17, 3, [(0, 1, 2), (0, 4, 7), (0, 5, 6), (1, 3, 7), (1, 4, 6), (2, 3, 6), (2, 4, 5)])

print("\nn=10, k=5, p=11, w=3")
analyze(10, 5, 11, 3, [(0, 1, 2), (3, 4, 8), (6, 7, 9)])

print("\nn=12, k=6, p=13, w=4")
analyze(12, 6, 13, 4, [(0, 1, 2, 4), (0, 6, 8, 10), (1, 5, 10, 11), (2, 3, 5, 8), (2, 7, 9, 10), (3, 4, 6, 7)])
