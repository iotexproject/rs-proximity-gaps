"""g3_niho_dichotomy_q_universal.py — verify the Niho dichotomy
{p* mod 4 ∈ {0, 1}: bad; p* mod 4 ∈ {2, 3}: never bad}
holds for all q ≡ 1 mod 32 in {97, 193, 449, 577, 641, 673, 769, 1153}.
"""
import sys, os
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter

from fri_2round_attack import setup_chain
from mds_decoder import precompute_diff_inv, batched_extras


def main():
    n0, k0, R = 32, 8, 2
    n2, k2 = 8, 2
    w_J_L2 = 4
    primes = [97, 193, 449, 577, 641, 673, 769, 1153]

    print(f"=== Niho dichotomy verification across q ≡ 1 mod {n0} ===\n")
    print(f"{'q':<6}", end='')
    for pstar in range(n2):
        print(f"p*={pstar:<6}", end='')
    print()
    print(f"{'mod4':<6}", end='')
    for pstar in range(n2):
        print(f"({pstar%4:<6})", end='')
    print()
    print('-'*60)

    for p in primes:
        chain = setup_chain(p, n0, k0, R=R)
        L2 = chain[2][0]
        L2_arr = np.array(L2, dtype=np.int64)
        D2, inv_D2 = precompute_diff_inv(L2_arr, p)
        info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)

        row = f"{p:<6}"
        for pstar in range(n2):
            n_bad = 0
            for c in range(1, p):
                vec = [(c * pow(int(L2[i]), pstar, p)) % p for i in range(n2)]
                v_arr = np.array(vec, dtype=np.int64)
                extras = batched_extras(info_sets_n2, v_arr, L2_arr, D2, inv_D2, p)
                d2 = n2 - k2 - int(extras.max())
                if d2 <= w_J_L2: n_bad += 1
            ratio = n_bad / (p - 1)
            tag = "ALL" if n_bad == p-1 else ("0" if n_bad == 0 else f"{n_bad}/{p-1}")
            row += f"{tag:<8}"
        print(row)

    print(f"\nDichotomy: bad iff p* mod 4 ∈ {{0, 1}} (universal across q)?")


if __name__ == "__main__":
    main()
