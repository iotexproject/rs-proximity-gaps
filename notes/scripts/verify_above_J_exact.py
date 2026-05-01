"""verify_above_J_exact.py — exact above-J verification for the 3 outliers.

The (i, i+8) family sweep found 3 candidates with tie_upper > 0.4490:
  (14, 22) coefs (72, 45): tie = 0.5052
  ( 8, 16) coefs (65, 77): tie = 0.5000
  (16, 24) coefs (15, 73): tie = 0.5000

dist_lower_bound_sampling uses 2000 random samples — could miss a close codeword.
This script does EXACT distance via info-set enumeration over C(32, 8) = 10,518,300.

If exact distance ≤ 16 = w_J: candidate is BELOW-J (sampling false positive).
If exact distance > 16: candidate is genuinely above-J — Theorem 8.2 needs revision.

Usage: python3 verify_above_J_exact.py
"""
from __future__ import annotations
import sys, os, time
from itertools import combinations
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_step5_n32_studio import P, N0, K0, R, N_R, W_J, evaluate_dft
from fri_2round_attack import setup_chain, dist_to_code_full, parity_check
from mds_decoder import precompute_diff_inv, batched_extras


def exact_distance_n32(f, L0, K0, p, batch_size=20000):
    """Exact dist(f, RS_{K0}(L0)) via batched info-set enumeration.

    For n=32, k=8: C(32, 8) = 10,518,300 subsets. Batched in chunks of 20K.
    Total time ~ 30-60 seconds.
    """
    L_arr = np.array(L0, dtype=np.int64)
    f_arr = np.array(f, dtype=np.int64)
    D, inv_D = precompute_diff_inv(L_arr, p)
    n = len(L0)
    max_extras = -1
    n_processed = 0
    t0 = time.time()
    info_set_iter = combinations(range(n), K0)
    while True:
        batch = list()
        try:
            for _ in range(batch_size):
                batch.append(next(info_set_iter))
        except StopIteration:
            pass
        if not batch:
            break
        T_batch = np.array(batch, dtype=np.int64)
        extras = batched_extras(T_batch, f_arr, L_arr, D, inv_D, p)
        m = int(extras.max())
        if m > max_extras:
            max_extras = m
        n_processed += len(batch)
    elapsed = time.time() - t0
    d = n - K0 - max_extras
    return d, elapsed, n_processed


def main():
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L0 = chain[0][0]

    candidates = [
        ((14, 22), (72, 45), 0.5052),
        (( 8, 16), (65, 77), 0.5000),
        ((16, 24), (15, 73), 0.5000),
        ((15, 23), (10, 17), 0.4490),  # baseline (verified above-J in prior work)
    ]

    print(f"Exact above-J verification (C(32,8)=10.5M info sets per candidate)")
    print(f"  w_J = {W_J} ⟹ above-J iff dist(f, C_0) > {W_J}")
    print()

    for (i, j), (a, b), tie_reported in candidates:
        fhat = [0] * N0
        fhat[i] = a
        fhat[j] = b
        f = evaluate_dft(fhat, L0, p)
        print(f"--- ({i}, {j}) coefs ({a}, {b}), reported tie={tie_reported:.4f} ---")
        t0 = time.time()
        d, elapsed, n_proc = exact_distance_n32(f, L0, K0, p)
        print(f"  exact dist = {d}  (above-J: {d > W_J})  ({elapsed:.0f}s, {n_proc} info sets)")
        if d <= W_J:
            print(f"  ⚠ FALSE POSITIVE — sampling missed close codeword (dist={d} ≤ w_J={W_J})")
        else:
            print(f"  ✓ GENUINELY above-J (dist={d} > w_J={W_J})")
            if tie_reported > 0.5:
                print(f"  ⚠⚠ tie_upper = {tie_reported:.4f} > 0.5 = √ρ_0 — Theorem 8.2 BREAKS at toy params")


if __name__ == '__main__':
    main()
