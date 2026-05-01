#!/usr/bin/env python3
"""
Pairwise Rank v3: Efficient approach for larger n.

Key insight from v2: the worst-case M conditions have combined rank = n-k-1.
The feasible syndrome set is 1-dimensional (a line in F_p^{n-k}).

Strategy: instead of enumerating all syndromes, work in the condition space.
For each M-tuple of error sets, check if the combined conditions have rank n-k-1.

For n=12: use the fact that M is p-independent, so use smallest p = 13.
Enumerate codewords via the generating matrix, not coefficient vectors.
"""

from itertools import combinations
from math import comb
from collections import defaultdict
import time


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


def left_kernel_mod_p(mat, p):
    m = len(mat)
    n = len(mat[0])
    matT = [[mat[i][j] for i in range(m)] for j in range(n)]
    return right_kernel_mod_p(matT, p)


def right_kernel_mod_p(mat, p):
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


def analysis_exhaustive_codewords(n, k, p, w):
    """
    For small enough p^k: enumerate all codewords, find worst-case center,
    analyze rank structure.
    """
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"\n{'='*70}")
    print(f"n={n}, k={k}, p={p}, w={w}")
    print(f"conds/B = {n-w-k}, syn_dim = {n-k}")

    # Generate all codewords
    t0 = time.time()
    codewords = []
    for idx in range(p**k):
        a = []
        temp = idx
        for _ in range(k):
            a.append(temp % p)
            temp //= p
        f = tuple(sum(a[j] * pow(L[i], j, p) for j in range(k)) % p for i in range(n))
        codewords.append(f)
    print(f"  Generated {len(codewords)} codewords in {time.time()-t0:.1f}s")

    # For each pair of codewords (f1, f2) at distance ≤ 2w:
    # they could both be in the list of some center c.
    # d(f1, f2) = d1 + d2 where d1 = d(c,f1), d2 = d(c,f2), and d(f1,f2) ≤ d1+d2.
    # For both to be at distance ≤ w from c: d(f1,f2) ≤ 2w.

    # Strategy: for each codeword pair (f1, f2) with d(f1,f2) = d_12 ≤ 2w:
    # Find centers c with d(c,f1) ≤ w AND d(c,f2) ≤ w.
    # For each such c: count ALL codewords at distance ≤ w.

    # This is still O(p^{2k}) pairs. For p=13, k=6: 13^12 ≈ 10^13 pairs. Too many.

    # Better: use the syndrome approach.
    # M(s) = |{e : He = s, wt(e) ≤ w}|.
    # For each error vector e with wt(e) ≤ w: compute He.

    # Number of weight-≤w vectors: sum_{j=1}^w C(n,j) * (p-1)^j
    # For n=12, w=4, p=13: C(12,1)*12 + C(12,2)*144 + C(12,3)*1728 + C(12,4)*20736
    # = 144 + 9504 + 380160 + 10264320 = 10,654,128
    # That's feasible!

    H = [[pow(L[i], k + r, p) for i in range(n)] for r in range(n - k)]

    t0 = time.time()
    # Count by weight
    syndrome_lists = defaultdict(lambda: defaultdict(int))  # s -> {w: count}

    total = 0
    for wt in range(1, w + 1):
        count_wt = 0
        for positions in combinations(range(n), wt):
            # Enumerate all nonzero value assignments
            def enum_nonzero(wt, p):
                if wt == 0:
                    yield ()
                    return
                for v in range(1, p):
                    for rest in enum_nonzero(wt - 1, p):
                        yield (v,) + rest

            for vals in enum_nonzero(wt, p):
                # Compute syndrome
                s = [0] * (n - k)
                for j, pos in enumerate(positions):
                    for r in range(n - k):
                        s[r] = (s[r] + vals[j] * H[r][pos]) % p
                s_tuple = tuple(s)
                syndrome_lists[s_tuple][wt] += 1
                count_wt += 1
                total += 1

        print(f"  Weight {wt}: {count_wt} vectors ({time.time()-t0:.1f}s)")

    # Now compute M(s) = total list at distance ≤ w
    max_M = 0
    best_s = None
    M_dist = defaultdict(int)

    for s, wt_counts in syndrome_lists.items():
        m = sum(wt_counts.values())
        M_dist[m] += 1
        if m > max_M:
            max_M = m
            best_s = s

    print(f"\n  List size distribution (M at dist ≤ {w}):")
    for m in sorted(M_dist.keys(), reverse=True)[:10]:
        print(f"    M={m}: {M_dist[m]} syndromes")
    print(f"  Max M = {max_M}")

    # Now find the M error sets for best_s
    # These are the positions sets achieving wt ≤ w with syndrome = best_s
    best_errors = []
    for wt in range(1, w + 1):
        for positions in combinations(range(n), wt):
            def enum_nonzero(wt, p):
                if wt == 0:
                    yield ()
                    return
                for v in range(1, p):
                    for rest in enum_nonzero(wt - 1, p):
                        yield (v,) + rest
            for vals in enum_nonzero(wt, p):
                s = [0] * (n - k)
                for j, pos in enumerate(positions):
                    for r in range(n - k):
                        s[r] = (s[r] + vals[j] * H[r][pos]) % p
                if tuple(s) == best_s:
                    best_errors.append((positions, vals))

    print(f"\n  {len(best_errors)} error vectors at best syndrome")

    # Group by position set (error set B)
    pos_groups = defaultdict(list)
    for positions, vals in best_errors:
        pos_groups[positions].append(vals)

    unique_pos = sorted(pos_groups.keys())
    print(f"  Unique error position sets: {len(unique_pos)}")

    # Only analyze errors of weight exactly w (these give the dominant M)
    exact_w = [B for B in unique_pos if len(B) == w]
    print(f"  At weight exactly {w}: {len(exact_w)} position sets")
    if not exact_w:
        print("  No errors at exact weight, checking lower weights...")
        for ww in range(w, 0, -1):
            exact_ww = [B for B in unique_pos if len(B) == ww]
            if exact_ww:
                print(f"  At weight {ww}: {len(exact_ww)} position sets")
                exact_w = exact_ww
                break

    M_pos = len(exact_w)
    wt_used = len(exact_w[0]) if exact_w else w
    conds_per = n - wt_used - k

    print(f"\n  Analyzing M = {M_pos} error sets (weight {wt_used}, conds/B = {conds_per})")

    for i, B in enumerate(exact_w[:20]):
        S = [j for j in range(n) if j not in B]
        print(f"    B_{i} = {B}, S = {S}")

    # Compute conditions
    all_conds = []
    for B in exact_w:
        S = [j for j in range(n) if j not in B]
        conds = get_conditions(S, L, k, p, n)
        all_conds.append(conds)

    # Pairwise overlaps and ranks
    if M_pos <= 20:
        print(f"\n  Pairwise overlap matrix:")
        for i in range(M_pos):
            row = []
            for j in range(M_pos):
                if i == j:
                    row.append(f" {wt_used}")
                else:
                    ov = len(set(exact_w[i]) & set(exact_w[j]))
                    row.append(f" {ov}")
            print(f"    [{','.join(row)}]")

    # Pairwise rank
    if M_pos <= 20:
        print(f"\n  Pairwise ranks:")
        for i in range(M_pos):
            for j in range(i + 1, M_pos):
                combined = all_conds[i] + all_conds[j]
                cr = rank_mod_p(combined, p)
                ov = len(set(exact_w[i]) & set(exact_w[j]))
                print(f"    B_{i},B_{j}: overlap={ov}, rank={cr}/{2*conds_per}")

    # Cumulative rank
    print(f"\n  Cumulative rank:")
    cumulative = []
    for i in range(M_pos):
        cumulative.extend(all_conds[i])
        r = rank_mod_p(cumulative, p)
        expected = min((i + 1) * conds_per, n - k)
        print(f"    After B_0..B_{i}: rank = {r}/{expected}")

    full = []
    for c in all_conds:
        full.extend(c)
    full_r = rank_mod_p(full, p)
    print(f"\n  Full {M_pos}-set rank: {full_r} / {n-k}")
    print(f"  Codimension = {full_r}, free dim = {n-k - full_r}")

    return M_pos, full_r, n - k


# Run
# Small cases (verification)
analysis_exhaustive_codewords(6, 3, 7, 2)
analysis_exhaustive_codewords(8, 4, 17, 3)
analysis_exhaustive_codewords(10, 5, 11, 3)

# The key case: n=12
analysis_exhaustive_codewords(12, 6, 13, 4)
