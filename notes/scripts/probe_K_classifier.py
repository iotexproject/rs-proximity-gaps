"""probe_K_classifier.py — count K = # distinct 1-dim subspaces L ⊆ U arising
as V_T ∩ U for some |T|=w_R, for rank-2 above-J f.

Hypothesis:
- K_full := #{T : V_T ⊇ U} should be 0 for above-J (else lift extension contradicts above-J).
- K = 2 ⇔ factored saturating sub-stratum (closed in note 0112).
- K ≤ 1 for non-factored cases (this is the conjecture this script tests).

If verified, then for non-factored above-J rank-2 f, V_δ ⊆ σ^{-1}(L) for ≤ 1 line L,
so |V_δ| ≤ |σ^{-1}(L)| ≤ 2q-1 (bidegree-(1,1) curve, SZ).
This combined with note 0112 closes Direction A bound for ALL rank-2 cases.
"""
from __future__ import annotations
import sys, os, random
from itertools import product, combinations
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, parity_check, gauss_rank
from probe_step5_n32_studio import (
    P, N0, K0, R, N_R, W_J,
    evaluate_dft, fold_at_alpha, compute_corner_syndromes,
)
from mds_decoder import is_above_johnson_sampling
from probe_rank2_struct_fast import mobius_psi


W_R = 3


def line_canonical(v, p):
    """Canonical rep of 1-dim subspace span(v). Normalize first nonzero = 1."""
    for i, x in enumerate(v):
        if x % p != 0:
            inv = pow(x % p, p - 2, p)
            return tuple((y * inv) % p for y in v)
    return tuple((y % p) for y in v)


def rref_basis(vectors, p):
    """Row-reduce stack of vectors; return basis (echelon form rows, leading 1s)."""
    M = [list(v) for v in vectors if any(x % p != 0 for x in v)]
    if not M:
        return []
    cols = len(M[0])
    rank = 0
    col = 0
    while rank < len(M) and col < cols:
        pr = None
        for r in range(rank, len(M)):
            if M[r][col] % p != 0:
                pr = r
                break
        if pr is None:
            col += 1
            continue
        M[rank], M[pr] = M[pr], M[rank]
        inv = pow(M[rank][col] % p, p - 2, p)
        M[rank] = [(x * inv) % p for x in M[rank]]
        for r in range(len(M)):
            if r != rank and M[r][col] % p != 0:
                f = M[r][col]
                M[r] = [(M[r][c] - f * M[rank][c]) % p for c in range(cols)]
        rank += 1
        col += 1
    return [M[i] for i in range(rank)]


def intersection_basis(U_basis, V_basis, p):
    """Zassenhaus: dim cols=cols. Stack rows [u|u] for u in U, [v|0] for v in V.
    RREF; rows with first half all zero give intersection in second half."""
    if not U_basis or not V_basis:
        return []
    cols = len(U_basis[0])
    M = [list(u) + list(u) for u in U_basis] + [list(v) + [0] * cols for v in V_basis]
    nrows = len(M)
    ncols = 2 * cols
    rank = 0
    col = 0
    while rank < nrows and col < ncols:
        pr = None
        for r in range(rank, nrows):
            if M[r][col] % p != 0:
                pr = r
                break
        if pr is None:
            col += 1
            continue
        M[rank], M[pr] = M[pr], M[rank]
        inv = pow(M[rank][col] % p, p - 2, p)
        M[rank] = [(x * inv) % p for x in M[rank]]
        for r in range(nrows):
            if r != rank and M[r][col] % p != 0:
                f = M[r][col]
                M[r] = [(M[r][c] - f * M[rank][c]) % p for c in range(ncols)]
        rank += 1
        col += 1
    inter = []
    for row in M:
        if all(row[c] % p == 0 for c in range(cols)) and any(row[c] % p != 0 for c in range(cols, 2 * cols)):
            inter.append([row[c] for c in range(cols, 2 * cols)])
    return rref_basis(inter, p)


def K_classifier(f, chain, H_R, p, n_R, w_R):
    """Compute (K, dim_distr, K_full, dim_U) for rank-≤2 above-J f.
    K = # distinct 1-dim L ⊆ U arising as V_T ∩ U.
    K_full = #{T : V_T ⊇ U}.
    dim_distr: count of dim(V_T ∩ U) over all T.
    """
    corners = compute_corner_syndromes(f, chain, R, p, H_R)
    psi = mobius_psi(corners, p)
    U_vecs = [psi[(0, 0)], psi[(1, 0)], psi[(0, 1)], psi[(1, 1)]]
    U_basis = rref_basis(U_vecs, p)
    dim_U = len(U_basis)
    if dim_U == 0:
        return 0, {}, 0, 0

    H_R_cols = [list(col) for col in zip(*H_R)]
    K_lines = set()
    K_full = 0
    dim_distr = Counter()

    for T in combinations(range(n_R), w_R):
        V_T_basis = rref_basis([H_R_cols[j] for j in T], p)
        inter = intersection_basis(U_basis, V_T_basis, p)
        d = len(inter)
        dim_distr[d] += 1
        if d == 1:
            K_lines.add(line_canonical(inter[0], p))
        if d >= dim_U:
            K_full += 1

    return len(K_lines), dict(dim_distr), K_full, dim_U


