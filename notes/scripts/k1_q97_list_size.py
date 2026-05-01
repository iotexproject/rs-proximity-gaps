"""k1_q97_list_size.py — verify K=1 odd-odd q=97 'violation' is from list size > 1.

In universal_fiber_bound.py, K=1 odd-odd at q=97 attempt 5 gave N=96 violation
(all 96 nonzero α had d_1=9). Hypothesis: this is due to GS list size > 1
at this specific algebraic configuration.

For K=1 odd-odd: f_e = 0, fold_α = α·f_o. Closest codeword scales: c_α = α·c_o
where c_o ∈ C_1 minimizes dist(f_o, C_1) = 9.

If list size at agreement 7 with f_o is L > 1: each codeword scales by α, giving
L 'parallel' affine lines. Different α's might pick different c_o.

This script: pick a K=1 odd-odd above-J f at q=97, compute exact list size for f_o.
"""
from __future__ import annotations
import sys, os, random
import numpy as np
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

P = 97
N0 = 32
K0 = 8
R = 2

import probe_step5_n32_studio
probe_step5_n32_studio.P = P

from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft(fhat, L, p):
    return [sum(fhat[k] * pow(L[i], k, p) for k in range(len(fhat))) % p for i in range(len(L))]


def lagrange_interp(L, T_idx, vals_T, p):
    out = []
    for x_eval in L:
        v = 0
        for j_loc, j_T in enumerate(T_idx):
            num = 1; den = 1
            for k_loc, k_T in enumerate(T_idx):
                if k_loc == j_loc: continue
                num = (num * (x_eval - L[k_T])) % p
                den = (den * (L[j_T] - L[k_T])) % p
            term = (vals_T[j_loc] * num * pow(den, p - 2, p)) % p
            v = (v + term) % p
        out.append(v)
    return out


def exact_list_size(received, L1, k1, p, threshold):
    n1 = len(L1)
    seen = {}
    for T in combinations(range(n1), k1):
        T_idx = list(T)
        vals_T = [received[i] for i in T_idx]
        c_full = lagrange_interp(L1, T_idx, vals_T, p)
        agree = sum(1 for i in range(n1) if c_full[i] == received[i])
        if agree >= threshold:
            key = tuple(c_full)
            if key not in seen or seen[key] < agree:
                seen[key] = agree
    return len(seen), seen


def main():
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L0 = chain[0][0]
    L1, k1, _ = chain[1]
    n1 = len(L1)

    rng = random.Random(2026 + 97)  # match seed in universal_fiber_bound.py
    print(f"=== K=1 odd-odd at q={p}: exact list size at agreement 7 ===")
    print()

    # Find K=1 odd-odd above-J f with min d_1 = 9
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets = list(combinations(range(n1), k1))
    info_sets_arr = np.array(info_sets, dtype=np.int64)

    for attempt in range(1000):
        # Build K=1 odd-odd: f_e = 0, f_o nontrivial
        # Sparse odd Fourier support in [k_0, n_0)
        odd_pos = [i for i in range(K0, N0) if i % 2 == 1]
        n_pos = rng.choice([1, 2, 3])
        chosen = rng.sample(odd_pos, n_pos)
        fhat = [rng.randrange(p) for _ in range(K0)] + [0] * (N0 - K0)
        for pos in chosen:
            fhat[pos] = rng.randrange(1, p)
        f = evaluate_dft(fhat, L0, p)
        f_e, f_o = even_odd_parts(f, L0, p)
        if all(v == 0 for v in f_e):
            pass
        else:
            # Make pure odd by zeroing f_e
            f_e = [0] * n1
        # Compute distance of f_o to C_1
        f_o_arr = np.array(f_o, dtype=np.int64)
        extras = batched_extras(info_sets_arr, f_o_arr, L1_arr, D1, inv_D1, p)
        d_fo = n1 - k1 - int(extras.max())
        if d_fo != 9:
            continue
        # Found K=1 odd-odd with d(f_o, C_1) = 9
        print(f"Found K=1 odd-odd with dist(f_o, C_1) = {d_fo}, fhat odd positions = {chosen}")
        # Compute exact list size for f_o at agreement 7
        L_size, codewords = exact_list_size(f_o, L1, k1, p, threshold=7)
        print(f"\nExact list size at agreement ≥ 7 with f_o: {L_size}")
        for c, agree in codewords.items():
            print(f"  codeword (first 8 vals): {c[:8]}, agreement = {agree}")
        if L_size > 1:
            print(f"\n★ List size > 1 at q={p}: confirms algebraic artifact at this q.")
            print(f"  Multiple codewords at agreement ≥ 7 with f_o → multiple 'lines' in α.")
            print(f"  This is the structural cause of the N=96 'violation'.")
        break
    else:
        print(f"No K=1 odd-odd with d(f_o, C_1) = 9 found in 100 attempts.")


if __name__ == "__main__":
    main()
