"""g3_count_alpha_sweep.py — measure max count_α(d_1 ≤ √(k_1 n_1)) across q.

The universal 𝔠(n_1, k_1) = C(n_1, k_1)·(n_1-√+1)/C(√, k_1) is exponential in n_1
at fixed rate. Empirical question: is the actual max count sublinear in n_1?

At (32, 8): 𝔠 = 234, but Note 0146 / verify_zT_universal_K saw max count = 8
across 180 above-J cases at q ∈ {97, 193, 449}. This script extends to larger q
and to (64, 16) deployment params to see if the pattern persists.

Hypothesis: max count_α(d_1 ≤ √(k_1 n_1)) ≤ 2 √(k_1 n_1) universally over above-J f
                                                                  (q-INDEPENDENT)
"""
from __future__ import annotations
import sys, os, random, math
import numpy as np
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import (
    precompute_diff_inv, batched_extras, dist_lower_bound_sampling
)


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


def exhaustive_above_J(f_arr, L0_arr, n0, k0, w_J, D0, inv_D0, p, batch_size=200000):
    """Rigorous: dist(f, C_0) > w_J ?  Enumerate all C(n_0, k_0) info sets."""
    threshold = n0 - k0 - w_J  # extras < threshold ⟺ dist > w_J
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
            return False, max_extras
    return max_extras < threshold, max_extras


def count_bad_alpha(f_e_arr, f_o_arr, L1_arr, info_sets_arr, D1, inv_D1, p, n1, k1, sqrt_k1n1):
    """count_α(d_1(α) ≤ n_1 - √(k_1 n_1)) over all α ∈ F_q."""
    threshold_d1 = n1 - sqrt_k1n1
    count = 0
    for a in range(p):
        fold = (f_e_arr + a * f_o_arr) % p
        extras = batched_extras(info_sets_arr, fold, L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras.max())
        if d1 <= threshold_d1:
            count += 1
    return count


def sweep(n0, k0, primes, n_above_J_per_q=30, max_tries=600, seed=2026):
    n1 = n0 // 2
    k1 = k0 // 2
    sqrt_k1n1 = int(math.isqrt(k1 * n1))
    w_J = n0 - int(math.isqrt(k0 * n0))
    threshold_d1 = n1 - sqrt_k1n1

    print(f"=== Sweep ({n0}, {k0}): n_1={n1}, k_1={k1}, √(k_1 n_1)={sqrt_k1n1} ===")
    print(f"  Johnson radius w_J = {w_J}")
    print(f"  Threshold d_1 ≤ {threshold_d1}, agreement ≥ {sqrt_k1n1}")
    C_n1_k1 = math.comb(n1, k1)
    C_sqrt_k1 = math.comb(sqrt_k1n1, k1)
    bound_universal = C_n1_k1 * (n1 - sqrt_k1n1 + 1) // C_sqrt_k1
    print(f"  Universal 𝔠(n_1, k_1) bound: {bound_universal}")
    print(f"  Conjectured sublinear bound (≤ 2√(k_1 n_1)): {2 * sqrt_k1n1}")
    print()

    overall_max_count = 0
    overall_max_witness = None

    for p in primes:
        if (p - 1) % n0 != 0:
            continue
        try:
            chain = setup_chain(p, n0, k0, R=2)
        except Exception as e:
            print(f"  q={p}: setup failed: {e}")
            continue
        L0 = chain[0][0]
        L0_arr = np.array(L0, dtype=np.int64)
        L1, _, _ = chain[1]
        L1_arr = np.array(L1, dtype=np.int64)
        D0, inv_D0 = precompute_diff_inv(L0_arr, p)
        D1, inv_D1 = precompute_diff_inv(L1_arr, p)
        info_sets = list(combinations(range(n1), k1))
        info_sets_arr = np.array(info_sets, dtype=np.int64)

        rng = random.Random(seed + p)

        max_count = 0
        max_witness = None
        n_above_J = 0
        n_tries = 0
        count_distribution = {}

        while n_above_J < n_above_J_per_q and n_tries < max_tries:
            n_tries += 1
            n_pos = rng.choice([3, 4, 5, 6, 7])
            positions = sorted(rng.sample(range(k0, n0), n_pos))
            has_even = any(j % 2 == 0 for j in positions)
            has_odd = any(j % 2 == 1 for j in positions)
            if not (has_even and has_odd):
                continue
            fhat = [0] * n0
            for pos in positions:
                fhat[pos] = rng.randrange(1, p)
            f = evaluate_dft_local(fhat, L0, p)
            f_arr_check = np.array(f, dtype=np.int64)
            # Quick sampling filter (fast reject of below-J cases)
            d = dist_lower_bound_sampling(
                f, L0, k0, p, n_samples=5000, batch=2048,
                seed=rng.randrange(10**9)
            )
            if d <= w_J:
                continue
            # Rigorous exhaustive above-J check (sampling can over-estimate distance)
            above_J, max_extras = exhaustive_above_J(
                f_arr_check, L0_arr, n0, k0, w_J, D0, inv_D0, p
            )
            if not above_J:
                continue
            n_above_J += 1
            f_e, f_o = even_odd_parts(f, L0, p)
            f_e_arr = np.array(f_e, dtype=np.int64)
            f_o_arr = np.array(f_o, dtype=np.int64)
            count = count_bad_alpha(
                f_e_arr, f_o_arr, L1_arr, info_sets_arr, D1, inv_D1,
                p, n1, k1, sqrt_k1n1
            )
            count_distribution[count] = count_distribution.get(count, 0) + 1
            if count > max_count:
                max_count = count
                max_witness = (positions, [int(fhat[pos]) for pos in positions])
                print(f"    q={p} new max count = {count}, positions={positions}, coeffs={max_witness[1]}")

        print(f"  q={p}: above-J cases = {n_above_J}, max count = {max_count}")
        print(f"    distribution = {dict(sorted(count_distribution.items()))}")
        if max_count > overall_max_count:
            overall_max_count = max_count
            overall_max_witness = (p, max_witness)
        print()

    print(f"=== Overall summary ({n0}, {k0}) ===")
    print(f"  Max count_α(d_1 ≤ {threshold_d1}) observed: {overall_max_count}")
    print(f"  Universal 𝔠 bound: {bound_universal} (loose by {bound_universal // max(1, overall_max_count)}×)")
    print(f"  Conjectured 2√(k_1 n_1) bound: {2 * sqrt_k1n1}")
    if overall_max_count <= 2 * sqrt_k1n1:
        print(f"  ✓ Conjecture max ≤ 2√(k_1 n_1) HOLDS empirically")
    else:
        print(f"  ✗ Conjecture violated — refine")
    if overall_max_witness:
        p, w = overall_max_witness
        print(f"  Witness: q={p}, positions={w[0]}, coeffs={w[1]}")
    print()
    return overall_max_count


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="Small sweep for testing")
    args = parser.parse_args()
    if args.quick:
        sweep(32, 8, [97, 193], n_above_J_per_q=10)
    else:
        primes_32 = [97, 193, 449, 769, 1153, 1409, 2113]
        sweep(32, 8, primes_32, n_above_J_per_q=20)
