"""g3_sweep_64_16.py — sweep at (n_0, k_0) = (64, 16) with bug-fixed code.

Test if same structural patterns hold at larger n_0:
- Conjecture E (count is DFT-support invariant)
- count distribution gaps
- Max count saturating n_1 - s + 1 = 32 - 16 + 1 = 17?
- σ_k invariants for biquadratic structure (a, a+m, a+32) at (64, 16).

Need: q with 64 | q-1. q=1153 (1152 = 18·64) ✓.

dist(f, RS_16 on L_0) requires C(64, 16) ≈ 4.9e14 info sets — must sample.
batched_extras at k=16 needs to be fast; use sampled above-J detection.
"""
import sys, os, random, time, math
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter
import multiprocessing as mp
mp.set_start_method('fork', force=True)
from multiprocessing import Pool

from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft_local(fhat, L, p):
    n = len(L)
    f = [0] * n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j] != 0:
                v = (v + fhat[j] * pow(x, j, p)) % p
        f[i] = v
    return f


_state = {}


def worker_init(p, n0, k0, n_samples_n0, n_samples_n1):
    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    n1 = len(L1); k1 = k0 // 2
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    rng_local = np.random.default_rng(42)
    # Sampled info sets at L_0 (C(64, 16) too large)
    all_T_n0 = list(combinations(range(n0), k0))
    if len(all_T_n0) > n_samples_n0:
        idx0 = rng_local.choice(len(all_T_n0), size=n_samples_n0, replace=False)
        info_n0 = np.array([all_T_n0[i] for i in idx0], dtype=np.int64)
    else:
        info_n0 = np.array(all_T_n0, dtype=np.int64)
    # Sampled info sets at L_1 (C(32, 8) = 10.5M too large)
    all_T_n1 = list(combinations(range(n1), k1))
    if len(all_T_n1) > n_samples_n1:
        idx1 = rng_local.choice(len(all_T_n1), size=n_samples_n1, replace=False)
        info_n1 = np.array([all_T_n1[i] for i in idx1], dtype=np.int64)
    else:
        info_n1 = np.array(all_T_n1, dtype=np.int64)
    _state.update({
        'p': p, 'n0': n0, 'k0': k0, 'n1': n1, 'k1': k1,
        'L0': L0, 'L0_arr': L0_arr, 'L1_arr': L1_arr,
        'D0': D0, 'inv_D0': inv_D0, 'D1': D1, 'inv_D1': inv_D1,
        'info_n0': info_n0, 'info_n1': info_n1,
        'w_J': n0 - int(math.isqrt(k0 * n0)),
        'threshold_d1': n1 - int(math.isqrt(k1 * n1)),
    })


def worker_check(positions_coeffs):
    positions, coeffs = positions_coeffs
    p = _state['p']; n0 = _state['n0']; k0 = _state['k0']
    n1 = _state['n1']; k1 = _state['k1']
    L0 = _state['L0']; L0_arr = _state['L0_arr']; L1_arr = _state['L1_arr']
    D0 = _state['D0']; inv_D0 = _state['inv_D0']
    D1 = _state['D1']; inv_D1 = _state['inv_D1']
    info_n0 = _state['info_n0']; info_n1 = _state['info_n1']
    w_J = _state['w_J']; threshold = _state['threshold_d1']

    fhat = [0] * n0
    for ps, c in zip(positions, coeffs):
        fhat[ps] = c
    f = evaluate_dft_local(fhat, L0, p)
    f_arr = np.array(f, dtype=np.int64)
    extras_n0 = batched_extras(info_n0, f_arr, L0_arr, D0, inv_D0, p)
    max_extras = int(extras_n0.max())
    d_f = n0 - k0 - max_extras
    if d_f <= w_J:
        return (positions, False, d_f, None)

    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)
    cnt = 0
    bad = []
    for a in range(p):
        fold = (f_e_arr + a * f_o_arr) % p
        extras = batched_extras(info_n1, fold, L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras.max())
        if d1 <= threshold:
            cnt += 1
            bad.append(a)
    return (positions, True, d_f, cnt, bad[:20])


def generate_candidates(p, n0, k0, n_candidates, seed):
    rng = random.Random(seed)
    out = []
    while len(out) < n_candidates:
        n_pos = rng.choice([3, 4, 5])
        positions = sorted(rng.sample(range(k0, n0), n_pos))
        has_even = any(j % 2 == 0 for j in positions)
        has_odd = any(j % 2 == 1 for j in positions)
        if not (has_even and has_odd):
            continue
        coeffs = [rng.randrange(1, p) for _ in positions]
        out.append((tuple(positions), tuple(coeffs)))
    return out


def main():
    p = 1153
    n0, k0 = 64, 16
    n_candidates = 100  # smaller than (32,8) since slower
    n_workers = 20
    n_samples_n0 = 50000  # of C(64,16)≈5e14
    n_samples_n1 = 50000  # of C(32,8)≈10.5M (sampling 50000 is good fraction)
    seed = 2026 + p

    print(f"=== Sweep at q={p}, (n_0,k_0)=({n0},{k0}), {n_candidates} cands, {n_workers} workers ===")
    print(f"Sampling: {n_samples_n0} info sets at L_0, {n_samples_n1} at L_1")
    print(f"w_J(L_0) = {n0 - int(math.isqrt(k0*n0))}")
    print(f"threshold d1 ≤ {n0//2 - int(math.isqrt((k0//2)*(n0//2)))}")

    candidates = generate_candidates(p, n0, k0, n_candidates, seed)
    t0 = time.time()
    above_J_results = []
    n_below = 0
    max_count = -1
    with Pool(processes=n_workers, initializer=worker_init, initargs=(p, n0, k0, n_samples_n0, n_samples_n1)) as pool:
        for i, res in enumerate(pool.imap_unordered(worker_check, candidates, chunksize=2)):
            if res[1]:  # above-J
                _, _, d_f, cnt, bad = res
                above_J_results.append((res[0], d_f, cnt, bad))
                if cnt > max_count:
                    max_count = cnt
                    print(f"  [{i+1}/{len(candidates)}] above-J dist={d_f} count={cnt} pos={res[0]} bad={bad[:10]}", flush=True)
            else:
                n_below += 1
            if (i+1) % 20 == 0:
                elapsed = time.time() - t0
                print(f"    progress {i+1}/{len(candidates)} | strict above-J: {len(above_J_results)} | elapsed {elapsed:.0f}s", flush=True)

    elapsed = time.time() - t0
    print(f"\n=== Done in {elapsed:.0f}s ===")
    print(f"Strict above-J: {len(above_J_results)} | not above-J: {n_below}")
    print(f"Max count: {max_count}")
    cnt_dist = Counter(r[2] for r in above_J_results)
    print(f"Count distribution: {dict(sorted(cnt_dist.items()))}")


if __name__ == "__main__":
    main()
