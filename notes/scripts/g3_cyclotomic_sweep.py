"""g3_cyclotomic_sweep.py — large sweep to test Conjecture D.

For every strict above-Johnson candidate, record:
  - bad-α set
  - whether bad-α set is a translated multiplicative coset of F_q*
  - if yes, the (β, λ, |H|) parameters
  - else: structural decomposition

Run at q ∈ {97, 193, 449, 769} with up to 2000 candidates each, 10 workers.
"""
import sys, os, math, random, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
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


def is_subgroup(S, p):
    Sset = set(S)
    for a in S:
        for b in S:
            if (a * b) % p not in Sset:
                return False
    return True


def find_coset_structure(bad, p):
    """Return (β, λ, H) if bad = β + λ · H for some F_p* subgroup H, else None."""
    if len(bad) == 0:
        return None
    bad = sorted(bad)
    for beta in range(p):
        translates = sorted([(b - beta) % p for b in bad])
        if 0 in translates:
            continue
        first = translates[0]
        first_inv = pow(first, p - 2, p)
        ratios_set = set((t * first_inv) % p for t in translates)
        ratios = sorted(ratios_set)
        if is_subgroup(ratios, p):
            return (beta, first, len(ratios), ratios)
    return None


def worker_check(positions_coeffs):
    positions, coeffs = positions_coeffs
    p, n0, k0 = _state['p'], _state['n0'], _state['k0']
    n1, k1 = _state['n1'], _state['k1']
    L0_arr = _state['L0_arr']
    L1_arr = _state['L1_arr']
    D0, inv_D0 = _state['D0'], _state['inv_D0']
    D1, inv_D1 = _state['D1'], _state['inv_D1']
    info_sets_arr = _state['info_sets_arr']
    sqrt_k1n1 = _state['sqrt_k1n1']
    w_J = _state['w_J']
    L0 = _state['L0']

    fhat = [0] * n0
    for pos, c in zip(positions, coeffs):
        fhat[pos] = c
    f = evaluate_dft_local(fhat, L0, p)
    f_arr = np.array(f, dtype=np.int64)

    n_zeros = int((f_arr == 0).sum())
    if n_zeros >= n0 - w_J:
        return ('below_J_by_zeros', n_zeros)

    above_J, dist_f = exhaustive_above_J(f_arr, L0_arr, n0, k0, w_J, D0, inv_D0, p)
    if not above_J:
        return ('not_above_J', dist_f)

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

    coset_info = find_coset_structure(bad, p)
    return ('above_J', dist_f, len(bad), bad, list(positions), list(coeffs),
            coset_info)


def generate_candidates(p, n0, k0, n_candidates, seed):
    rng = random.Random(seed)
    out = []
    while len(out) < n_candidates:
        n_pos = rng.choice([3, 4, 5, 6, 7])
        positions = sorted(rng.sample(range(k0, n0), n_pos))
        has_even = any(j % 2 == 0 for j in positions)
        has_odd = any(j % 2 == 1 for j in positions)
        if not (has_even and has_odd):
            continue
        coeffs = [rng.randrange(1, p) for _ in positions]
        out.append((tuple(positions), tuple(coeffs)))
    return out


def sweep_q(p, n0, k0, n_candidates, n_workers, seed):
    print(f"\n=== q={p}: candidates={n_candidates}, workers={n_workers} ===", flush=True)
    candidates = generate_candidates(p, n0, k0, n_candidates, seed)
    t0 = time.time()
    above_J_results = []
    n_below_J = 0
    n_zeros = 0
    max_count = 0
    cyclotomic_count = 0
    non_cyclotomic = []

    with Pool(processes=n_workers, initializer=worker_init, initargs=(p, n0, k0)) as pool:
        for i, res in enumerate(pool.imap_unordered(worker_check, candidates, chunksize=1)):
            tag = res[0]
            if tag == 'above_J':
                _, dist_f, count, bad, pos, coeffs, coset_info = res
                above_J_results.append((dist_f, count, bad, pos, coeffs, coset_info))
                if coset_info is not None:
                    cyclotomic_count += 1
                else:
                    non_cyclotomic.append((count, bad, pos, coeffs))
                if count > max_count:
                    max_count = count
                    cs = "cyclotomic" if coset_info else "NON-cyclotomic"
                    print(f"  [{i}/{len(candidates)}] above-J dist={dist_f} count={count} bad={bad} pos={pos} {cs}: {coset_info}", flush=True)

            elif tag == 'not_above_J':
                n_below_J += 1
            elif tag == 'below_J_by_zeros':
                n_zeros += 1

            if (i + 1) % 200 == 0:
                elapsed = time.time() - t0
                print(f"    progress {i+1}/{len(candidates)} | strict above-J: {len(above_J_results)} | cyclotomic: {cyclotomic_count} | non-cyclo: {len(non_cyclotomic)} | elapsed {elapsed:.0f}s", flush=True)

    elapsed = time.time() - t0
    print(f"\n  Done q={p}: {len(candidates)} cands in {elapsed:.0f}s")
    print(f"  Strict above-J: {len(above_J_results)} | not above-J: {n_below_J} | zero-saturated: {n_zeros}")
    print(f"  Cyclotomic: {cyclotomic_count} | Non-cyclotomic: {len(non_cyclotomic)}")
    print(f"  Max count: {max_count}")
    if non_cyclotomic:
        print(f"  Non-cyclotomic samples (up to 5):")
        for nc in non_cyclotomic[:5]:
            print(f"    count={nc[0]} bad={nc[1]} pos={nc[2]} coeffs={nc[3]}")
    distrib_count = {}
    for r in above_J_results:
        distrib_count[r[1]] = distrib_count.get(r[1], 0) + 1
    print(f"  Count distribution: {dict(sorted(distrib_count.items()))}")
    return len(above_J_results), max_count, above_J_results, non_cyclotomic


def main():
    n0, k0 = 32, 8
    # q=1153 is the smallest test prime with 9 | (q-1) — under Conjecture D
    # this is the FIRST place where count=9 is allowed (divisor of q-1).
    primes_32 = [1153]
    n_candidates_per_q = 300
    n_workers = 20  # studio has 28 cores; user works locally not on studio

    print(f"Local cyclotomic sweep: ({n0}, {k0}) at q ∈ {primes_32}, {n_candidates_per_q} candidates/q, {n_workers} workers")
    overall_max = 0
    all_results = {}
    all_non_cyc = []
    for p in primes_32:
        n_above_J, max_count, results, non_cyc = sweep_q(p, n0, k0, n_candidates_per_q, n_workers, seed=2026 + p)
        if max_count > overall_max:
            overall_max = max_count
        all_results[p] = (n_above_J, max_count, len(non_cyc))
        all_non_cyc.extend([(p, *nc) for nc in non_cyc])

    print(f"\n=== OVERALL ({n0},{k0}) ===")
    print(f"  Per-q (n_above_J, max_count, n_non_cyclotomic): {all_results}")
    print(f"  Overall max count: {overall_max}")
    print(f"  Total non-cyclotomic: {len(all_non_cyc)}")
    if all_non_cyc:
        print(f"  Conjecture D NEEDS REFINEMENT — found {len(all_non_cyc)} non-cyclotomic witnesses")
        for p, count, bad, pos, coeffs in all_non_cyc[:10]:
            print(f"    q={p}, count={count}, bad={bad}, pos={pos}, coeffs={coeffs}")
    else:
        print(f"  ✓ Conjecture D HOLDS for all {sum(r[0] for r in all_results.values())} strict above-J cases.")


if __name__ == "__main__":
    main()
