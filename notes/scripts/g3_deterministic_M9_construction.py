"""g3_deterministic_M9.py — explicit construction targeting M=9 at q=193.

Setup: pick K = ω^0, ..., ω^6 (size 7). For y ∈ L_1 \ K (9 values):
  - φ(y) = distinct values in F_q \ L_0
  - B(y) = 1 for simplicity
  - A(y) = -φ(y) (since A = -φ * B and B = 1)
  - f_e(y) = A(y), f_o(y) = B(y) on L_1 \ K; both 0 on K.

Goal: verify f is strictly above-J AND count_α = 9.
"""
import sys, os, math
import numpy as np
from itertools import combinations

sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))
from fri_2round_attack import setup_chain
from mds_decoder import precompute_diff_inv, batched_extras


def main():
    n0, k0 = 32, 8
    n1, k1 = 16, 4
    s = 8
    w_J = n0 - int(math.isqrt(k0 * n0))

    for p in [97, 193, 449]:
        chain = setup_chain(p, n0, k0, R=2)
        L0 = chain[0][0]
        L1 = chain[1][0]
        L0_set = set(L0)
        L0_arr = np.array(L0, dtype=np.int64)
        L1_arr = np.array(L1, dtype=np.int64)
        Fq_minus_L0 = sorted([a for a in range(p) if a not in L0_set])
        if len(Fq_minus_L0) < 9:
            print(f"q={p}: too few F_q\\L_0 elements ({len(Fq_minus_L0)})")
            continue

        print(f"\n=== q={p}: |L_0|={len(L0)}, |F_q\\L_0|={len(Fq_minus_L0)} ===")
        # K = first 7 indices of L_1
        K_idx = list(range(7))
        out_K_idx = list(range(7, 16))  # 9 indices
        K_vals = [L1[i] for i in K_idx]

        # Pick first 9 distinct values from F_q \ L_0
        phi_values = Fq_minus_L0[:9]
        print(f"K = ω^0..ω^6 = {K_vals}")
        print(f"φ values (distinct, ∉ L_0) = {phi_values}")

        # B(y) = 1, A(y) = -φ(y) for y in L_1 \ K
        f_e = [0] * n1
        f_o = [0] * n1
        for j, idx in enumerate(out_K_idx):
            f_e[idx] = (-phi_values[j]) % p
            f_o[idx] = 1
        # K positions: f_e[i] = f_o[i] = 0 already.

        # Construct f on L_0
        f = [0] * n0
        for i, x in enumerate(L0):
            x2 = (x * x) % p
            j = L1.index(x2)
            f[i] = (f_e[j] + x * f_o[j]) % p
        f_arr = np.array(f, dtype=np.int64)
        n_zeros_f = int((f_arr == 0).sum())
        print(f"f vanishes on {n_zeros_f} L_0 positions (expected 14 = 2|K|)")

        # Exhaustive above-J check
        D0, inv_D0 = precompute_diff_inv(L0_arr, p)
        threshold = n0 - k0 - w_J  # 8
        max_extras = 0
        all_T = list(combinations(range(n0), k0))
        batch_size = 500000
        for start in range(0, len(all_T), batch_size):
            batch = all_T[start:start + batch_size]
            T_arr = np.array(batch, dtype=np.int64)
            extras = batched_extras(T_arr, f_arr, L0_arr, D0, inv_D0, p)
            m = int(extras.max())
            if m > max_extras:
                max_extras = m
        dist_f = n0 - k0 - max_extras
        print(f"dist(f, C_0) = {dist_f} (Johnson w_J = {w_J})")
        above_J = dist_f > w_J
        print(f"strict above-J: {above_J}")

        if not above_J:
            print(f"  Construction NOT strict above-J — likely some other codeword too close.")
            continue

        # Count bad α
        f_e_arr = np.array(f_e, dtype=np.int64)
        f_o_arr = np.array(f_o, dtype=np.int64)
        info_sets = list(combinations(range(n1), k1))
        info_sets_arr = np.array(info_sets, dtype=np.int64)
        D1, inv_D1 = precompute_diff_inv(L1_arr, p)
        bad = []
        for a in range(p):
            fold = (f_e_arr + a * f_o_arr) % p
            extras = batched_extras(info_sets_arr, fold, L1_arr, D1, inv_D1, p)
            d1 = n1 - k1 - int(extras.max())
            if d1 <= n1 - s:
                bad.append((a, d1))
        print(f"count_α(d_1 ≤ {n1-s}) = {len(bad)}")
        print(f"bad α: {bad[:15]}")
        if len(bad) >= 9:
            print(f"  *** SUCCESS: M = {len(bad)} ≥ 9 ***")


if __name__ == "__main__":
    main()
