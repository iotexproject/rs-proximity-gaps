"""g3_count_by_support_q97.py — Conjecture E test at q=97 with multiprocessing.

Test: count_α depends ONLY on DFT support of f, not coefficients.
Use 4 workers (leave 8 for user). Q=97 makes per-candidate scan fast.

For each 3-position DFT support in syndrome window {8..31}, run 3 random
coefficient trials and verify count_α is invariant across trials.
"""
import sys, os, random, time, math
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


_state = {}


def worker_init(p, n0, k0):
    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    n1 = len(L1); k1 = k0 // 2
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets_n1 = list(combinations(range(n1), k1))
    info_sets_arr_n1 = np.array(info_sets_n1, dtype=np.int64)
    # n0 has C(32,8)=10.5M info sets — too large to materialize.
    # We use sampled above-J detection: random N samples gives FPR ≈ exp(-N·...)
    rng_local = np.random.default_rng(42)
    n_samples = 5000
    all_T = list(combinations(range(n0), k0))
    sampled_idx = rng_local.choice(len(all_T), size=n_samples, replace=False)
    info_sets_arr_n0_sampled = np.array([all_T[i] for i in sampled_idx], dtype=np.int64)
    _state.update({
        'p': p, 'n0': n0, 'k0': k0, 'n1': n1, 'k1': k1,
        'L0': L0, 'L0_arr': L0_arr, 'L1_arr': L1_arr,
        'D0': D0, 'inv_D0': inv_D0, 'D1': D1, 'inv_D1': inv_D1,
        'info_sets_n1': info_sets_arr_n1,
        'info_sets_n0': info_sets_arr_n0_sampled,
        'w_J': 16, 'threshold_d1': 8,
    })


def worker_check(arg):
    """Check one (positions, coeffs) candidate. Return (positions, above_J, count)."""
    positions, coeffs = arg
    p = _state['p']; n0 = _state['n0']; k0 = _state['k0']
    n1 = _state['n1']; k1 = _state['k1']
    L0 = _state['L0']; L0_arr = _state['L0_arr']; L1_arr = _state['L1_arr']
    D0 = _state['D0']; inv_D0 = _state['inv_D0']
    D1 = _state['D1']; inv_D1 = _state['inv_D1']
    info_sets_n1 = _state['info_sets_n1']
    info_sets_n0 = _state['info_sets_n0']
    w_J = _state['w_J']; threshold = _state['threshold_d1']

    fhat = [0] * n0
    for ps, c in zip(positions, coeffs):
        fhat[ps] = c
    f = evaluate_dft_local(fhat, L0, p)
    f_arr = np.array(f, dtype=np.int64)
    extras_n0 = batched_extras(info_sets_n0, f_arr, L0_arr, D0, inv_D0, p)
    max_extras = int(extras_n0.max())
    d_f = n0 - k0 - max_extras
    above_J = d_f > w_J
    if not above_J:
        return (positions, False, None)
    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)
    cnt = 0
    for a in range(p):
        fold = (f_e_arr + a * f_o_arr) % p
        extras = batched_extras(info_sets_n1, fold, L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras.max())
        if d1 <= threshold:
            cnt += 1
    return (positions, True, cnt)


def main():
    p = 97
    n0, k0 = 32, 8
    n_workers = 4
    n_trials = 3

    # Generate all 3-position DFT supports in syndrome window with even+odd
    supports = []
    for ps in combinations(range(8, 32), 3):
        has_e = any(j % 2 == 0 for j in ps)
        has_o = any(j % 2 == 1 for j in ps)
        if has_e and has_o:
            supports.append(ps)
    print(f"Total 3-pos supports: {len(supports)}")

    # Build candidate list with random coefficients
    rng = random.Random(2026)
    candidates = []
    for ps in supports:
        for tr in range(n_trials):
            coeffs = tuple(rng.randint(1, p-1) for _ in ps)
            candidates.append((ps, coeffs))
    print(f"Candidates (each support × {n_trials} trials): {len(candidates)}")

    # Run in parallel
    t0 = time.time()
    results_per_support = defaultdict(list)
    n_above_J = 0
    with Pool(processes=n_workers, initializer=worker_init, initargs=(p, n0, k0)) as pool:
        for i, (ps, above, cnt) in enumerate(pool.imap_unordered(worker_check, candidates, chunksize=8)):
            if above:
                results_per_support[ps].append(cnt)
                n_above_J += 1
            if (i+1) % 500 == 0:
                elapsed = time.time() - t0
                print(f"  [{i+1}/{len(candidates)}] above-J: {n_above_J}, elapsed {elapsed:.0f}s", flush=True)

    elapsed = time.time() - t0
    print(f"\n=== Done in {elapsed:.0f}s ===")

    # For each support, check if all trials have same count
    invariant_count = {}
    variant_count = {}
    for ps, cnts in results_per_support.items():
        if len(cnts) >= 2:  # Need at least 2 trials
            uniq = set(cnts)
            if len(uniq) == 1:
                invariant_count[ps] = next(iter(uniq))
            else:
                variant_count[ps] = cnts

    print(f"Total supports with ≥2 above-J trials: {len(invariant_count) + len(variant_count)}")
    print(f"  Class-invariant count: {len(invariant_count)}")
    print(f"  Coefficient-dependent count: {len(variant_count)}")

    if variant_count:
        print(f"\n!!! Conjecture E REFUTED at these supports !!!")
        for ps, cnts in list(variant_count.items())[:10]:
            print(f"  pos={ps}: counts={cnts}")
    else:
        print(f"\n✓ Conjecture E holds (all {len(invariant_count)} supports invariant)")

    # Histogram
    cnt_dist = Counter(invariant_count.values())
    print(f"\nCount-value distribution (across {len(invariant_count)} invariant supports):")
    for c in sorted(cnt_dist):
        print(f"  count={c}: {cnt_dist[c]} supports")

    # Examples per count
    print(f"\nExamples per count:")
    for c in sorted(cnt_dist):
        examples = [ps for ps, v in invariant_count.items() if v == c][:5]
        print(f"  count={c}: {examples}")

    # Specifically check case (b) ⊂ {16..23}
    caseB_supports = [ps for ps in supports if all(16 <= j <= 23 for j in ps)]
    caseB_invariant = {ps: invariant_count[ps] for ps in caseB_supports if ps in invariant_count}
    print(f"\nCase (b) supports ⊂ {{16..23}}: {len(caseB_supports)}, invariant: {len(caseB_invariant)}")
    if caseB_invariant:
        print(f"  Counts: {Counter(caseB_invariant.values())}")
        print(f"  All count={p}? {all(v == p for v in caseB_invariant.values())}")


if __name__ == "__main__":
    main()
