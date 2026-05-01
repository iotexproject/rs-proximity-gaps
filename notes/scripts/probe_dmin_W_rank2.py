"""probe_dmin_W_rank2.py — exact d_min(W) for rank-2 above-J f at n_0=32, R=2.

Lemma A target: prove d_min(W) > w_R = 3 for all rank-2 above-J f.
Empirically (note 0108): 0 bad lines for all 443 cases ⟺ d_min(W) > 3 always.
This probe computes the exact d_min(W) ∈ {4, 5} per case to look for structural
patterns (e.g., always MDS = 5, or sometimes 4 with characteristic structure).

W = C_R + span{Q_b : b ∈ {0,1}^R}, a (k_R + r)-dim code in F_q^{n_R}.
For r = 2: dim(W) = 4, length n_R = 8 over F_97. Singleton: d_min(W) ≤ 5.

Usage: python3 probe_dmin_W_rank2.py [n_workers] [seed]
"""
from __future__ import annotations
import sys, os, time, random, math
from itertools import product, combinations
from multiprocessing import Pool, cpu_count

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, parity_check, gauss_rank
from mds_decoder import is_above_johnson_sampling
from probe_step5_n32_studio import (
    P, N0, K0, R, N_R, W_J,
    evaluate_dft, fold_at_alpha, compute_corner_syndromes,
)


def gauss_rank_local(rows, p):
    """Modified gauss_rank that doesn't mutate the input (defensive copy)."""
    return gauss_rank([list(r) for r in rows], p)


def build_G_W(f, chain, R_local, p, k_R, n_R, L_R):
    """Build (k_R + r) × n_R generator matrix of W = C_R + span{Q_b}.
    Returns (G_W, dim_W) where G_W is reduced to a basis."""
    # C_R generator: rows g_i[j] = L_R[j]^i for i ∈ [0, k_R)
    G_R = [[pow(L_R[j], i, p) for j in range(n_R)] for i in range(k_R)]
    # Q_b for b ∈ {0,1}^R
    Qs = []
    for b in product([0, 1], repeat=R_local):
        Q_b = fold_at_alpha(f, chain, list(b), p)
        Qs.append(Q_b)
    # Combine and reduce to basis
    all_rows = G_R + Qs
    # Gauss elimination keeping pivot rows
    M = [list(r) for r in all_rows]
    n_cols = n_R
    pivot_rows = []
    pivot_cols = []
    cur = 0
    for col in range(n_cols):
        if cur >= len(M):
            break
        pr = None
        for r in range(cur, len(M)):
            if M[r][col] % p != 0:
                pr = r
                break
        if pr is None:
            continue
        M[cur], M[pr] = M[pr], M[cur]
        from fri_2round_attack import modinv
        inv = modinv(M[cur][col], p)
        M[cur] = [(x * inv) % p for x in M[cur]]
        for r in range(len(M)):
            if r != cur and M[r][col] != 0:
                ff = M[r][col]
                M[r] = [(M[r][c] - ff * M[cur][c]) % p for c in range(n_cols)]
        pivot_rows.append(M[cur])
        pivot_cols.append(col)
        cur += 1
    return pivot_rows, len(pivot_rows)


def dmin_W(G_W, n_cols, p, max_w_to_check=5):
    """Exact d_min(W) by enumerating supports T of size w = 1, 2, ..., max_w_to_check.
    Returns smallest w such that G_W|_{T^c} has rank < dim(W) for some T of size w.
    If no such w found within max_w_to_check, returns max_w_to_check + 1 (likely > Singleton)."""
    full_rank = len(G_W)  # should be dim(W) since G_W is already reduced
    for w in range(1, max_w_to_check + 1):
        for T in combinations(range(n_cols), w):
            T_c = [j for j in range(n_cols) if j not in T]
            G_proj = [[row[j] for j in T_c] for row in G_W]
            if gauss_rank_local(G_proj, p) < full_rank:
                return w
    return max_w_to_check + 1


def process_one_f(args):
    """Worker. Returns dict with positions, status, dim_W, d_min_W."""
    positions, coefs, seed = args
    chain = setup_chain(P, N0, K0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, P)

    fhat = [0] * N0
    for pos, c in zip(positions, coefs):
        fhat[pos] = c
    f = evaluate_dft(fhat, L0, P)

    above_J, max_extras, _ = is_above_johnson_sampling(
        f, L0, K0, P, W_J, n_samples=50000, batch=4096, seed=seed,
        return_evidence=True,
    )
    if not above_J:
        return {'positions': positions, 'status': 'BELOW_J',
                'dim_W': None, 'd_min_W': None, 'rank': None}

    # Compute rank from corner syndromes
    corner_syns = compute_corner_syndromes(f, chain, R, P, H_R)
    nonzero_syns = [s for s in corner_syns.values() if any(x != 0 for x in s)]
    if not nonzero_syns:
        return {'positions': positions, 'status': 'ABOVE_J_RANK_0',
                'dim_W': None, 'd_min_W': None, 'rank': 0}
    rank = gauss_rank_local(nonzero_syns, P)
    if rank != 2:
        return {'positions': positions, 'status': f'ABOVE_J_RANK_{rank}',
                'dim_W': None, 'd_min_W': None, 'rank': rank}

    # Build G_W and compute d_min
    G_W, dim_W = build_G_W(f, chain, R, P, k_R, N_R, L_R)
    d_min = dmin_W(G_W, N_R, P, max_w_to_check=5)
    return {'positions': positions, 'coefs': coefs,
            'status': 'ABOVE_J_RANK_2',
            'dim_W': dim_W, 'd_min_W': d_min, 'rank': rank}


