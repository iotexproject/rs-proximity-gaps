"""probe_G_alpha_universal.py — does every rank-r above-J f admit a degree-≤R polynomial G_f vanishing on V_δ?

For r ∈ {1, 2}: brute-force enumerate V_δ ⊂ F_q^R (R=2). For r=2 with |V_δ|≤2q this should
have at least one nonzero deg-≤2 G. For r=1 even smaller.

For r=3 with R=2 we'd expect |V_δ| could be larger; we test whether deg-≤2 G still exists
(probably not always; deg-≤3 might be needed).

Output: per (positions, coefs, rank) report
  - |V_δ|
  - dim(deg-≤R vanishing G_f)
  - confirms V_δ ⊆ Z(G).

Goal: empirically confirm "rank-r above-J f admits deg-≤R polynomial vanishing on V_δ" universally.
"""
from __future__ import annotations
import sys, os, time, random
from itertools import product, combinations
from multiprocessing import Pool, cpu_count
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, parity_check, gauss_rank, matvec, modinv
from mds_decoder import is_above_johnson_sampling
from probe_step5_n32_studio import (
    P, N0, K0, R, N_R, W_J,
    evaluate_dft, fold_at_alpha, compute_corner_syndromes, min_wt_via_MDS,
)


def gauss_kernel(rows, n_cols, p):
    A = [list(r) for r in rows]
    n_rows = len(A)
    pivot_row_of_col = [-1] * n_cols
    cur_row = 0
    for col in range(n_cols):
        if cur_row >= n_rows:
            break
        pr = None
        for r in range(cur_row, n_rows):
            if A[r][col] % p != 0:
                pr = r
                break
        if pr is None:
            continue
        A[cur_row], A[pr] = A[pr], A[cur_row]
        inv = modinv(A[cur_row][col], p)
        A[cur_row] = [(x * inv) % p for x in A[cur_row]]
        for rr in range(n_rows):
            if rr != cur_row and A[rr][col] % p != 0:
                ff = A[rr][col]
                A[rr] = [(A[rr][c] - ff * A[cur_row][c]) % p for c in range(n_cols)]
        pivot_row_of_col[col] = cur_row
        cur_row += 1
    free_cols = [c for c in range(n_cols) if pivot_row_of_col[c] == -1]
    basis = []
    for fc in free_cols:
        v = [0] * n_cols
        v[fc] = 1
        for c in range(n_cols):
            if pivot_row_of_col[c] != -1:
                v[c] = (-A[pivot_row_of_col[c]][fc]) % p
        basis.append(v)
    return basis


def monomial_exps(deg, n_vars):
    """All exponent tuples (e_1, ..., e_n_vars) with sum ≤ deg."""
    out = []
    for total_d in range(deg + 1):
        # all compositions of total_d into n_vars parts
        for tup in product(range(total_d + 1), repeat=n_vars):
            if sum(tup) == total_d:
                out.append(tup)
    return out


def eval_monomial_basis(point, exps, p):
    out = []
    for tup in exps:
        v = 1
        for x, e in zip(point, tup):
            for _ in range(e):
                v = (v * x) % p
        out.append(v)
    return out


def compute_V_delta(f, chain, R_local, p, H_R, n_R, w_R):
    V = []
    for alphas in product(range(p), repeat=R_local):
        g = fold_at_alpha(f, chain, list(alphas), p)
        syn = matvec(H_R, g, p)
        if all(x == 0 for x in syn):
            V.append(alphas)
            continue
        w_min, _T, _e = min_wt_via_MDS(syn, H_R, n_R, p, max_w=w_R)
        if w_min is not None:
            V.append(alphas)
    return V


