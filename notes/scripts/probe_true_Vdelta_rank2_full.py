"""probe_true_Vdelta_rank2_full.py — true |V_δ| for ALL rank-2 above-J f at n_0=32.

After Lemma A (d_min(W) > w_R) was falsified by 6 cases yet bound R q^(R-1) = 194
still held, we need a comprehensive empirical: does ANY rank-2 above-J f exceed
|V_δ| = 194? Empirically tight at 193 in falsifiers, so any breach would be very
informative.

Per-f cost: q^R = 9409 alpha enumerations × min_wt_via_MDS check (max_w=3).
With multiprocessing this is feasible at scale.

Output: histogram of |V_δ| across all rank-2 above-J cases + flag any > 194.
"""
from __future__ import annotations
import sys, os, time, random
from itertools import product, combinations
from multiprocessing import Pool, cpu_count

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, parity_check, gauss_rank, matvec
from mds_decoder import is_above_johnson_sampling
from probe_step5_n32_studio import (
    P, N0, K0, R, N_R, W_J,
    evaluate_dft, fold_at_alpha, compute_corner_syndromes, min_wt_via_MDS,
)


def process_one_f(args):
    positions, coefs, seed = args
    chain = setup_chain(P, N0, K0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, P)
    W_R = 3

    fhat = [0] * N0
    for pos, c in zip(positions, coefs):
        fhat[pos] = c
    f = evaluate_dft(fhat, L0, P)

    above_J, max_e, _ = is_above_johnson_sampling(
        f, L0, K0, P, W_J, n_samples=50000, batch=4096, seed=seed,
        return_evidence=True,
    )
    if not above_J:
        return {'positions': positions, 'status': 'BELOW_J', 'rank': None, 'v_delta': None}

    corner_syns = compute_corner_syndromes(f, chain, R, P, H_R)
    nz = [s for s in corner_syns.values() if any(x != 0 for x in s)]
    rank = gauss_rank([list(s) for s in nz], P) if nz else 0
    if rank != 2:
        return {'positions': positions, 'status': f'ABOVE_J_RANK_{rank}', 'rank': rank, 'v_delta': None}

    # Brute-force |V_δ|
    v_delta = 0
    for alphas in product(range(P), repeat=R):
        g = fold_at_alpha(f, chain, list(alphas), P)
        syn = matvec(H_R, g, P)
        if all(x == 0 for x in syn):
            v_delta += 1
            continue
        w_min, _T, _e = min_wt_via_MDS(syn, H_R, N_R, P, max_w=W_R)
        if w_min is not None:
            v_delta += 1
    return {'positions': positions, 'coefs': coefs, 'status': 'ABOVE_J_RANK_2',
            'rank': 2, 'v_delta': v_delta}


def build_specs(n_random, seed):
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
    target_bound = R * P  # 194

    print(f"# probe_true_Vdelta_rank2_full")
    print(f"# Setup: p={P}, n_0={N0}, R={R}, w_R=3, target |V_δ| ≤ {target_bound}")
    print(f"# n_workers={n_workers}, n_random={n_random}, seed={seed}")
    print()

    specs = build_specs(n_random, seed)
    print(f"# Generated {len(specs)} specs.")
    print()

    t0 = time.time()
    rank2 = []
    counts = {}
    n_done = 0
    with Pool(n_workers) as pool:
        for r in pool.imap_unordered(process_one_f, specs, chunksize=2):
            n_done += 1
            counts[r['status']] = counts.get(r['status'], 0) + 1
            if r['status'] == 'ABOVE_J_RANK_2':
                rank2.append(r)
                if r['v_delta'] > target_bound:
                    print(f"# ★★★ EXCEEDS BOUND ★★★ positions={r['positions']}, coefs={r['coefs']}, |V_δ|={r['v_delta']}", flush=True)
            if n_done % 50 == 0:
                rate = n_done / (time.time() - t0)
                print(f"#  {n_done}/{len(specs)}  rate {rate:.2f}/sec  {dict(counts)}", flush=True)

    elapsed = time.time() - t0
    print()
    print(f"# === DONE in {elapsed:.0f}s ===")
    for k, v in counts.items():
        print(f"#   {k}: {v}")
    print()

    if not rank2:
        print("# No rank-2 above-J f.")
        return

    # Histogram
    print(f"# === Rank-2 above-J: {len(rank2)} cases ===")
    vd_list = [r['v_delta'] for r in rank2]
    max_vd = max(vd_list)
    breaches = [r for r in rank2 if r['v_delta'] > target_bound]
    print(f"#   max |V_δ| = {max_vd}, target = {target_bound}, breaches = {len(breaches)}")
    print(f"#   |V_δ| histogram:")
    hist = {}
    for v in vd_list:
        hist[v] = hist.get(v, 0) + 1
    for v in sorted(hist):
        marker = " ← EXCEEDS" if v > target_bound else ""
        print(f"#     {v:>5d}: {hist[v]:>4d}{marker}")

    if breaches:
        print()
        print(f"# ★★★ {len(breaches)} BREACHES OF DIRECTION A BOUND ★★★")
        for r in breaches[:30]:
            print(f"#   positions={r['positions']}, coefs={r['coefs']}, |V_δ|={r['v_delta']}")
    else:
        print()
        print(f"# ✓ Direction A bound holds for all {len(rank2)} rank-2 above-J cases.")
        print(f"#   max |V_δ| = {max_vd}/{target_bound} = {max_vd/target_bound:.3f}")


if __name__ == '__main__':
    main()