def build_candidate_specs(n_random, seed):
    rng = random.Random(seed)
    specs = []
    for a, b in combinations(range(K0, N0), 2):
        specs.append(((a, b), (1, 1), rng.randrange(2**31)))
    triples = list(combinations(range(K0, N0), 3))
    rng.shuffle(triples)
    for t in triples[:min(len(triples), max(0, n_random // 2))]:
        specs.append((t, tuple(rng.randrange(1, P) for _ in range(3)), rng.randrange(2**31)))
    n_left = max(0, n_random - len(specs) + len(list(combinations(range(K0, N0), 2))))
    for _ in range(n_left):
        sparsity = rng.choice([2, 3, 4, 5])
        pos = tuple(sorted(rng.sample(range(K0, N0), sparsity)))
        cs = tuple(rng.randrange(1, P) for _ in range(sparsity))
        specs.append((pos, cs, rng.randrange(2**31)))
    return specs


def main():
    n_random = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    n_workers = int(sys.argv[2]) if len(sys.argv) > 2 else max(1, cpu_count() - 1)
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 2026

    print(f"# probe_dmin_W_rank2.py — exact d_min(W) for rank-2 above-J f")
    print(f"# Setup: p={P}, n_0={N0}, k_0={K0}, R={R}, w_R=3")
    print(f"# n_R={N_R}, k_R+r={2+2}=4, MDS bound d_min(W) ≤ 5")
    print(f"# n_workers={n_workers}, n_random={n_random}, seed={seed}")
    print()

    specs = build_candidate_specs(n_random, seed)
    print(f"# Generated {len(specs)} candidate f-specs.")
    print()

    t0 = time.time()
    results = []
    counts = {}
    rank2_results = []
    n_done = 0
    with Pool(n_workers) as pool:
        for r in pool.imap_unordered(process_one_f, specs, chunksize=4):
            n_done += 1
            results.append(r)
            counts[r['status']] = counts.get(r['status'], 0) + 1
            if r['status'] == 'ABOVE_J_RANK_2':
                rank2_results.append(r)
            if n_done % 50 == 0:
                rate = n_done / (time.time() - t0)
                print(f"#  {n_done}/{len(specs)}  rate {rate:.1f}/sec  "
                      f"counts: {dict(counts)}", flush=True)
    elapsed = time.time() - t0

    print()
    print(f"# === DONE in {elapsed:.0f}s ===")
    for k, v in counts.items():
        print(f"#   {k}: {v}")
    print()

    if not rank2_results:
        print("# No rank-2 above-J f found.")
        return

    # Histogram d_min(W)
    print(f"# === Rank-2 above-J: {len(rank2_results)} cases ===")
    dmin_dist = {}
    for r in rank2_results:
        d = r['d_min_W']
        dmin_dist[d] = dmin_dist.get(d, 0) + 1
    print(f"# d_min(W) distribution: {dict(sorted(dmin_dist.items()))}")
    print()

    # Headline: any d_min ≤ 3? (would falsify Lemma A)
    if any(d <= 3 for d in dmin_dist):
        bad = [r for r in rank2_results if r['d_min_W'] <= 3]
        print(f"# ★★★ FALSIFIES Lemma A: {len(bad)} cases with d_min(W) ≤ 3 ★★★")
        for r in bad[:20]:
            print(f"#   positions={r['positions']}, coefs={r['coefs']}, d_min={r['d_min_W']}")
    else:
        print(f"# ✓ Lemma A holds for all {len(rank2_results)} cases: d_min(W) > 3")

    # Detail: how many are MDS (d_min = 5) vs not (d_min = 4)?
    mds_count = dmin_dist.get(5, 0)
    near_mds = dmin_dist.get(4, 0)
    if mds_count == len(rank2_results):
        print(f"# ★ STRONG STRUCTURE: ALL rank-2 above-J f give W as MDS (d_min = 5)!")
    elif near_mds + mds_count == len(rank2_results):
        print(f"# Mix: {mds_count} MDS (d_min=5), {near_mds} near-MDS (d_min=4)")
        # Print a few d_min=4 cases for inspection
        d4 = [r for r in rank2_results if r['d_min_W'] == 4]
        if d4:
            print(f"# === Sample d_min=4 cases ({min(10, len(d4))}/{len(d4)}) ===")
            for r in d4[:10]:
                print(f"#   positions={r['positions']}, coefs={r['coefs']}")


if __name__ == '__main__':
    main()
