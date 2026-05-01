"""Local multiprocess driver for G3 strict-above-J sweep — runs on M3 Pro 12 cores."""
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
    L1, _, _ = chain[1]
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
            bad.append((a, d1))
    return ('above_J', dist_f, len(bad), bad[:20], list(positions), list(coeffs))


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
    max_witness = None

    with Pool(processes=n_workers, initializer=worker_init, initargs=(p, n0, k0)) as pool:
        for i, res in enumerate(pool.imap_unordered(worker_check, candidates, chunksize=1)):
            tag = res[0]
            if tag == 'above_J':
                _, dist_f, count, bad, pos, coeffs = res
                above_J_results.append((dist_f, count, bad, pos, coeffs))
                if count > max_count:
                    max_count = count
                    max_witness = (i, dist_f, count, bad, pos, coeffs)
                    print(f"  [{i}/{len(candidates)}] above-J dist={dist_f} count={count} bad={bad} pos={pos}", flush=True)
                elif count >= 1 and count <= 2:
                    # Log every 10th case for reference
                    if len(above_J_results) % 20 == 0:
                        print(f"  [{i}/{len(candidates)}] above-J dist={dist_f} count={count} bad={bad}", flush=True)
            elif tag == 'not_above_J':
                n_below_J += 1
            elif tag == 'below_J_by_zeros':
                n_zeros += 1

            if (i + 1) % 100 == 0:
                elapsed = time.time() - t0
                print(f"    progress {i+1}/{len(candidates)} | strict above-J so far: {len(above_J_results)} | elapsed {elapsed:.0f}s", flush=True)

    elapsed = time.time() - t0
    distrib = {}
    for r in above_J_results:
        distrib[r[1]] = distrib.get(r[1], 0) + 1
    print(f"  Done q={p}: total {len(candidates)} in {elapsed:.0f}s ({elapsed/len(candidates):.2f}s/cand)")
    print(f"  Strict above-J: {len(above_J_results)} | not above-J: {n_below_J} | zero-saturated: {n_zeros}")
    print(f"  Count distribution: {dict(sorted(distrib.items()))}")
    print(f"  Max count: {max_count}")
    if max_witness:
        print(f"  Max witness: {max_witness}")
    return len(above_J_results), max_count, above_J_results


def main():
    n0, k0 = 32, 8
    primes_32 = [97, 193, 449, 769, 1153, 2113]
    n_candidates_per_q = 300  # ~80 min total at 10 workers
    n_workers = 10

    print(f"Local sweep: ({n0}, {k0}) at q ∈ {primes_32}, {n_candidates_per_q} candidates/q, {n_workers} workers")
    print(f"Hardware: M3 Pro 12 cores")
    overall_max = 0
    overall_n_above_J = 0
    all_above_J = {}
    for p in primes_32:
        n_above_J, max_count, results = sweep_q(p, n0, k0, n_candidates_per_q, n_workers, seed=2026 + p)
        overall_n_above_J += n_above_J
        if max_count > overall_max:
            overall_max = max_count
        all_above_J[p] = (n_above_J, max_count)

    print(f"\n=== OVERALL ({n0},{k0}) ===")
    print(f"  Total strict above-J cases: {overall_n_above_J}")
    print(f"  Overall max count: {overall_max}")
    print(f"  PR #372 D bound: 124. Legacy 𝔠 bound: 234.")
    print(f"  Per-q: {all_above_J}")
    if overall_max == 1:
        print("  ✓ Empirical: count ≤ 1 universally across this sample.")
    elif overall_max <= 9:
        print("  ✓ Empirical: count ≤ 9 (matches 2-α-lift packing bound).")


if __name__ == "__main__":
    main()
