"""g3_niho_dichotomy_64_16.py — verify Niho dichotomy at (64, 16) deployment scale.

L_2 = ⟨ω^4⟩ of order n_2 = 16, k_2 = 4, w_J(L_2) = 8.
For ω of order n_0 = 64: ω^32 = -1, so z^8 acts as sign character on L_2.

Predicted dichotomy: c·z^{p*} on L_2 has d_2 ≤ w_J=8 iff p* mod 8 ∈ {0, 1, 2, 3}.
i.e. {0,1,2,3} (deg<k_2 codewords, d_2=0) ∪ {8,9,10,11} (Niho boundary, d_2=8?).
And {4,5,6,7,12,13,14,15} (mod 8 ∈ {4,5,6,7}) → never bad.
"""
import sys, os
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter

from fri_2round_attack import setup_chain
from mds_decoder import precompute_diff_inv, batched_extras


def main():
    n0, k0, R = 64, 16, 2
    n2, k2 = 16, 4
    w_J_L2 = 8

    # Primes ≡ 1 mod 64
    primes = [193, 257, 449, 577, 641, 769, 1153, 1217]

    print(f"=== Niho dichotomy at (64, 16) deployment scale ===")
    print(f"  n_2={n2}, k_2={k2}, w_J(L_2)={w_J_L2}\n")

    print(f"{'q':<6}", end='')
    for pstar in range(n2):
        print(f"p*={pstar:<5}", end='')
    print()
    print(f"{'mod 8':<6}", end='')
    for pstar in range(n2):
        print(f"({pstar%8:<5})", end='')
    print()
    print('-'*120)

    for p in primes:
        try:
            chain = setup_chain(p, n0, k0, R=R)
        except ValueError:
            continue
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
            tag = "ALL" if n_bad == p-1 else ("0" if n_bad == 0 else f"{n_bad}/{p-1}")
            row += f"{tag:<7}"
        print(row)

    print(f"\n{'q':<6}", end='')
    for pstar in range(n2):
        print(f"d_2(p*={pstar})", end=' ')
    print()
    p_show = primes[0]
    chain = setup_chain(p_show, n0, k0, R=R)
    L2 = chain[2][0]
    L2_arr = np.array(L2, dtype=np.int64)
    D2, inv_D2 = precompute_diff_inv(L2_arr, p_show)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)
    print(f"{p_show:<6}", end='')
    for pstar in range(n2):
        c = 1
        vec = [(c * pow(int(L2[i]), pstar, p_show)) % p_show for i in range(n2)]
        v_arr = np.array(vec, dtype=np.int64)
        extras = batched_extras(info_sets_n2, v_arr, L2_arr, D2, inv_D2, p_show)
        d2 = n2 - k2 - int(extras.max())
        print(f"d_2={d2:<7}", end=' ')
    print()


if __name__ == "__main__":
    main()
