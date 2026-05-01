"""list_size_random_fold.py — exact list size at w=7 for RANDOM received words.

Compare structured K=2 fold (always L=1) to RANDOM received word in F_q^16.
If random words also give L=1 mostly, the bound is generic.
If random words sometimes give L>1, the K=2 structure GUARANTEES uniqueness.
"""
from __future__ import annotations
import sys, os, random
import numpy as np
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fri_2round_attack import setup_chain
from mds_decoder import precompute_diff_inv, batched_extras


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
    return len(seen)


def main():
    P = 193
    chain = setup_chain(P, 32, 8, R=2)
    L1, k1, _ = chain[1]
    n1 = len(L1)
    print(f"=== List size at agreement ≥ 7 for RANDOM r ∈ F_{P}^{n1}, RS_{k1}(L_1) ===")
    print()

    rng = random.Random(2026)
    list_size_dist = {}
    n_tests = 30
    n_with_dist_9 = 0
    for trial in range(100):
        if n_with_dist_9 >= n_tests: break
        # Random received word
        r = [rng.randrange(P) for _ in range(n1)]
        # First check if min distance is 9 (worth analyzing)
        L1_arr = np.array(L1, dtype=np.int64)
        D1, inv_D1 = precompute_diff_inv(L1_arr, P)
        info_sets = list(combinations(range(n1), k1))
        info_sets_arr = np.array(info_sets, dtype=np.int64)
        r_arr = np.array(r, dtype=np.int64)
        extras = batched_extras(info_sets_arr, r_arr, L1_arr, D1, inv_D1, P)
        max_agree = int(extras.max())
        d = n1 - k1 - max_agree
        if d != 9:  # Want d=9 = agreement 7
            continue
        n_with_dist_9 += 1
        # Compute exact list size
        L_size = exact_list_size(r, L1, k1, P, threshold=7)
        list_size_dist[L_size] = list_size_dist.get(L_size, 0) + 1
        if L_size > 1:
            print(f"  trial {trial}: r={r[:5]}... distance = {d}, list size = {L_size}")

    print()
    print(f"Tested {n_with_dist_9} random r with min distance = 9 to RS_4(L_1)")
    print(f"List size distribution: {list_size_dist}")
    if max(list_size_dist) > 1:
        print(f"\nRandom inputs CAN have list size > 1 at agreement 7.")
        print(f"K=2 structured inputs giving list = 1 is therefore a STRUCTURAL property.")
    else:
        print(f"\nList size = 1 even for random inputs. Bound is generic at agreement 7.")


if __name__ == "__main__":
    main()
