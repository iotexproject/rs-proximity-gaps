"""g3_count_by_support.py — Conjecture E: count_α depends ONLY on DFT support.

Test: for each 3-position DFT support in syndrome window {8..31}, run multiple
random coefficient trials and verify count is invariant across trials.

If confirmed, count is a CLASS INVARIANT of the DFT support, dramatically
simplifying the structure of bad-α sets.

Then enumerate all 3-position supports and tabulate count by support.
"""
import sys, os, random, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter, defaultdict

from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft(fhat, L, p):
    n = len(L)
    f = [0] * n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j] != 0:
                v = (v + fhat[j] * pow(x, j, p)) % p
        f[i] = v
    return f


def compute_count(positions, coeffs, p, n0, k0, L0, L0_arr, L1_arr, D0, inv_D0,
                  D1, inv_D1, n1, k1, info_sets_arr_n1, info_sets_arr_n0):
    """Return (above_J, dist_f, count) — count = #bad alphas if above-J, else None."""
    fhat = [0] * n0
    for ps, c in zip(positions, coeffs):
        fhat[ps] = c
    f = evaluate_dft(fhat, L0, p)
    f_arr = np.array(f, dtype=np.int64)
    extras_n0 = batched_extras(info_sets_arr_n0, f_arr, L0_arr, D0, inv_D0, p)
    max_extras = int(extras_n0.max())
    d_f = n0 - k0 - max_extras
    above_J = d_f > 16
    if not above_J:
        return False, d_f, None
    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)
    threshold = 8
    cnt = 0
    for a in range(p):
        fold = (f_e_arr + a * f_o_arr) % p
        extras = batched_extras(info_sets_arr_n1, fold, L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras.max())
        if d1 <= threshold:
            cnt += 1
    return True, d_f, cnt


def main():
    p = 1153
    n0, k0 = 32, 8

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    n1, k1 = len(L1), k0 // 2
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets_n1 = list(combinations(range(n1), k1))
    info_sets_arr_n1 = np.array(info_sets_n1, dtype=np.int64)
    info_sets_n0 = list(combinations(range(n0), k0))
    info_sets_arr_n0 = np.array(info_sets_n0, dtype=np.int64)

    rng = random.Random(2026)

    # Enumerate ALL 3-position DFT supports in syndrome window {8..31}
    # (with at least 1 even and 1 odd to allow folding)
    supports = []
    for ps in combinations(range(8, 32), 3):
        has_e = any(j % 2 == 0 for j in ps)
        has_o = any(j % 2 == 1 for j in ps)
        if has_e and has_o:
            supports.append(ps)
    print(f"Total 3-pos supports with even+odd: {len(supports)}")

    # For each support, run 3 random coefficient trials.
    # Conjecture E: count is the same across all 3 trials.
    n_trials = 3
    results = defaultdict(list)
    invariants = {}
    above_J_supports = []
    t0 = time.time()
    for i, ps in enumerate(supports):
        cnts = []
        above_count = 0
        for tr in range(n_trials):
            coeffs = tuple(rng.randint(1, p-1) for _ in ps)
            above, df, cnt = compute_count(ps, coeffs, p, n0, k0, L0, L0_arr, L1_arr,
                                           D0, inv_D0, D1, inv_D1, n1, k1,
                                           info_sets_arr_n1, info_sets_arr_n0)
            if above:
                cnts.append(cnt)
                above_count += 1
        results[ps] = cnts
        if cnts:
            uniq = set(cnts)
            if len(uniq) == 1:
                invariants[ps] = next(iter(uniq))
                above_J_supports.append(ps)
            else:
                # NOT INVARIANT — record both
                invariants[ps] = ('VARIANT', cnts)
                above_J_supports.append(ps)
        if (i+1) % 100 == 0:
            elapsed = time.time() - t0
            print(f"  [{i+1}/{len(supports)}] above-J supports: {len(above_J_supports)}, elapsed {elapsed:.0f}s", flush=True)

    elapsed = time.time() - t0
    print(f"\n=== Done in {elapsed:.0f}s ===")
    print(f"Total above-J supports: {len(above_J_supports)}")

    # How many supports are CLASS INVARIANT vs VARIANT?
    n_invariant = sum(1 for v in invariants.values() if not isinstance(v, tuple))
    n_variant = sum(1 for v in invariants.values() if isinstance(v, tuple))
    print(f"Invariant (count fixed across trials): {n_invariant}")
    print(f"Variant (count depends on coeffs):    {n_variant}")

    # Histogram of count values
    count_dist = Counter()
    for ps, v in invariants.items():
        if not isinstance(v, tuple):
            count_dist[v] += 1
    print(f"\nCount-value histogram (across invariant supports):")
    for c in sorted(count_dist):
        print(f"  count={c}: {count_dist[c]} supports")

    # Show examples for each count value
    print(f"\nExample DFT supports per count value:")
    for c in sorted(count_dist):
        examples = [ps for ps, v in invariants.items() if v == c][:5]
        print(f"  count={c}: {examples}")

    # Show case (b) coverage: {16..23}
    caseB = [ps for ps in supports if all(16 <= j <= 23 for j in ps)]
    caseB_results = [(ps, invariants[ps]) for ps in caseB if ps in invariants]
    print(f"\nCase (b) supports (⊂ {{16..23}}): {len(caseB)}, with above-J: {len(caseB_results)}")
    if caseB_results:
        cnts = [c for _, c in caseB_results if not isinstance(c, tuple)]
        print(f"  Counts: {Counter(cnts)}")

    # Show variants explicitly
    if n_variant > 0:
        print(f"\nVariant supports (first 10):")
        for ps, v in list(invariants.items())[:200]:
            if isinstance(v, tuple):
                print(f"  pos={ps}: counts={v[1]}")


if __name__ == "__main__":
    main()
