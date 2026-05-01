"""g3_enumerate_3pos_q1153.py — enumerate ALL 3-position DFT supports at q=1153.

For each 3-position support in syndrome window {8..31} (with at least 1 even and
1 odd), pick a random coefficient triple, compute count_α.

Goal: characterize the (DFT support → count_α) function, identify which supports
give high counts (>2), see structural patterns.

Test at q=1153 with bug-fixed batched_extras. Use 20 workers.
"""
import sys, os, random, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter, defaultdict
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


def exhaustive_above_J(f_arr, L0_arr, n0, k0, w_J, D0, inv_D0, p, batch_size=300000):
    threshold = n0 - k0 - w_J
    max_extras = 0
    all_T = list(combinations(range(n0), k0))
    for start in range(0, len(all_T), batch_size):
        batch = all_T[start:start + batch_size]
        T_arr = np.array(batch, dtype=np.int64)
        extras = batched_extras(T_arr, f_arr, L0_arr, D0, inv_D0, p)
        m = int(extras.max())
        if m > max_extras:
            max_extras = m
        if max_extras >= threshold:
            return False, n0 - k0 - max_extras
    return max_extras < threshold, n0 - k0 - max_extras


_state = {}


def worker_init(p, n0, k0, seed):
    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    n1 = len(L1); k1 = k0 // 2
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets = list(combinations(range(n1), k1))
    info_sets_arr_n1 = np.array(info_sets, dtype=np.int64)
    _state.update({
        'p': p, 'n0': n0, 'k0': k0, 'n1': n1, 'k1': k1,
        'L0': L0, 'L0_arr': L0_arr, 'L1_arr': L1_arr,
        'D0': D0, 'inv_D0': inv_D0, 'D1': D1, 'inv_D1': inv_D1,
        'info_sets_arr_n1': info_sets_arr_n1,
        'rng': random.Random(seed),
        'w_J': 16, 'threshold_d1': 8,
    })


def worker_check(positions):
    """For one DFT support, pick random coefficients, return (positions, above_J, count)."""
    p = _state['p']; n0 = _state['n0']; k0 = _state['k0']
    n1 = _state['n1']; k1 = _state['k1']
    L0 = _state['L0']; L0_arr = _state['L0_arr']; L1_arr = _state['L1_arr']
    D0 = _state['D0']; inv_D0 = _state['inv_D0']
    D1 = _state['D1']; inv_D1 = _state['inv_D1']
    info_sets = _state['info_sets_arr_n1']
    w_J = _state['w_J']; threshold = _state['threshold_d1']

    # Use deterministic per-position seed
    rng_pos = random.Random(hash(positions))
    coeffs = tuple(rng_pos.randint(1, p-1) for _ in positions)
    fhat = [0] * n0
    for ps, c in zip(positions, coeffs):
        fhat[ps] = c
    f = evaluate_dft_local(fhat, L0, p)
    f_arr = np.array(f, dtype=np.int64)

    above_J, d_f = exhaustive_above_J(f_arr, L0_arr, n0, k0, w_J, D0, inv_D0, p)
    if not above_J:
        return (positions, False, d_f, None)

    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)
    cnt = 0
    for a in range(p):
        fold = (f_e_arr + a * f_o_arr) % p
        extras = batched_extras(info_sets, fold, L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras.max())
        if d1 <= threshold:
            cnt += 1
    return (positions, True, d_f, cnt)


def main():
    p = 1153
    n0, k0 = 32, 8
    n_workers = 20

    # Enumerate ALL 3-position DFT supports in syndrome window {8..31}
    supports = []
    for ps in combinations(range(8, 32), 3):
        has_e = any(j % 2 == 0 for j in ps)
        has_o = any(j % 2 == 1 for j in ps)
        if has_e and has_o:
            supports.append(ps)
    print(f"Total 3-pos supports: {len(supports)}, q={p}, workers={n_workers}")

    t0 = time.time()
    results = {}
    with Pool(processes=n_workers, initializer=worker_init, initargs=(p, n0, k0, 0)) as pool:
        for i, (pos, above, df, cnt) in enumerate(pool.imap_unordered(worker_check, supports, chunksize=4)):
            results[pos] = (above, df, cnt)
            if (i+1) % 100 == 0:
                elapsed = time.time() - t0
                print(f"  [{i+1}/{len(supports)}] elapsed {elapsed:.0f}s", flush=True)

    elapsed = time.time() - t0
    print(f"\n=== Done in {elapsed:.0f}s ===")

    above_J = {pos: cnt for pos, (above, df, cnt) in results.items() if above}
    print(f"Above-J supports: {len(above_J)} / {len(supports)}")

    cnt_dist = Counter(above_J.values())
    print(f"Count distribution:")
    for c in sorted(cnt_dist):
        print(f"  count={c}: {cnt_dist[c]} supports")

    # Highlight supports with count ≥ 3
    print(f"\nSupports with count ≥ 3:")
    for pos, cnt in sorted(above_J.items()):
        if cnt and cnt >= 3:
            print(f"  pos={pos}: count={cnt}")


if __name__ == "__main__":
    main()
