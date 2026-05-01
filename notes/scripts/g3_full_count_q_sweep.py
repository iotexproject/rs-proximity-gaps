"""g3_full_count_q_sweep.py — comprehensive sweep across all 3-pos supports
(syndrome window {8..31}) at q=1153, finding ALL count=q witnesses, with
the conjectured characterization:

CONJECTURE (loop iter 3):
  count = q  ⟺  for some shift t with |t| ≥ k_1 = 4 within 0..n_1-1,
                f_e and f_o L_1-DFT supports both lie in the cyclic
                interval {t, t+1, ..., t+k_1-1} mod n_1.

Mechanism: on subdomain {y : y^{n_1/(t cyclic)} = 1} (more carefully:
y^{gcd of relevant} = 1), the monomial f_e and f_o restrict to RS_{k_1}
codewords (after dividing by y^t).
"""
import sys, os, math, random
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter
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


def count_bad_alpha(positions, coeffs, p, n0, k0, threshold,
                    L0, L1_arr, all_T, D1, inv_D1):
    fhat = [0] * n0
    for ps, c in zip(positions, coeffs):
        fhat[ps] = c
    f = evaluate_dft_local(fhat, L0, p)
    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)
    n1 = len(L1_arr)
    k1 = k0 // 2

    cnt = 0
    for alpha in range(p):
        fold = (f_e_arr + alpha * f_o_arr) % p
        extras = batched_extras(all_T, fold, L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras.max())
        if d1 <= threshold:
            cnt += 1
    return cnt


def L1_dft_positions(positions):
    """For sup (a, b, c) ⊂ [0..n_0-1], compute (f_e_DFT_supp, f_o_DFT_supp) on L_1."""
    fe, fo = [], []
    for j in positions:
        if j % 2 == 0:
            fe.append(j // 2)
        else:
            fo.append((j - 1) // 2)
    return tuple(sorted(fe)), tuple(sorted(fo))


def in_cyclic_interval(positions, n, length):
    """True if positions all fit in some cyclic interval of length L mod n."""
    pos = sorted(positions)
    for start in range(n):
        if all((p - start) % n < length for p in pos):
            return True, start
    return False, None


def main():
    p = 1153
    n0, k0 = 32, 8
    n1, k1 = 16, 4
    threshold = n1 - int(math.isqrt(k1 * n1))  # = 8

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    all_T = np.array(list(combinations(range(n1), k1)), dtype=np.int64)

    # Gather all 3-pos supports with both even and odd elements
    all_sups = []
    for sup in combinations(range(8, 32), 3):
        has_even = any(j % 2 == 0 for j in sup)
        has_odd = any(j % 2 == 1 for j in sup)
        if has_even and has_odd:
            all_sups.append(sup)

    print(f"=== Full count=q sweep at q={p} ({n0},{k0}), {len(all_sups)} supports ===\n")

    rng = random.Random(2026)

    count_q_sups = []
    other_high = []
    for sup in all_sups:
        coeffs = tuple(rng.randrange(1, p) for _ in range(3))
        cnt = count_bad_alpha(sup, coeffs, p, n0, k0, threshold,
                               L0, L1_arr, all_T, D1, inv_D1)
        if cnt > 100:
            count_q_sups.append((sup, cnt))
        elif cnt > 9:
            other_high.append((sup, cnt))

    print(f"\nFound {len(count_q_sups)} count>100 supports (likely count=q).")
    print(f"Found {len(other_high)} other count>9 supports.\n")

    # check conjecture for count=q
    print("=== Verify each count=q support: f_e, f_o DFT supports on L_1 ===")
    in_interval = 0
    not_in_interval = []
    for sup, cnt in count_q_sups:
        fe_supp, fo_supp = L1_dft_positions(sup)
        all_supp = sorted(set(fe_supp + fo_supp))
        ok_4, start_4 = in_cyclic_interval(all_supp, n1, k1)
        if ok_4:
            in_interval += 1
        else:
            not_in_interval.append((sup, fe_supp, fo_supp, all_supp))

    print(f"  {in_interval}/{len(count_q_sups)} count=q supports have all L_1 DFT positions ⊂ length-{k1} cyclic interval mod {n1}")
    if not_in_interval:
        print(f"  {len(not_in_interval)} supports VIOLATE the conjecture:")
        for sup, fe, fo, all_s in not_in_interval[:10]:
            print(f"    sup={sup}, f_e_supp={fe}, f_o_supp={fo}, union={all_s}")

    # Reverse: any sup with all L_1 DFT in length-k_1 cyclic interval BUT NOT count=q?
    print("\n=== Reverse check: supports with L_1 DFT in length-k_1 interval ===")
    interval_sups = []
    for sup in all_sups:
        fe, fo = L1_dft_positions(sup)
        all_supp = sorted(set(fe + fo))
        ok, _ = in_cyclic_interval(all_supp, n1, k1)
        if ok:
            interval_sups.append(sup)
    print(f"  {len(interval_sups)} supports have L_1 DFT in length-{k1} cyclic interval mod {n1}")
    cnt_q_set = set(s for s, _ in count_q_sups)
    extras = [s for s in interval_sups if s not in cnt_q_set]
    if extras:
        print(f"  {len(extras)} interval supports do NOT have count=q (verify counts):")
        for sup in extras[:10]:
            coeffs = tuple(rng.randrange(1, p) for _ in range(3))
            cnt = count_bad_alpha(sup, coeffs, p, n0, k0, threshold,
                                   L0, L1_arr, all_T, D1, inv_D1)
            print(f"    sup={sup}: count={cnt}")


if __name__ == "__main__":
    main()
