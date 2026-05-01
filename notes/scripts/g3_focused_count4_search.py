"""g3_focused_count4_search.py — try to construct strict above-J f with bad-α count = 4.

Conjecture D predicts |B(f)| | (q-1). At q=97, divisors of 96 ≤ 9 are
{1,2,3,4,6,8}. We've seen counts 1, 2, 8. We want to find count = 4 or 6
to verify D's prediction structure.

Strategy: pick f with DFT support that, after folding, gives a polynomial
with cyclotomic action of order 4 (gives count=4 orbit) or 6 (count=6 orbit).

For count=4, the cyclotomic action should be by μ_4 ⊂ μ_8 ⊂ F_97*.
For count=6 — μ_6 ⊂ F_97* (since 6 | 96).

Approach: brute-force scan small DFT supports {pos1, pos2}, {pos1, pos2, pos3}
with random coefficients, capturing every strict above-J case + bad α set
+ cyclotomic structure.
"""
import sys, os, math, random, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations, product
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


def exhaustive_above_J(f_arr, L0_arr, n0, k0, w_J, D0, inv_D0, p, batch_size=500000):
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


def is_subgroup(S, p):
    Sset = set(S)
    for a in S:
        for b in S:
            if (a * b) % p not in Sset:
                return False
    return True


def find_coset_structure(bad, p):
    if len(bad) == 0:
        return None
    bad = sorted(bad)
    for beta in range(p):
        translates = sorted([(b - beta) % p for b in bad])
        if 0 in translates:
            continue
        first = translates[0]
        first_inv = pow(first, p - 2, p)
        ratios = sorted({(t * first_inv) % p for t in translates})
        if is_subgroup(ratios, p):
            return (beta, first, len(ratios))
    return None


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
    info_sets = list(combinations(range(n1), k1))
    info_sets_arr = np.array(info_sets, dtype=np.int64)
    _state.update({
        'p': p, 'n0': n0, 'k0': k0, 'n1': n1, 'k1': k1,
        'L0': L0, 'L0_arr': L0_arr, 'L1_arr': L1_arr,
        'D0': D0, 'inv_D0': inv_D0, 'D1': D1, 'inv_D1': inv_D1,
        'info_sets_arr': info_sets_arr,
        'sqrt_k1n1': int(math.isqrt(k1 * n1)),
        'w_J': n0 - int(math.isqrt(k0 * n0)),
    })


def worker_check(positions_coeffs):
    positions, coeffs = positions_coeffs
    p = _state['p']; n0 = _state['n0']; k0 = _state['k0']
    n1 = _state['n1']; k1 = _state['k1']
    L0_arr = _state['L0_arr']; L1_arr = _state['L1_arr']
    D0 = _state['D0']; inv_D0 = _state['inv_D0']
    D1 = _state['D1']; inv_D1 = _state['inv_D1']
    info_sets_arr = _state['info_sets_arr']
    sqrt_k1n1 = _state['sqrt_k1n1']; w_J = _state['w_J']
    L0 = _state['L0']

    fhat = [0] * n0
    for pos, c in zip(positions, coeffs):
        fhat[pos] = c
    f = evaluate_dft_local(fhat, L0, p)
    f_arr = np.array(f, dtype=np.int64)

    n_zeros = int((f_arr == 0).sum())
    if n_zeros >= n0 - w_J:
        return ('zero', n_zeros)

    above_J, dist_f = exhaustive_above_J(f_arr, L0_arr, n0, k0, w_J, D0, inv_D0, p)
    if not above_J:
        return ('not_above', dist_f)

    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)
    threshold_d1 = n1 - sqrt_k1n1
    bad = []
    for a in range(p):
        fold = (f_e_arr + a * f_o_arr) % p
        extras = batched_extras(info_sets_arr, fold, L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras.max())
        if d1 <= threshold_d1:
            bad.append(a)

    coset = find_coset_structure(bad, p)
    return ('above', dist_f, len(bad), bad, list(positions), list(coeffs), coset)


def main():
    p = 97
    n0, k0 = 32, 8

    # Try ALL 2-position DFT supports with random coefficients
    rng = random.Random(2026)
    candidates = []

    # 2-pos exhaustive
    for pos in combinations(range(k0, n0), 2):
        # need at least 1 even and 1 odd among the 2
        evens = sum(1 for j in pos if j % 2 == 0)
        odds = sum(1 for j in pos if j % 2 == 1)
        if evens == 0 or odds == 0:
            continue
        # Try a few coefficient pairs
        for _ in range(40):
            coeffs = tuple(rng.randrange(1, p) for _ in pos)
            candidates.append((tuple(pos), coeffs))

    print(f"Total 2-pos candidates at q={p}: {len(candidates)}")

    n_workers = 10
    counts_seen = {}
    cyclotomic_breaks = []
    t0 = time.time()
    with Pool(processes=n_workers, initializer=worker_init, initargs=(p, n0, k0)) as pool:
        for i, res in enumerate(pool.imap_unordered(worker_check, candidates, chunksize=2)):
            if res[0] == 'above':
                _, dist_f, count, bad, pos, coeffs, coset = res
                counts_seen.setdefault(count, []).append((pos, coeffs, bad, coset))
                if coset is None:
                    cyclotomic_breaks.append((count, bad, pos, coeffs))
                    print(f"  ✗ NON-cyclotomic: count={count} bad={bad} pos={pos} coeffs={coeffs}", flush=True)
            if (i+1) % 500 == 0:
                elapsed = time.time() - t0
                print(f"  [{i+1}/{len(candidates)}] elapsed {elapsed:.0f}s, counts seen: {sorted(counts_seen)}", flush=True)

    elapsed = time.time() - t0
    print(f"\n=== Done in {elapsed:.0f}s ===")
    print(f"Counts seen: {dict(sorted({k: len(v) for k, v in counts_seen.items()}.items()))}")
    for c in sorted(counts_seen):
        ws = counts_seen[c]
        coset_summary = {}
        for w in ws:
            cset = w[3]
            if cset is None: key = "non-cyclo"
            else: key = (cset[2], cset[1])  # (|H|, λ)
            coset_summary[key] = coset_summary.get(key, 0) + 1
        print(f"  count={c}: {len(ws)} witnesses, structures: {coset_summary}")
        # Show one example
        if ws:
            pos, coeffs, bad, coset = ws[0]
            print(f"     example pos={pos} coeffs={coeffs} bad={bad} coset={coset}")
    if cyclotomic_breaks:
        print(f"\n*** Cyclotomic breakdowns: {len(cyclotomic_breaks)} ***")
    else:
        print("\n✓ All cases cyclotomic.")


if __name__ == "__main__":
    main()