def main():
    chain = setup_chain(P, N0, K0, R=R)
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, P)
    p = P
    n_R = N_R
    w_R = W_R

    print(f"# probe_K_classifier — count K = # distinct V_T-lines in U for rank-2 above-J f")
    print(f"# Setup: p={p}, n_0={N0}, k_0={K0}, R={R}, n_R={n_R}, w_R={w_R}, w_J={W_J}")
    print(f"# Hypothesis 1 (lift contradiction): K_full = 0 for above-J.")
    print(f"# Hypothesis 2 (saturating classifier): K=2 ⇔ factored bilinear σ.")
    print(f"# Hypothesis 3 (non-factored): K ≤ 1 for non-factored ⇒ |V_δ| ≤ 2q-1 via single curve.")
    print()

    falsifiers = [
        ((12, 18, 22), (59, 73, 36), 0, "non-sat"),
        ((14, 18, 31), (90, 90, 88), 193, "factored"),
        ((9, 19, 27), (16, 86, 49), 193, "factored"),
        ((13, 22, 30), (23, 17, 17), 97, "non-fact"),
        ((9, 10, 22, 25, 26), (30, 38, 58, 50, 69), 97, "non-fact"),
        ((14, 18, 28, 30), (91, 88, 70, 22), 97, "non-fact"),
    ]
    print("# === Known falsifiers (with prior |V_δ|) ===")
    for i, (positions, coefs, vd, label) in enumerate(falsifiers):
        fhat = [0] * N0
        for pos, c in zip(positions, coefs):
            fhat[pos] = c
        f = evaluate_dft(fhat, chain[0][0], p)
        K, dim_distr, K_full, dim_U = K_classifier(f, chain, H_R, p, n_R, w_R)
        print(f"  fals#{i+1} ({label}, |V_δ|={vd:3d}): "
              f"dim_U={dim_U}, K={K}, K_full={K_full}, dim_distr={dict(dim_distr)}")

    print()
    print("# === Random rank-2 above-J ===")
    rng = random.Random(2027)
    n_done = 0
    n_tried = 0
    fact_results = []
    nonfact_results = []
    while n_done < 80 and n_tried < 5000:
        n_tried += 1
        sparsity = rng.choice([2, 3])
        positions = tuple(sorted(rng.sample(range(K0, N0), sparsity)))
        coefs = tuple(rng.randrange(1, p) for _ in range(sparsity))
        fhat = [0] * N0
        for pos, c in zip(positions, coefs):
            fhat[pos] = c
        f = evaluate_dft(fhat, chain[0][0], p)
        above, _, _ = is_above_johnson_sampling(
            f, chain[0][0], K0, p, W_J, n_samples=20000, batch=4096, seed=8888,
            return_evidence=True,
        )
        if not above:
            continue
        corners = compute_corner_syndromes(f, chain, R, p, H_R)
        nz = [list(s) for s in corners.values() if any(x != 0 for x in s)]
        rk = gauss_rank(nz, p) if nz else 0
        if rk != 2:
            continue
        psi = mobius_psi(corners, p)
        p00z = all(x == 0 for x in psi[(0, 0)])
        p10z = all(x == 0 for x in psi[(1, 0)])
        p01z = all(x == 0 for x in psi[(0, 1)])
        p11nz = any(x != 0 for x in psi[(1, 1)])
        is_factored = (p00z and (p10z or p01z) and p11nz)
        K, dim_distr, K_full, dim_U = K_classifier(f, chain, H_R, p, n_R, w_R)
        label = "factored" if is_factored else "non-fact"
        print(f"  rand#{n_done+1} pos={positions} ({label}): K={K}, K_full={K_full}, dim_distr={dict(dim_distr)}")
        if is_factored:
            fact_results.append((K, K_full, dim_distr))
        else:
            nonfact_results.append((K, K_full, dim_distr))
        n_done += 1

    print()
    print(f"# === Summary ===")
    print(f"# Factored cases ({len(fact_results)}):")
    if fact_results:
        K_distr = Counter(r[0] for r in fact_results)
        Kfull_distr = Counter(r[1] for r in fact_results)
        for k, cnt in sorted(K_distr.items()):
            print(f"  K = {k}: {cnt}")
        print(f"  K_full distr: {dict(Kfull_distr)}")
    print(f"# Non-factored cases ({len(nonfact_results)}):")
    if nonfact_results:
        K_distr = Counter(r[0] for r in nonfact_results)
        Kfull_distr = Counter(r[1] for r in nonfact_results)
        for k, cnt in sorted(K_distr.items()):
            print(f"  K = {k}: {cnt}")
        print(f"  K_full distr: {dict(Kfull_distr)}")

    # Hypothesis check
    print()
    nf_K_max = max((r[0] for r in nonfact_results), default=0)
    nf_Kfull_max = max((r[1] for r in nonfact_results), default=0)
    f_K_distr = Counter(r[0] for r in fact_results)
    f_Kfull_max = max((r[1] for r in fact_results), default=0)

    print(f"# Hypothesis 1 (K_full = 0 for above-J): "
          f"non-fact max K_full = {nf_Kfull_max}, factored max K_full = {f_Kfull_max}")
    print(f"#   {'✓ HOLDS' if nf_Kfull_max == 0 and f_Kfull_max == 0 else '✗ FAILS'}")
    print(f"# Hypothesis 3 (K ≤ 1 for non-factored): max K = {nf_K_max}")
    print(f"#   {'✓ HOLDS' if nf_K_max <= 1 else '✗ FAILS'}")


if __name__ == '__main__':
    main()
