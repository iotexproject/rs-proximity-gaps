"""g3_count_q_combinatorial.py — fast combinatorial prediction of count=q
supports + sample verification.

CONJECTURE: count_α = q ⟺ ∃ cyclic interval I of length k_1 in Z/n_1Z
                          such that f_e_DFT_supp ∪ f_o_DFT_supp ⊂ I.

Mechanism: on subdomain {y ∈ L_1 : y^{lcm related to interval position} = 1},
both f_e and f_o restrict to RS_{k_1} codewords, giving 8+ trivial agreements
for any α.

Verify on sample of predicted YES + NO supports.
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


def count_bad_alpha_fast(positions, coeffs, p, n0, k0, threshold,
                         L0, L1_arr, all_T, D1, inv_D1, early_exit_count=200):
    fhat = [0] * n0
    for ps, c in zip(positions, coeffs):
        fhat[ps] = c
    f = evaluate_dft_local(fhat, L0, p)
    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)
    n1 = len(L1_arr)
    k1 = k0 // 2

    # Batch alphas in chunks of 64
    CHUNK = 64
    cnt = 0
    for alpha_start in range(0, p, CHUNK):
        alphas = np.arange(alpha_start, min(alpha_start + CHUNK, p))
        for alpha in alphas:
            fold = (f_e_arr + alpha * f_o_arr) % p
            extras = batched_extras(all_T, fold, L1_arr, D1, inv_D1, p)
            d1 = n1 - k1 - int(extras.max())
            if d1 <= threshold:
                cnt += 1
                if cnt >= early_exit_count and alpha_start + CHUNK < p:
                    # likely count=q; project: if cnt/seen > 0.5 then count = q
                    seen = alpha_start + (alpha - alpha_start + 1)
                    if cnt > seen * 0.5:
                        return cnt, p  # placeholder for "likely count=q"
    return cnt, cnt


def L1_dft_positions(positions):
    fe, fo = [], []
    for j in positions:
        if j % 2 == 0:
            fe.append(j // 2)
        else:
            fo.append((j - 1) // 2)
    return tuple(sorted(set(fe))), tuple(sorted(set(fo)))


def in_cyclic_interval(positions, n, length):
    pos = sorted(set(positions))
    for start in range(n):
        if all((p - start) % n < length for p in pos):
            return True, start
    return False, None


def main():
    p = 1153
    n0, k0 = 32, 8
    n1, k1 = 16, 4
    threshold = n1 - int(math.isqrt(k1 * n1))

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    all_T = np.array(list(combinations(range(n1), k1)), dtype=np.int64)

    # All 3-pos supports with both even and odd
    all_sups = []
    for sup in combinations(range(8, 32), 3):
        has_e = any(j % 2 == 0 for j in sup)
        has_o = any(j % 2 == 1 for j in sup)
        if has_e and has_o:
            all_sups.append(sup)
    print(f"Total mixed-parity 3-pos supports: {len(all_sups)}\n")

    # Predict count=q via conjecture
    pred_q = []
    pred_not_q = []
    for sup in all_sups:
        fe, fo = L1_dft_positions(sup)
        union = sorted(set(fe + fo))
        ok, _ = in_cyclic_interval(union, n1, k1)
        if ok:
            pred_q.append(sup)
        else:
            pred_not_q.append(sup)
    print(f"Predicted count=q (union DFT in cyclic length-{k1} interval): {len(pred_q)}")
    print(f"Predicted count<q: {len(pred_not_q)}\n")

    rng = random.Random(2026)

    # Verify ALL predicted count=q
    print("=== Verify ALL predicted count=q supports ===")
    fails_yes = []
    for i, sup in enumerate(pred_q):
        coeffs = tuple(rng.randrange(1, p) for _ in range(3))
        cnt, _ = count_bad_alpha_fast(sup, coeffs, p, n0, k0, threshold,
                                        L0, L1_arr, all_T, D1, inv_D1)
        if cnt < 100:
            fails_yes.append((sup, cnt))
        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{len(pred_q)} checked, fails so far: {len(fails_yes)}")
    print(f"  Fails: {len(fails_yes)}/{len(pred_q)} predicted YES are NOT count=q")
    if fails_yes:
        for sup, cnt in fails_yes[:10]:
            print(f"    sup={sup}: count={cnt} (predicted q)")

    # Sample verify predicted count<q (50 random)
    print("\n=== Sample verify predicted count<q (50 random) ===")
    sample_no = rng.sample(pred_not_q, min(50, len(pred_not_q)))
    fails_no = []
    for sup in sample_no:
        coeffs = tuple(rng.randrange(1, p) for _ in range(3))
        cnt, _ = count_bad_alpha_fast(sup, coeffs, p, n0, k0, threshold,
                                        L0, L1_arr, all_T, D1, inv_D1)
        if cnt > 100:
            fails_no.append((sup, cnt))
    print(f"  Fails: {len(fails_no)}/50 predicted NOT count=q ARE count=q")
    if fails_no:
        for sup, cnt in fails_no[:10]:
            print(f"    sup={sup}: count={cnt} (predicted not q)")
            fe, fo = L1_dft_positions(sup)
            print(f"      f_e_supp={fe}, f_o_supp={fo}, union={sorted(set(fe+fo))}")

    # Print conjecture refinement / confirmation
    if not fails_yes and not fails_no:
        print("\n=== CONJECTURE CONFIRMED ===")
        print(f"count = q ⟺ f_e_DFT_supp ∪ f_o_DFT_supp ⊂ length-{k1} cyclic interval mod {n1}")
        print(f"\nNumber of supports satisfying this: {len(pred_q)}")
    else:
        print("\n=== CONJECTURE NEEDS REFINEMENT ===")


if __name__ == "__main__":
    main()
