#!/usr/bin/env python3
"""
Pairwise Rank Lemma — v2: correct list-size computation.

For each center c, a codeword f is in the list at distance w iff
d(c, f) ≤ w, i.e., |{i : c_i ≠ f_i}| ≤ w.

Each such f gives error set B_f = {i : c_i ≠ f_i}.

M = number of DISTINCT codewords in the ball.

For each error set B_f, the agreement set S_f = {i : c_i = f_i}
contributes (|S_f| - k) conditions on the syndrome.

This script:
1. Finds the worst-case center c (max M)
2. Lists the M codewords and their error sets
3. Computes the pairwise rank of the conditions
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


def left_kernel_mod_p(mat, p):
    """Left kernel of mat (m x n): vectors u (length m) with u * mat = 0."""
    m = len(mat)
    n = len(mat[0])
    matT = [[mat[i][j] for i in range(m)] for j in range(n)]
    return right_kernel_mod_p(matT, p)


def right_kernel_mod_p(mat, p):
    """Right kernel of mat (m x n): vectors x (length n) with mat * x = 0."""
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
    """
    Get the linear conditions on the center c from agreement set S.
    S_indices: list of indices into L.
    Returns list of condition vectors in F_p^n.
    """
    n_w = len(S_indices)
    if n_w <= k:
        return []  # no conditions (underdetermined)

    # V_S: n_w x k Vandermonde submatrix
    V_S = [[pow(L[S_indices[j]], l, p) for l in range(k)] for j in range(n_w)]

    # Left kernel
    lk = left_kernel_mod_p(V_S, p)

    conditions = []
    for u in lk:
        v = [0] * n
        for j, idx in enumerate(S_indices):
            v[idx] = u[j] % p
        conditions.append(v)
    return conditions


def compute_list_and_rank(n, k, p, w):
    """
    Compute list sizes and rank structure for RS[n,k] over F_p at distance w.
    """
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    # Parity check matrix H[r][i] = L[i]^(k+r)
    H = [[pow(L[i], k + r, p) for i in range(n)] for r in range(n - k)]

    # All RS codewords: for each coefficient vector a = (a_0, ..., a_{k-1}),
    # f_i = a_0 + a_1*L[i] + ... + a_{k-1}*L[i]^{k-1}
    # Total: p^k codewords.

    print(f"\n{'='*70}")
    print(f"n={n}, k={k}, p={p}, w={w}")
    print(f"conds/B = {n-w-k}, syndrome_dim = {n-k}")
    print(f"#codewords = p^k = {p**k}")

    if p**k > 5_000_000:
        print("  Too many codewords for exhaustive search")
        return

    # Precompute all codewords
    codewords = []
    for idx in range(p**k):
        a = []
        temp = idx
        for _ in range(k):
            a.append(temp % p)
            temp //= p
        # f_i = sum_j a[j] * L[i]^j mod p
        f = [sum(a[j] * pow(L[i], j, p) for j in range(k)) % p for i in range(n)]
        codewords.append(tuple(f))

    # For each center c ∈ F_p^n, compute M(c,w) = |{f ∈ RS_k : d(c,f) ≤ w}|.
    # But p^n is too large. Instead, for each syndrome s:
    # M(s,w) = max over c with Hc=s of |{f : d(c,f) ≤ w}| - but M depends on c not just s!
    #
    # Wait: M DOES depend only on s. Because for any c, c' with Hc = Hc':
    # c - c' ∈ RS_k. So d(c, f) = d(c', f + (c-c')) and f + (c-c') is also a codeword.
    # So M(c, w) = M(c', w). M depends only on the syndrome.

    # So: pick one representative c per syndrome, compute M.

    # Compute syndrome for each codeword-center pair.
    # For efficiency: for each center c (representative), and each codeword f,
    # compute d(c, f).

    # Actually, let's just compute: for c = (0,0,...,0) (syndrome s = 0), M = A_w = 0
    # (no codeword at distance ≤ w from zero vector... wait, the zero codeword IS at distance 0!)
    # M = 1 + A_1 + ... + A_w. For w < d: M = 1 (only the zero codeword).

    # For non-trivial M: need non-codeword centers.

    # Strategy: for each codeword f, the error vector e = c - f has syndrome He = Hc = s.
    # So: for center c with syndrome s, the codewords at distance w are those f where
    # wt(c - f) ≤ w, i.e., wt(e) ≤ w where He = s.

    # M(s) = |{e : He = s, wt(e) ≤ w}|
    # This counts VECTORS, not codewords. But each e corresponds to f = c - e.

    # Wait, wt(e) = d(c, f) where f = c - e. And different e give different f. So M(s) = |{e : He = s, wt(e) ≤ w}|.

    # For the ACTUAL list decoding, we need d(c,f) = exactly some value ≤ w.
    # So M(s, ≤w) = sum_{j=0}^{w} |{e : He = s, wt(e) = j}| = sum_{j=0}^w N_j(s).

    # Let me compute N_w(s) for all s via FFT-like approach.

    # For small p^(n-k): iterate over all syndromes.

    if p**(n-k) > 2_000_000:
        print("  Syndrome space too large")
        return

    # For each error vector e with wt(e) ≤ w, compute syndrome He.
    syndrome_to_errors = defaultdict(list)

    # Enumerate all e with wt(e) ≤ w
    for wt in range(1, w + 1):  # skip wt=0 (trivial)
        for positions in combinations(range(n), wt):
            # For each nonzero assignment to these positions
            if wt == 1:
                for v0 in range(1, p):
                    e = [0] * n
                    e[positions[0]] = v0
                    # syndrome = He
                    s = tuple(sum(H[r][i] * e[i] for i in range(n)) % p for r in range(n-k))
                    syndrome_to_errors[s].append((positions, tuple(e[i] for i in positions)))
            elif wt == 2:
                for v0 in range(1, p):
                    for v1 in range(1, p):
                        e = [0] * n
                        e[positions[0]] = v0
                        e[positions[1]] = v1
                        s = tuple(sum(H[r][i] * e[i] for i in range(n)) % p for r in range(n-k))
                        syndrome_to_errors[s].append((positions, (v0, v1)))
            elif wt == 3:
                for v0 in range(1, p):
                    for v1 in range(1, p):
                        for v2 in range(1, p):
                            e = [0] * n
                            e[positions[0]] = v0
                            e[positions[1]] = v1
                            e[positions[2]] = v2
                            s = tuple(sum(H[r][i] * e[i] for i in range(n)) % p for r in range(n-k))
                            syndrome_to_errors[s].append((positions, (v0, v1, v2)))
            elif wt <= w:
                # General case
                def enum_vals(wt, p):
                    if wt == 0:
                        yield ()
                        return
                    for v in range(1, p):
                        for rest in enum_vals(wt - 1, p):
                            yield (v,) + rest

                for vals in enum_vals(wt, p):
                    e = [0] * n
                    for i, pos in enumerate(positions):
                        e[pos] = vals[i]
                    s = tuple(sum(H[r][i] * e[i] for i in range(n)) % p for r in range(n-k))
                    syndrome_to_errors[s].append((positions, vals))

    # Also add wt=0 (the trivial codeword)
    zero_s = tuple([0] * (n - k))
    syndrome_to_errors[zero_s].append(((), ()))

    # Now: for each syndrome s, M(s) = len(syndrome_to_errors[s])
    # But this includes wt=0 (the codeword c itself, which always contributes M=1)
    # We count errors at distance EXACTLY w for the error set analysis.

    # For list size at distance ≤ w:
    # Count only errors with 1 ≤ wt ≤ w for non-trivial codewords.

    # Find worst-case syndrome
    max_M = 0
    best_s = None
    M_dist = defaultdict(int)

    # For list-decoding M at distance exactly w:
    syndrome_errors_at_w = defaultdict(list)
    for s, errors in syndrome_to_errors.items():
        for positions, vals in errors:
            if len(positions) == w:
                syndrome_errors_at_w[s].append((positions, vals))

    for s, errors in syndrome_errors_at_w.items():
        m = len(errors)
        M_dist[m] += 1
        if m > max_M:
            max_M = m
            best_s = s

    print(f"\nList size distribution at distance exactly w={w}:")
    for m in sorted(M_dist.keys(), reverse=True)[:10]:
        print(f"  M={m}: {M_dist[m]} syndromes")

    print(f"\nMax M = {max_M} at syndrome {best_s}")

    if max_M == 0:
        print("  No non-trivial list (w < d-1)")
        return

    # Now analyze the worst-case errors
    worst_errors = syndrome_errors_at_w[best_s]
    print(f"\nWorst-case {max_M} error sets (at distance exactly {w}):")

    error_sets = []
    for positions, vals in worst_errors:
        B = set(positions)
        error_sets.append(B)

    # Deduplicate by error SET (different values can give same positions)
    # Actually, for RS (MDS), different codewords give different error positions.
    # So each position set appears at most... let's check.
    pos_count = defaultdict(int)
    for B in error_sets:
        pos_count[tuple(sorted(B))] += 1

    unique_error_sets = list(set(tuple(sorted(B)) for B in error_sets))
    print(f"  Unique error position sets: {len(unique_error_sets)}")
    print(f"  Multiplicity distribution: {dict(sorted(defaultdict(int, {v: sum(1 for x in pos_count.values() if x == v) for v in set(pos_count.values())}).items()))}")

    # For the rank analysis: we care about DISTINCT error SETS (position patterns).
    # Each error set contributes (n-w-k) conditions.
    M_pos = len(unique_error_sets)
    conds_per = n - w - k

    print(f"\n  M (distinct error sets) = {M_pos}")
    print(f"  Conditions per error set = {conds_per}")

    if M_pos == 0:
        return

    # Compute conditions for each unique error set
    all_conds = []
    for B_tuple in unique_error_sets:
        S = [i for i in range(n) if i not in B_tuple]
        conds = get_conditions(S, L, k, p, n)
        all_conds.append(conds)
        assert len(conds) == conds_per, f"Expected {conds_per} conds, got {len(conds)}"

    # Print error sets and agreement sets
    for i, B_tuple in enumerate(unique_error_sets[:20]):
        S = [j for j in range(n) if j not in B_tuple]
        print(f"  B_{i} = {B_tuple}, S = {S}")

    # Pairwise overlap and rank
    print(f"\n  Pairwise analysis:")
    for i in range(min(M_pos, 15)):
        for j in range(i+1, min(M_pos, 15)):
            overlap = len(set(unique_error_sets[i]) & set(unique_error_sets[j]))
            combined = all_conds[i] + all_conds[j]
            cr = rank_mod_p(combined, p)
            redundancy = 2 * conds_per - cr
            print(f"    B_{i},B_{j}: overlap={overlap}, rank={cr}/{2*conds_per}, Φ={redundancy}")

    # Cumulative rank
    print(f"\n  Cumulative rank:")
    cumulative = []
    for i in range(M_pos):
        cumulative.extend(all_conds[i])
        r = rank_mod_p(cumulative, p)
        expected = min((i+1) * conds_per, n - k)
        print(f"    After B_0..B_{i}: rank = {r}/{expected}")

    # Full rank
    all_flat = []
    for conds in all_conds:
        all_flat.extend(conds)
    full_r = rank_mod_p(all_flat, p)
    print(f"\n  Full {M_pos}-set rank: {full_r} / {n-k}")
    print(f"  Total conditions: {M_pos * conds_per}, redundancy: {M_pos * conds_per - full_r}")


# Run for key cases

# n=6, k=3, p=7, w_J = ceil(0.293*6) = 2
compute_list_and_rank(6, 3, 7, 2)

# n=8, k=4, p=17, w_J = ceil(0.293*8) = 3
compute_list_and_rank(8, 4, 17, 3)

# n=10, k=5, p=11, w_J = ceil(0.293*10) = 3
compute_list_and_rank(10, 5, 11, 3)

# n=12, k=6, p=13, w_J = ceil(0.293*12) = 4
compute_list_and_rank(12, 6, 13, 4)
