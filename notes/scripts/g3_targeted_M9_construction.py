"""g3_targeted_M9.py — try to construct strict above-J f with count_α = M ∈ {2,...,9}.

Strategy: pick K ⊂ L_1 of size |K| ∈ {6, 7}. Pick φ: L_1 \ K → F_q taking distinct
values, all in F_q \ L_0. Then construct (f_e, f_o) such that:
  - f_e, f_o vanish on K (so K is the kernel)
  - On L_1 \ K: A(y) = -φ(y) B(y) for chosen B(y) ≠ 0
This gives count_α(d_1 ≤ 8) = #{y ∈ L_1 \ K : φ(y) ∈ φ(L_1\K)} = |L_1 \ K| if φ injective.

Plus: ensure strict above-J w.r.t. (P_e, P_o) = (0, 0) lift, requires φ(y) ∉ L_0
for all y, so bonus = 0.

Plus: ensure strict above-J w.r.t. ALL OTHER C_0 codewords. This is the hardest part —
we'll just check empirically.
"""
import sys, os, math, random
import numpy as np
from itertools import combinations

sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))
from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def construct_targeted_f(p, K_idx, target_phi_values, B_values):
    """K_idx: indices in L_1 (size |K|=6 or 7). target_phi_values: φ(y) for y in L_1\K.
       B_values: chosen B(y) values for y in L_1\K (all nonzero in F_q).
       Returns f_e, f_o on L_1 (and reconstructs f on L_0)."""
    n0, k0 = 32, 8
    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L1 = chain[1][0]
    n1 = len(L1); k1 = k0 // 2
    L0_arr = np.array(L0, dtype=np.int64)
    L1_arr = np.array(L1, dtype=np.int64)

    # f_e and f_o vanish on K, so they're polys in y of the form g_K(y) * h(y)
    # where g_K(y) = ∏_{a ∈ K} (y - L1[a]).
    K_vals = [L1[i] for i in K_idx]

    # We want: A(y) := f_e(y) = -φ(y) B(y) on L_1 \ K.
    # And f_o(y) = B(y) on L_1 \ K.
    # On K: both zero.
    f_e = [0] * n1
    f_o = [0] * n1
    out_K = [i for i in range(n1) if i not in K_idx]
    if len(out_K) != len(target_phi_values):
        raise ValueError(f"len(out_K)={len(out_K)} != len(phi)={len(target_phi_values)}")
    for j, i in enumerate(out_K):
        # f_o(y_i) = B[j], f_e(y_i) = -phi[j] * B[j]
        f_o[i] = B_values[j] % p
        f_e[i] = (-target_phi_values[j] * B_values[j]) % p
    # K positions: f_e[K] = f_o[K] = 0 (already initialized).

    # Reconstruct f on L_0
    f = [0] * n0
    for i, x in enumerate(L0):
        x2 = (x * x) % p
        j = L1.index(x2)
        f[i] = (f_e[j] + x * f_o[j]) % p

    return f, f_e, f_o, L0, L1, L0_arr, L1_arr


def exhaustive_above_J(f_arr, L0_arr, n0, k0, w_J, D0, inv_D0, p, batch_size=500000):
    threshold = n0 - k0 - w_J
    max_extras = 0
    all_T = list(combinations(range(n0), k0))
    for start in range(0, len(all_T), batch_size):
        batch = all_T[start:start + batch_size]
        T_arr = np.array(batch, dtype=np.int64)
        extras = batched_extras(T_arr, f_arr, L0_arr, D0, inv_D0, p)
        m = int(extras.max())
        if m > max_extras: max_extras = m
        if max_extras >= threshold:
            return False, n0 - k0 - max_extras
    return max_extras < threshold, n0 - k0 - max_extras


def count_alpha(f_e_arr, f_o_arr, L1_arr, p, n1=16, k1=4, sqrt_k1n1=8):
    info_sets = list(combinations(range(n1), k1))
    info_sets_arr = np.array(info_sets, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    threshold_d1 = n1 - sqrt_k1n1
    bad = []
    for a in range(p):
        fold = (f_e_arr + a * f_o_arr) % p
        extras = batched_extras(info_sets_arr, fold, L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras.max())
        if d1 <= threshold_d1:
            bad.append((a, d1))
    return bad


def main():
    n0, k0 = 32, 8
    w_J = 16
    n1, k1 = 16, 4

    for p in [2113, 1153, 769]:
        chain = setup_chain(p, n0, k0, R=2)
        L0 = chain[0][0]
        L1 = chain[1][0]
        L0_set = set(L0)
        n_L0 = len(L0)
        Fq_minus_L0 = [a for a in range(p) if a not in L0_set]

        print(f"\n=== q={p}: |L_0|={n_L0}, |F_q \\ L_0|={len(Fq_minus_L0)} ===", flush=True)

        rng = random.Random(2026 + p)
        n_attempts = 0
        n_strict = 0
        max_count = 0
        max_witness = None

        for K_size in [7, 6]:
            for trial in range(50):
                n_attempts += 1
                K_idx = rng.sample(range(n1), K_size)
                out_K = [i for i in range(n1) if i not in K_idx]
                # Pick distinct φ values from F_q \ L_0
                phi_values = rng.sample(Fq_minus_L0, len(out_K))
                B_values = [rng.randrange(1, p) for _ in out_K]

                try:
                    f, f_e, f_o, _, _, L0_arr, L1_arr = construct_targeted_f(
                        p, K_idx, phi_values, B_values
                    )
                except Exception as e:
                    print(f"  construct error: {e}")
                    continue
                f_arr = np.array(f, dtype=np.int64)

                # Count zeros
                n_zeros = int((f_arr == 0).sum())
                if n_zeros >= n0 - w_J:
                    continue

                # Strict above-J check
                D0, inv_D0 = precompute_diff_inv(L0_arr, p)
                above_J, dist_f = exhaustive_above_J(f_arr, L0_arr, n0, k0, w_J, D0, inv_D0, p)
                if not above_J:
                    continue
                n_strict += 1

                # Count bad α
                f_e_arr = np.array(f_e, dtype=np.int64)
                f_o_arr = np.array(f_o, dtype=np.int64)
                bad = count_alpha(f_e_arr, f_o_arr, L1_arr, p, n1, k1)

                if len(bad) > max_count:
                    max_count = len(bad)
                    max_witness = (K_size, K_idx, phi_values[:5], B_values[:5], dist_f, bad[:10])
                    print(f"  K={K_size}, dist={dist_f}, count={len(bad)}, bad={bad[:10]}", flush=True)

                if len(bad) >= 2:
                    print(f"  *** COUNT ≥ 2 FOUND at q={p}, K_size={K_size}", flush=True)
                    print(f"      K_idx={K_idx}, dist={dist_f}, bad={bad}", flush=True)

        print(f"  q={p}: attempts={n_attempts}, strict above-J={n_strict}, max count={max_count}")
        if max_witness:
            print(f"  Max witness: {max_witness}")


if __name__ == "__main__":
    main()