def process_one(args):
    positions, coefs, seed = args
    chain = setup_chain(P, N0, K0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, P)
    w_R = 3

    fhat = [0] * N0
    for pos, c in zip(positions, coefs):
        fhat[pos] = c
    f = evaluate_dft(fhat, L0, P)

    above, _, _ = is_above_johnson_sampling(
        f, L0, K0, P, W_J, n_samples=30000, batch=4096, seed=seed,
        return_evidence=True,
    )
    if not above:
        return {'positions': positions, 'status': 'BELOW_J'}

    corner_syns = compute_corner_syndromes(f, chain, R, P, H_R)
    nz = [s for s in corner_syns.values() if any(x != 0 for x in s)]
    rk = gauss_rank([list(s) for s in nz], P) if nz else 0

    V = compute_V_delta(f, chain, R, P, H_R, N_R, w_R)
    V_size = len(V)

    # Fit deg-≤R G_f
    exps = monomial_exps(R, R)  # R variables, deg ≤ R
    rows = [eval_monomial_basis(point, exps, P) for point in V]
    n_cols = len(exps)
    basis = gauss_kernel(rows, n_cols, P)

    # Sanity: pick first basis vec, check Z ⊇ V
    if basis:
        G = basis[0]
        ok = all(sum(c * m for c, m in zip(G, eval_monomial_basis(point, exps, P))) % P == 0 for point in V)
    else:
        ok = (V_size == 0)

    return {
        'positions': positions,
        'coefs': coefs,
        'status': 'OK',
        'rank': rk,
        'v_delta': V_size,
        'deg_R_kernel_dim': len(basis),
        'V_in_ZG': ok,
    }


def build_specs(n_random, seed):
    rng = random.Random(seed)
    specs = []
    # Mix of sparsities; the rank distribution will fall out naturally
    for _ in range(n_random):
        sparsity = rng.choice([2, 3, 4, 5])
        positions = tuple(sorted(rng.sample(range(K0, N0), sparsity)))
        coefs = tuple(rng.randrange(1, P) for _ in range(sparsity))
        specs.append((positions, coefs, rng.randrange(2**31)))
    return specs


def main():
    n_random = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    n_workers = int(sys.argv[2]) if len(sys.argv) > 2 else max(1, cpu_count() - 1)
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 4242
    target_bound = R * P

    print(f"# probe_G_alpha_universal")
    print(f"# Setup: p={P}, n_0={N0}, R={R}, w_R=3, target |V_δ| ≤ {target_bound}")
    print(f"# n_workers={n_workers}, n_random={n_random}, seed={seed}")
    print()

    specs = build_specs(n_random, seed)
    print(f"# Generated {len(specs)} specs.")
    print()

    t0 = time.time()
    results = []
    fails = []
    n_done = 0
    rank_counts = {}
    with Pool(n_workers) as pool:
        for r in pool.imap_unordered(process_one, specs, chunksize=2):
            n_done += 1
            if r['status'] == 'BELOW_J':
                continue
            results.append(r)
            rk = r['rank']
            rank_counts[rk] = rank_counts.get(rk, 0) + 1
            if r['deg_R_kernel_dim'] == 0 and r['v_delta'] > 0:
                fails.append(r)
                print(f"# ★★★ FAIL ★★★ positions={r['positions']}, rank={rk}, |V_δ|={r['v_delta']}", flush=True)
            if not r['V_in_ZG']:
                fails.append(r)
                print(f"# ★★★ Z⊉V ★★★ positions={r['positions']}, rank={rk}", flush=True)
            if n_done % 50 == 0:
                print(f"#  {n_done}/{len(specs)}  ranks {dict(rank_counts)}  fails={len(fails)}", flush=True)

    elapsed = time.time() - t0
    print()
    print(f"# === DONE in {elapsed:.0f}s ===")
    print(f"# Total above-J: {len(results)}")
    print(f"# Rank distribution: {dict(rank_counts)}")
    print(f"# G_f failures: {len(fails)}")
    print()

    # Per-rank summary
    for rk in sorted(rank_counts):
        sub = [r for r in results if r['rank'] == rk]
        if not sub:
            continue
        max_vd = max(r['v_delta'] for r in sub)
        zero_vd = sum(1 for r in sub if r['v_delta'] == 0)
        always_kernel_pos = all(r['deg_R_kernel_dim'] >= 1 or r['v_delta'] == 0 for r in sub)
        print(f"# Rank {rk}: {len(sub)} cases, max |V_δ| = {max_vd}, |V_δ|=0 cases = {zero_vd}")
        print(f"#   ker(G_f) ≥ 1 always: {always_kernel_pos}")
        # Histogram
        vd_hist = {}
        for r in sub:
            vd_hist[r['v_delta']] = vd_hist.get(r['v_delta'], 0) + 1
        print(f"#   |V_δ| histogram (top 10): {dict(sorted(vd_hist.items())[:10])}")

    if fails:
        print()
        print(f"# ★ {len(fails)} FAILURES — G_f does not exist for these ★")
        for f in fails[:30]:
            print(f"#   {f}")


if __name__ == '__main__':
    main()
